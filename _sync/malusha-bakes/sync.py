# Pulls the wall of the VK group club242334404 and rebuilds malusha-bakes/index.html:
# menu prices and photos, new menu items, the «Уже уехали в подарок» sets.
# Runs in GitHub Actions (.github/workflows/malusha-bakes-sync.yml) with VK_TOKEN = a service token (wall.get).
# Offline: python3 sync.py --offline  (data/wall.json, photos from the local originals folder)
import datetime, hashlib, io, json, os, re, sys, urllib.parse, urllib.request
from zoneinfo import ZoneInfo
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import menu  # noqa: E402

GID = 242334404
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SITE = os.path.join(ROOT, 'malusha-bakes')
IMG = os.path.join(SITE, 'img')
DATA = os.path.join(HERE, 'data')
MAN = os.path.join(DATA, 'manifest.json')
OFFLINE = '--offline' in sys.argv
FORCE = '--force' in sys.argv
ORIG = os.environ.get('MALUSHA_ORIG', '/home/leonti/portfolio/malusha-originals')
MSK = ZoneInfo('Europe/Moscow')
MON = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
UA = {'User-Agent': 'Mozilla/5.0 (malusha-bakes site sync)'}
SNAPSHOT = datetime.datetime(2026, 11, 12, 12, 0, tzinfo=MSK).timestamp()  # posts after this are «new»

# hand-made crops from the first mockup: key -> (photo for cards and the lightbox, close-up for circles)
CURATED = {
    'photo456239019': ('m-mini-banan.jpg', None), 'photo456239020': ('m-mini-malina.jpg', None),
    'photo456239021': ('m-snikers-boks.jpg', 'f-snikers.jpg'), 'photo456239022': ('p-kraft.jpg', None),
    'photo456239023': ('p-lenta.jpg', 'f-krasnyi-barhat.jpg'), 'photo456239024': ('m-medovik.jpg', None),
    'photo456239025': ('m-chizkeik.jpg', None), 'photo456239026': ('m-trifl-boks.jpg', 'f-banan-karamel.jpg'),
    'photo456239027': ('c-luna-trifly.jpg', None), 'photo456239028': ('c-luna.jpg', 'm-bento-serdtsa.jpg'),
    'photo456239029': ('c-luna-stakan.jpg', None), 'photo456239032': ('c-lev.jpg', None),
    'photo456239035': ('m-trifly-6.jpg', 'f-klubnika-banan.jpg'), 'photo456239036': ('m-trifly-ruka.jpg', None),
    'video456239017': ('c-spasibo.jpg', 'f-klubnika-slivki.jpg'), 'video456239024': ('c-zaika.jpg', None),
    'video456239026': ('c-papa.jpg', None), 'video456239023': ('m-korpusnye.jpg', None),
}
# local originals for --offline (photos the first mockup did not crop)
LOCAL = {'photo456239033': 'p18_2_photo.jpg', 'video456239020': 'p19_2_video_ff.jpg'}
# captions of the sets in the first mockup: post id -> (tag on the photo, title, text)
CAPTIONS = {
    15: ('До Луны и обратно', 'Подарок ко Дню отца', 'Бенто вишня-шоколад с сердечками и трайфлы с пряниками «Любим тебя до Луны и обратно»'),
    18: ('Львиный набор', 'Любимому папе', 'Бенто клубника-сливки с картинкой «Мы тебя любим» и трайфлы с топперами'),
    26: ('Мужу и папе', 'Чизкейк на шоколадном сабле', 'С орео, голубикой и топпером «Любимому мужу и папе»'),
    25: ('Нежный сникерс', 'Тортик с зайкой', 'Розовые ленты, жемчужины и фигурка зайки'),
    17: ('Спасибо, что ты есть', 'Трайфлы с пожеланиями', 'Клубника-сливки и топперы «Спасибо, что ты у нас есть»'),
}
FEATURED = 15        # the big card until a newer set with several photos appears
GIFT_COVER = {15: 'photo456239028'}  # main photo of a set when it isn't the first one in the post
GIFT_ORDER = [15, 18, 26, 25, 17]  # order of the first mockup, newer posts go first
BENTO_FLAVOURS = ['вишня-шоколад', 'клубника-сливки']


class VKError(Exception):
    pass


def api(method, **params):
    token = os.environ.get('VK_TOKEN', '')
    if not token:
        sys.exit('VK_TOKEN is not set')
    params.update(access_token=token, v='5.199')
    req = urllib.request.Request('https://api.vk.com/method/' + method, data=urllib.parse.urlencode(params).encode(), headers=UA)
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if 'error' in data:  # never print the request: it contains the token
        e = data['error']; raise VKError(f"VK {method} error {e.get('error_code')}: {e.get('error_msg')}")
    return data


def fetch(url):
    err = None
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e:  # noqa: BLE001
            err = e
    raise err


def dstr(ts):
    d = datetime.datetime.fromtimestamp(ts, MSK); return f'{d.day} {MON[d.month - 1]}'


def source_url(kind, obj):
    if kind == 'photo':
        s = max((s for s in obj.get('sizes', []) if s.get('url')), key=lambda s: s.get('width', 0) * s.get('height', 0), default=None)
        return s and s['url']
    imgs = [i for i in obj.get('first_frame', []) + obj.get('image', []) if i.get('url')]
    tall = [i for i in imgs if i.get('height', 0) > i.get('width', 0) and i.get('width', 0) >= 400]
    pick = max(tall or imgs, key=lambda i: i.get('width', 0), default=None)
    return pick and pick['url']


def make_images(key, kind, obj, man):
    """card + square files for one VK photo or clip frame; returns (card, close-up) paths relative to the site"""
    if key in CURATED:
        c, s = CURATED[key]
        return 'img/' + c, 'img/' + (s or c)
    card, sq = f'img/vk/{key}.jpg', f'img/vk/{key}-s.jpg'
    if key in man['img'] and os.path.exists(os.path.join(SITE, card)):
        return card, sq
    raw = None
    if key in LOCAL and os.path.exists(os.path.join(ORIG, LOCAL[key])):
        raw = open(os.path.join(ORIG, LOCAL[key]), 'rb').read()
    elif not OFFLINE:
        url = source_url(kind, obj)
        raw = url and fetch(url)
    if not raw:
        return None, None
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB')
    os.makedirs(os.path.join(IMG, 'vk'), exist_ok=True)
    big = im.copy(); big.thumbnail((1100, 1100), Image.LANCZOS)
    big.save(os.path.join(SITE, card), 'JPEG', quality=80, optimize=True, progressive=True)
    w, h = im.size; a = min(w, h)
    left, top = (w - a) // 2, max(0, int((h - a) * .45))
    s = im.crop((left, top, left + a, top + a)); s.thumbnail((560, 560), Image.LANCZOS)
    s.save(os.path.join(SITE, sq), 'JPEG', quality=80, optimize=True, progressive=True)
    man['img'][key] = [card, sq]
    print('image', key, im.size)
    return card, sq


def tidy_lines(post):
    return menu.clean(menu.text_of(post))


def main():
    wall_file = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--wall=')), None)  # test: posts from a file, photos downloaded
    if OFFLINE or wall_file:
        wall = json.load(open(wall_file or os.path.join(DATA, 'wall.json'), encoding='utf-8'))
    else:
        wall = api('wall.get', owner_id=-GID, count=100)
    posts = wall['response']['items']
    man = json.load(open(MAN)) if os.path.exists(MAN) else {}
    man.setdefault('img', {})
    media = {k: (kind, obj) for p in posts for k, kind, obj in menu.media(p)}

    def pics(keys):
        out = []
        for k in keys:
            kind, obj = media[k]
            c, s = make_images(k, kind, obj, man)
            if c:
                out.append((k, c, s))
        return out

    items = []
    for it in menu.build(posts):
        ph = pics([x['key'] for x in it['photos']])
        if ph and ph[0][0] in CURATED:  # a hand-made close-up beats the plain photo
            close = next((s for k, c, s in ph if k in CURATED and CURATED[k][1]), ph[0][2])
        else:
            close = ph[0][2] if ph else None
        items.append({
            'id': it['id'], 'cat': it['cat'], 'kind': it.get('kind'), 'name': it['name'],
            'price': it.get('price'), 'frm': bool(it.get('frm')), 'unit': it.get('unit') or '',
            'desc': it.get('desc') or '', 'sq': close, 'gal': [c for k, c, s in ph][:8],
            'post': it.get('post'), 'icon': it.get('icon'),
            'new': bool(it.get('new') and it.get('date') and it['date'] > SNAPSHOT),
        })

    # sets that went to someone as a present: curated ones in the old order, newer posts first
    gifts = []
    gift_posts = [p for p in posts if menu.is_gift(p) or p['id'] in CAPTIONS]
    gift_posts.sort(key=lambda p: (p['date'] <= SNAPSHOT, GIFT_ORDER.index(p['id']) if p['id'] in GIFT_ORDER else 99, -p['date']))
    for p in gift_posts[:9]:
        ph = pics([k for k, _, _ in menu.media(p)])
        if not ph:
            continue
        ph.sort(key=lambda x: x[0] != GIFT_COVER.get(p['id']))
        if p['id'] in CAPTIONS:
            tag, title, text = CAPTIONS[p['id']]
        else:
            lines = tidy_lines(p)
            title = lines[0] if lines else 'Из группы VK'
            if len(title) > 70: title = title[:70].rsplit(' ', 1)[0] + '…'
            text = ' '.join(lines[1:])
            if len(text) > 150: text = text[:150].rsplit(' ', 1)[0] + '…'
            tag = dstr(p['date'])
        gifts.append({'post': p['id'], 'tag': tag, 'title': title, 'text': text, 'imgs': [c for k, c, s in ph][:3], 'date': p['date']})
    newer = [g for g in gifts if g['date'] > SNAPSHOT and len(g['imgs']) > 1]
    big = newer[0]['post'] if newer else FEATURED
    gifts.sort(key=lambda g: g['post'] != big)
    for g in gifts:
        del g['date']

    bento = next((i for i in items if i['id'] == 'bento'), None)
    data = {'cats': menu.CATS, 'items': items, 'gifts': gifts,
            'bento': {'price': bento and bento['price'], 'frm': bento['frm'] if bento else True, 'flav': BENTO_FLAVOURS}}
    h = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if h == man.get('hash') and not FORCE and os.path.exists(os.path.join(SITE, 'index.html')):
        json.dump(man, open(MAN, 'w'), ensure_ascii=False, indent=0)
        print('no changes'); return
    now = datetime.datetime.now(MSK)
    data['upd'] = f'{now.day} {MON[now.month - 1]}'
    price = {i['id']: i['price'] for i in items}
    cup = min((i['price'] for i in items if i['kind'] == 'cup' and i['price']), default=None)
    bits = [f'трайфлы {cup} ₽' if cup else '', f'мини-чизкейки {price["mini"]} ₽' if price.get('mini') else '',
            f'бенто-торты от {price["bento"]} ₽' if price.get('bento') else '']
    meta = 'Домашняя кондитерская в Колпино: ' + ', '.join(b for b in bits if b) + '. Соберите коробочку десертов в подарок и оставьте заявку.'
    tpl = open(os.path.join(HERE, 'index.src.html'), encoding='utf-8').read()
    page = tpl.replace('/*__DATA__*/{}', json.dumps(data, ensure_ascii=False, separators=(',', ':'))).replace('__META_DESC__', meta)
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(page)
    man['hash'] = h
    if not OFFLINE and not wall_file:
        json.dump(wall, open(os.path.join(DATA, 'wall.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(man, open(MAN, 'w'), ensure_ascii=False, indent=0)
    print('rebuilt:', len(items), 'items,', len(gifts), 'sets, updated', data['upd'])


if __name__ == '__main__':
    main()
