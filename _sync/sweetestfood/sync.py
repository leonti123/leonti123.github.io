# Pulls SweetestFood's VK market, wall and clips and rebuilds sweetestfood/index.html.
# Runs in GitHub Actions (see .github/workflows/sweetestfood-sync.yml).
#   VK_TOKEN  service token (wall, clips). market.get needs a user token, so the menu comes from
#             data/market.json, which the VK mini app button (sweetestfood-vk/) saves through Apps Script
# Offline test: python3 sync.py --offline  (uses data/*.json, no network for the API)
import datetime, hashlib, io, json, os, re, sys, urllib.parse, urllib.request
from zoneinfo import ZoneInfo
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import catalog  # noqa: E402

GID = 241272766
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SITE = os.path.join(ROOT, 'sweetestfood')
IMG = os.path.join(SITE, 'img')
DATA = os.path.join(HERE, 'data')
MAN = os.path.join(DATA, 'manifest.json')
OFFLINE = '--offline' in sys.argv
FORCE = '--force' in sys.argv
COVER = {13355103: 4, 13359805: 2, 13359809: 2, 13359810: 2, 13422945: 2, 13489739: 2, 13489863: 2, 13387055: 2}
CLIPS_PINNED = [456239017, 456239081, 456239031, 456239022, 456239047, 456239087, 456239095, 456239121, 456239071, 456239026]
NEW_AFTER = datetime.datetime(2026, 11, 9, 23, 0, tzinfo=ZoneInfo('Europe/Moscow')).timestamp()  # clips after the first snapshot
MON = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
UA = {'User-Agent': 'Mozilla/5.0 (sweetestfood site sync)'}


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
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e:  # noqa: BLE001
            err = e
    raise err


def save_img(raw, name, mx, q):
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB')
    im.thumbnail((mx, mx), Image.LANCZOS)
    im.save(os.path.join(IMG, name + '.jpg'), 'JPEG', quality=q, optimize=True, progressive=True)


def biggest(sizes):
    return max((s for s in sizes if s.get('url')), key=lambda s: s.get('width', 0) * s.get('height', 0))['url']


def load(name):
    return json.load(open(os.path.join(DATA, name), encoding='utf-8'))


def dump(name, obj):
    json.dump(obj, open(os.path.join(DATA, name), 'w', encoding='utf-8'), ensure_ascii=False)


def tidy(t):
    t = re.sub(r'\[#alias\|[^\]]*\]', '', t)
    t = re.sub(r'#\S+', '', t)
    t = re.sub('[\U0001F000-\U0001FAFF☀-➿️‍⠀]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def dstr(ts):
    d = datetime.datetime.fromtimestamp(ts, ZoneInfo('Europe/Moscow')); return f'{d.day} {MON[d.month - 1]}'


def main():
    market_live = False
    if OFFLINE:
        market, wall, group = load('market.json'), load('wall.json'), load('group.json')
    else:
        try:
            market = api('market.get', owner_id=-GID, count=200, extended=1)
            market_live = True
        except VKError as e:  # a service token can't read the market: keep the last saved menu
            print(e, '-> menu kept from data/market.json'); market = load('market.json'); market_live = False
        wall = api('wall.get', owner_id=-GID, count=100)
        group = api('groups.getById', group_ids=GID, fields='counters')
    items = market['response']['items']
    posts_raw = wall['response']['items']
    g = group['response']; g = g['groups'][0] if isinstance(g, dict) and 'groups' in g else g[0]
    man = json.load(open(MAN)) if os.path.exists(MAN) else {}
    photos_man = man.get('photos', {})

    # product photos: regenerate only when the item's photo list changed
    for it in items:
        pid = str(it['id']); ph = it.get('photos', [])[:4]
        ids = [p['id'] for p in ph]
        if not ph or (photos_man.get(pid) == ids and os.path.exists(os.path.join(IMG, f't-{pid}.jpg'))):
            continue
        ci = COVER.get(it['id'], 1) if photos_man.get(pid) is None else 1
        ci = ci if ci <= len(ph) else 1
        order = [ci] + [k for k in range(1, len(ph) + 1) if k != ci]
        raws = {k: fetch(biggest(ph[k - 1]['sizes'])) for k in order}
        save_img(raws[ci], f't-{pid}', 640, 74)
        for n, k in enumerate(order, 1):
            save_img(raws[k], f'p-{pid}-{n}', 1000, 76)
        photos_man[pid] = ids
        print('photos updated for', pid, it['title'][:40])

    cat = catalog.build(items)
    for c in cat['items']:  # the page needs the photo count
        c['np'] = len(photos_man.get(str(c['id']), [])) or c['np']

    # posts: newest 3 with a photo and text (the poll poster is used elsewhere)
    posts = []
    for p in posts_raw:
        ph = [a['photo'] for a in p.get('attachments', []) if a['type'] == 'photo']
        if not ph or not p.get('text', '').strip() or p['id'] == 45:
            continue
        name = f"post-{ph[0]['id']}"
        if not os.path.exists(os.path.join(IMG, name + '.jpg')):
            save_img(fetch(biggest(ph[0]['sizes'])), name, 640, 76)
        t = tidy(p['text'])
        if len(t) > 190: t = t[:190].rsplit(' ', 1)[0] + '…'
        posts.append({'id': p['id'], 'date': dstr(p['date']), 'text': t, 'img': name})
        if len(posts) == 3: break

    # clips: new ones (after the curated set) go first, then the curated ones, 10 in total
    seed = {c['id']: c for c in load('clips_seed.json')}
    clips = {}
    for p in posts_raw:
        for a in p.get('attachments', []):
            if a['type'] == 'clip':
                c = a['clip']; clips[c['id']] = c
    fresh = sorted((c for c in clips.values() if c['date'] > NEW_AFTER), key=lambda c: -c['date'])
    chosen = [c['id'] for c in fresh] + [i for i in CLIPS_PINNED if i in clips or i in seed]
    cl = []
    for cid in chosen[:10]:
        c = clips.get(cid) or {}
        s = seed.get(cid, {})
        name = f'clip-{cid}'
        if not os.path.exists(os.path.join(IMG, name + '.jpg')) and c:
            big = [i for i in c.get('image', []) if i.get('width', 0) >= 600 and i.get('height', 0) > i.get('width', 0)]
            src = big or [i for i in c.get('first_frame', []) if i.get('width', 0) >= 600] or c.get('image', [])
            save_img(fetch(max(src, key=lambda i: i.get('width', 0))['url']), name, 640, 72)
        desc = c.get('description', s.get('desc', ''))
        lines = [tidy(x) for x in desc.split('\n')]; lines = [x for x in lines if x]
        cap = lines[0] if lines else ''
        if len(cap) > 80: cap = cap[:80].rsplit(' ', 1)[0] + '…'
        cl.append({'id': cid, 'cap': cap, 'views': c.get('views', s.get('views', 0)), 'dur': c.get('duration', s.get('dur', 0))})

    cnt = g.get('counters') if isinstance(g.get('counters'), dict) else {}
    if cnt.get('clips'):
        man['stats'] = {'clips': cnt['clips'], 'views': cnt.get('clips_views', 0)}
    cnt = cnt if cnt.get('clips') else {'clips': man.get('stats', {}).get('clips', 27), 'clips_views': man.get('stats', {}).get('views', 8632)}
    data = {'cats': cat['cats'], 'items': cat['items'], 'posts': posts, 'clips': cl,
            'stats': {'clips': cnt.get('clips', len(clips)), 'views': cnt.get('clips_views', 0)}}
    # view counters change all the time: leave them out of the hash so they don't cause a commit every run
    stable = dict(data, stats=None, clips=[dict(c, views=0) for c in cl])
    h = hashlib.sha256(json.dumps(stable, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    man['photos'] = photos_man
    if h == man.get('hash') and not FORCE:
        json.dump(man, open(MAN, 'w'), ensure_ascii=False)
        print('no changes'); return
    now = datetime.datetime.now(ZoneInfo('Europe/Moscow'))
    data['updated'] = f'{now.day} {MON[now.month - 1]} {now.year}'
    tpl = open(os.path.join(HERE, 'index.src.html'), encoding='utf-8').read()
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':'))))
    man['hash'] = h
    if market_live:
        dump('market.json', market)
    json.dump(man, open(MAN, 'w'), ensure_ascii=False)
    print('rebuilt:', len(cat['items']), 'items,', len(posts), 'posts,', len(cl), 'clips')


if __name__ == '__main__':
    main()
