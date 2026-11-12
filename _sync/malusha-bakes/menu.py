# Turns the posts of the VK group «Бенто торты, трайфлы, корпусные, моти Колпино» (club242334404)
# into the site menu. Base items below keep categories, descriptions and photo choices; every post
# with a price («Трайфлы клубника банан ... 350р-1шт») updates that item, a priced post about
# something new becomes a new menu item, and photos of single-item posts go to that item.
import re

CATS = [
    ('tr', 'Трайфлы'),
    ('ch', 'Чизкейки'),
    ('ck', 'Тортики'),
    ('more', 'Ещё вкусное'),
]

# kind 'cup' = a trifle flavour: goes to the box builder and the first screen
BASE = [
    dict(id='rv', cat='tr', kind='cup', name='Красный бархат', price=350, unit='шт',
         desc='Праздничный, с жемчужной посыпкой', pat=r'красн\w*\s+бархат'),
    dict(id='sn', cat='tr', kind='cup', name='Сникерс', price=350, unit='шт',
         desc='Мягкая карамель с жареным солёным арахисом', pat=r'сникерс'),
    dict(id='ks', cat='tr', kind='cup', name='Клубника-сливки', price=350, unit='шт',
         desc='Нежный сливочный крем и клубника', pat=r'клубник\w*\s+(?:и\s+)?сливк|сливк\w*\s+(?:и\s+)?клубник'),
    dict(id='kb', cat='tr', kind='cup', name='Клубника-банан', price=350, unit='шт',
         desc='Для любителей нежной и воздушной текстуры', pat=r'клубник\w*\s+(?:и\s+)?банан|банан\w*\s+(?:и\s+)?клубник'),
    dict(id='trbox', cat='tr', name='Трайфл-бокс', price=750, unit='шт',
         desc='Порция побольше в круглом боксе: банан-карамель или банан-клубника', pat=r'трайфл\w*\s*бокс|бокс\w*\s+трайфл'),
    dict(id='mini', cat='ch', name='Мини-чизкейк', price=450, unit='шт',
         desc='Банан-карамель или малина-кокос', pat=r'мини\s*чизкейк'),
    dict(id='cheese', cat='ch', name='Классический чизкейк', price=None,
         desc='На шоколадном сабле. Можно украсить ягодами и надписью', pat=r'чизкейк'),
    dict(id='bento', cat='ck', name='Бенто-торт', price=950, frm=True,
         desc='Цена зависит от веса. Вишня-шоколад или клубника-сливки, надпись или картинка', pat=r'бенто'),
    dict(id='maxi', cat='ck', name='Тортик «макс»', price=None,
         desc='Домашний торт побольше, например нежный «Сникерс» с зайкой', pat=r'\bмакс\b|тортик\w*\s+побольше'),
    dict(id='medovik', cat='ck', name='Домашний медовик', price=None,
         desc='С нежнейшим заварным кремом', pat=r'медовик'),
    dict(id='korpus', cat='more', name='Корпусные десерты', price=None,
         desc='Например, манго. Иногда бывают в наличии', pat=r'корпусн'),
    dict(id='cinna', cat='more', name='Синнабоны', price=None, icon='roll',
         desc='Корица, сливочный, пекан, тирамису', pat=r'синнабон'),
    dict(id='pops', cat='more', name='Кейкпопсы', price=None, icon='pop',
         desc='Пирожные на палочке', pat=r'кейк\s*попс'),
    dict(id='moti', cat='more', name='Моти', price=None, icon='moti',
         desc='Нежный вкус', pat=r'\bмоти\b'),
]
# mini cheesecakes and bento also match the plain words, so they are checked first
ORDER = ['trbox', 'mini', 'rv', 'sn', 'ks', 'kb', 'cheese', 'bento', 'maxi', 'medovik', 'korpus', 'cinna', 'pops', 'moti']
BOX_FIRST = re.compile(r'трайфл\w*\s*бокс|бокс\w*\s+трайфл')

# photos whose post text doesn't say what is on them (gift posts, a clip without text)
ASSIGN = {'photo456239028': 'bento', 'photo456239033': 'bento', 'video456239024': 'maxi'}
# preferred first photo of an item while that photo is in the group
PREFER = {'mini': 'photo456239020', 'kb': 'photo456239036', 'bento': 'photo456239028'}
GIFT = re.compile(r'подар|отправил|поздравл|праздник|день рожд|юбиле|свадьб|любим|сюрприз', re.I)
SKIP_POST = re.compile(r'инстаграм|instagram', re.I)
BOILER = re.compile(r'^(заказ\w*\s+к\s+любому\s+праздник\w*|заказы?\s+принима\w*.*|оставляю\s+ссылку.*)$', re.I)
GIFTY = re.compile(r'подар|отправил|поздравля|праздник|спасибо|отзыв|наличи|дегустац', re.I)
NUM = r'(\d{1,3}(?:[  ]\d{3})+|\d{2,6})'
PRICE = re.compile(r'(?:\b(от)\s*)?' + NUM + r'\s*(?:р\b\.?|р(?=[-–\s/]|$)|руб\w*\.?|₽)\s*(?:[-–/]|за)?\s*(?:(\d{1,2})\s*)?(шт|кг|г\b|порц\w*|стакан\w*)?', re.I)
PACK = re.compile(r'(\d{1,2})\s*(?:шт\w*|штук\w*)', re.I)
EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-➿️‍⭐⬆↔-⇿⤴⤵〰〽㊗㊙]')


def clean(t):
    t = re.sub(r'\[(?:#alias|club\d+|id\d+|public\d+)\|([^\]|]*)(?:\|[^\]]*)?\]', r'\1', t or '')
    t = re.sub(r'#\S+', '', t)
    t = EMOJI.sub('', t)
    lines = [re.sub(r'[ \t ]+', ' ', x).strip(' .,;:!-–—') for x in t.split('\n')]
    return [x for x in lines if x and not BOILER.match(x)]


def norm(s):
    s = s.lower().replace('ё', 'е')
    s = re.sub(r'[/\\\-–—+&,«»"()]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def match(text):
    """ids of base items named in the text; a trifle with no known flavour gives 'tr?'"""
    n = norm(text); found = []
    if BOX_FIRST.search(n):
        found.append('trbox'); n = BOX_FIRST.sub(' ', n)
    by = {b['id']: b for b in BASE}
    for i in ORDER:
        if i == 'trbox' or i in found:
            continue
        if i == 'cheese' and 'mini' in found and len(re.findall('чизкейк', n)) < 2:
            continue
        if re.search(by[i]['pat'], n):
            found.append(i)
    if 'трайфл' in n and not any(by[i].get('kind') == 'cup' for i in found) and 'trbox' not in found:
        found.append('tr?')
    return found


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def offers(lines):
    """(name, desc, price, from, unit) for every price in the post"""
    out = []; start = 0
    for k, ln in enumerate(lines):
        m = PRICE.search(ln)
        if not m:
            continue
        price = int(re.sub(r'\D', '', m.group(2)))
        if price < 50:
            continue
        frm = bool(m.group(1)); unit = (m.group(4) or '').lower(); cnt = int(m.group(3) or 1)
        unit = 'кг' if unit == 'кг' else 'шт' if unit.startswith(('шт', 'стакан', 'порц')) else ''
        before = ln[:m.start()].strip(' -–—:,'); after = ln[m.end():].strip(' -–—:,.')
        pk = PACK.search(before)
        if pk and int(pk.group(1)) > 1:  # «Синнабоны 4шт - 600р»
            cnt, unit = int(pk.group(1)), 'шт'; before = (before[:pk.start()] + before[pk.end():]).strip(' -–—:,')
        if unit == 'шт' and cnt > 1:
            unit = '%d шт' % cnt
        block = [x for x in range(start, k) if not PRICE.search(lines[x]) and not GIFTY.search(lines[x])]
        start = k + 1
        src = 'after'
        if re.search(r'[а-яa-z]{3}', before, re.I):
            name, desc = before, cap(after)
        else:
            # the name is the topmost line above the price (after the previous price) that names a dessert
            named = [x for x in block if match(lines[x])]
            j = named[0] if named else (block[0] if block else None)
            if j is None:
                continue
            name = lines[j]
            own = ' '.join(lines[x] for x in block if x > j)
            desc, src = (own, 'lines') if own else (cap(after), 'after')
        par = re.search(r'\(([^)]{6,})\)', name)
        if par and src != 'lines':
            desc, src = cap(par.group(1)), 'lines'
        desc = re.sub(r'(?<=[а-яё])/(?=[а-яё])', '-', desc, flags=re.I)
        out.append(dict(name=name, desc=desc, src=src, price=price, frm=frm, unit=unit))
    return out


def media(post):
    """photos first, then clip/video frames: [(key, kind, obj)]"""
    res = []
    for a in post.get('attachments', []):
        t = a.get('type')
        if t == 'photo':
            res.append(('photo%d' % a['photo']['id'], 'photo', a['photo']))
        elif t in ('clip', 'video'):  # clips are videos: the same id whatever type the API reports
            res.append(('video%d' % a[t]['id'], t, a[t]))
    return res


def text_of(post):
    t = post.get('text') or ''
    if not t.strip():
        for a in post.get('attachments', []):
            if a.get('type') in ('clip', 'video'):
                d = a[a['type']].get('description') or ''
                if d and not d.startswith(('Клип сообщества', 'Видео от')):
                    return d
    return t


def new_name(off, cat):
    n = re.sub(r'^\s*трайфл\w*\s*(в\s+стаканчик\w*\s*)?', '', off['name'], flags=re.I) if cat == 'tr' else off['name']
    n = re.sub(r'\s*\(.*?\)\s*', ' ', n).strip(' -–,')
    n = re.sub(r'\s*/\s*', '-', n)
    return cap(n)


TR = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','c','ch','sh','sch','','y','','e','yu','ya']))


def slug(s):
    s = ''.join(TR.get(c, c) for c in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:28] or 'item'


def guess_cat(name):
    n = norm(name)
    if 'трайфл' in n: return 'tr'
    if 'чизкейк' in n: return 'ch'
    if re.search(r'бенто|торт|медовик|наполеон', n): return 'ck'
    return 'more'


def build(posts):
    items = {b['id']: dict(b, photos=[], post=None, date=None) for b in BASE}
    extra = {}
    for p in sorted(posts, key=lambda p: p['date']):  # older first, newer posts win
        if p.get('is_pinned') and p.get('marked_as_ads'):
            continue
        raw = text_of(p)
        if SKIP_POST.search(raw):
            continue
        lines = clean(raw)
        med = media(p)
        offs = offers(lines)
        touched = set()
        for o in offs:
            found = match(o['name'])
            ids = [i for i in found if i != 'tr?']
            if len(found) == 1 and ids:
                it = items[ids[0]]
                it.update(price=o['price'], frm=o['frm'], unit=o['unit'] or it.get('unit'), post=p['id'], date=p['date'])
                if o['src'] == 'lines' and len(o['desc']) > 8:
                    d = o['desc']
                    it['desc'] = cap(d)
                touched.add(ids[0])
            elif len(found) > 1:
                touched.update(found)  # a set or a gift with several desserts: no price, no photos
            else:
                cat = guess_cat(o['name'])
                nm = new_name(o, cat)
                if len(nm) < 3 or re.fullmatch(r'(?i)трайфл\w*', nm) or (cat == 'tr' and re.match(r'(?i)(к|для)\s', nm)):
                    continue
                key = 'n-' + slug(nm)
                d = o['desc']
                extra[key] = dict(id=key, cat=cat, kind='cup' if cat == 'tr' and o['unit'] == 'шт' and o['price'] <= 600 else None,
                                  name=nm, price=o['price'], frm=o['frm'], unit=o['unit'], desc=cap(d),
                                  photos=[], post=p['id'], date=p['date'], new=True)
                touched.add(key)
        if not offs and lines:
            found = match(' '.join(lines[:2]))
            if len(found) == 1 and found[0] != 'tr?':
                touched.add(found[0])
        # photos go to an item only when the post is about that one item
        for n, (key, kind, obj) in enumerate(med):
            target = ASSIGN.get(key)
            if not target and len(touched) == 1:
                target = next(iter(touched))
            if not target:
                continue
            it = items.get(target) or extra.get(target)
            if it is not None:
                it['photos'].append(dict(key=key, kind=kind, post=p['id'], date=p['date'], i=n))
    out = []
    for it in list(items.values()) + list(extra.values()):
        ph = it['photos']
        # real photos before video frames, newest post first, keep the post's own photo order
        ph.sort(key=lambda x: (x['kind'] != 'photo', -x['date'], x['i']))
        seen = []
        for x in ph:
            if x['key'] not in [s['key'] for s in seen]:
                seen.append(x)
        pref = PREFER.get(it['id'])
        if pref and any(s['key'] == pref for s in seen):
            seen.sort(key=lambda s: s['key'] != pref)
        it['photos'] = seen
        out.append(it)
    return out



def is_gift(post):
    """a post about a set or a present (not a single menu item), with photos or a clip"""
    if not media(post) or SKIP_POST.search(text_of(post)):
        return False
    lines = clean(text_of(post))
    if not lines:
        return True  # a clip or photo without words
    single = [o for o in offers(lines) if len(match(o['name'])) == 1]
    return bool(GIFT.search(' '.join(lines))) or not (single or match(' '.join(lines[:2])))
