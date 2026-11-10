# Builds the site catalog from a VK market.get response (extended=1).
# The same parser is meant to run in the scheduled sync after launch:
# market.json (VK API) -> cat.json (site data). Images are handled by imgs.py.
import json, re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'data/market.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data/cat.json'

CATS = [  # key, title, keyword test on the lowercased title
    ('pelmeni', 'Пельмени', lambda t: 'пельмен' in t),
    ('vareniki', 'Вареники', lambda t: 'вареник' in t),
    ('veg', 'Без мяса', lambda t: 'нут' in t or 'фалафель' in t or 'овощные' in t),
    ('kotlety', 'Котлеты и тефтели', lambda t: 'котлет' in t or 'тефтел' in t or 'фрикадел' in t),
    ('golubtsy', 'Голубцы', lambda t: 'голубц' in t),
    ('bliny', 'Блинчики', lambda t: 'блин' in t),
    ('syrniki', 'Сырники', lambda t: 'сырник' in t),
]
ORDER = ['pelmeni', 'vareniki', 'kotlety', 'golubtsy', 'bliny', 'syrniki', 'veg', 'other']
FIX = [('жаренным луком', 'жареным луком'), ('Варëная', 'Варёная'), ('сгущëнка', 'сгущёнка'), ('без соли, консервантов', 'без сои, консервантов'),
       ('сковородена', 'сковороде'), ('переодически', 'периодически'), ('паровачные', 'панировочные'), ('яйчный', 'яичный'),
       ('куринного', 'куриного'), ('востановленный', 'восстановленный'), ('специ.', 'специй.'), ('соль севанская', 'соль сванская')]
EMO = re.compile('[\U0001F000-\U0001FAFF☀-➿️‍⠀⭐⬆↔-↪⃣]')


def fix(s):
    for a, b in FIX:
        s = s.replace(a, b)
    return s


def quotes(s):
    return re.sub(r'"([^"]+)"', r'«\1»', s)


def clean(s):
    return re.sub(r'\s+', ' ', EMO.sub('', s)).strip(' •-—– ')


def parse(it):
    title = fix(it['title'].strip())
    low = title.lower()
    cat = next((k for k, _, f in CATS if f(low)), 'other')
    unit = 'pc' if re.search(r'1\s*шт', low) else 'kg'
    desc = fix(it.get('description', ''))
    m = re.search(r'упаковк[аи]\s*[-–—]?\s*(\d+)\s*шт', low) or re.search(r'упаковк[аи]\s*[-–—]?\s*(\d+)\s*шт', desc.lower())
    pack = int(m.group(1)) if m else None
    name = re.sub(r'\s*[-–—]?\s*\(?\s*1\s*(кг|шт)\.?\s*\)?.*$', '', title).strip()
    name = re.sub(r'\s+', ' ', quotes(name)).strip()
    short = re.sub(r'\s+(фаршированные|творожные)\b', '', name)
    price = round(int(it['price']['amount']) / 100)

    # split the description into blocks by blank lines; recognise keyed blocks
    lines = [l.rstrip() for l in desc.replace('\r', '').split('\n')]
    blocks, cur = [], []
    for l in lines:
        if not clean(l) and not re.search(r'[—]{3,}', l):
            if cur: blocks.append(cur); cur = []
        else:
            cur.append(l)
    if cur: blocks.append(cur)

    intro, pros, sostav, kbju, cook, store = [], [], '', None, [], ''
    mode = None
    seen_first = False
    for b in blocks:
        txt = '\n'.join(b)
        head = clean(b[0]).lower()
        if head.startswith('состав') or head.startswith('📋 состав'):
            raw = [('---' if re.match(r'^[—\-–]{3,}$', x.strip()) else clean(x)) for x in re.split(r'\n|•', '\n'.join(b))]
            raw = [re.sub(r'^состав\s*:?\s*', '', x, flags=re.I) for x in raw]
            groups, curg = [], []
            for x in raw:
                if x == '---': groups.append(curg); curg = []; continue
                if x: curg.append(x)
            groups.append(curg)
            nosoy = False
            for g2 in groups:
                for k2, x in enumerate(g2):
                    if x.lower().startswith('без сои'): nosoy = True; g2[k2] = ''
            groups = [[x.rstrip('.') for x in g2 if x] for g2 in groups if any(g2)]
            if len(groups) == 2:
                sostav = 'Тесто: ' + ', '.join(groups[0]) + '. Начинка: ' + ', '.join(groups[1])
            else:
                sostav = ', '.join(x for g2 in groups for x in g2)
            sostav = re.sub(r',\s*,', ',', sostav).replace(' ,', ',').strip(' ,.')
            mode = None; continue
        if False:
            body = ' '.join(clean(x) for x in b)
            body = re.sub(r'^состав\s*:?\s*', '', body, flags=re.I)
            body = re.sub(r'\s*-{3,}|—{3,}', '', body)
            # bullet lists -> comma list
            parts = [clean(x) for x in re.split(r'\n|•', '\n'.join(b)) if clean(x) and not re.match(r'^[—-]{3,}$', clean(x))]
            if len(parts) > 2:
                parts = [re.sub(r'^состав\s*:?\s*', '', p, flags=re.I) for p in parts]
                parts = [p for p in parts if p]
                body = ', '.join(parts)
            sostav = body.replace(' ,', ',')
            mode = None; continue
        if 'ценность' in head:
            t = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', txt)
            g = lambda rx: (lambda mm: float(mm.group(1).replace(',', '.')) if mm else None)(re.search(rx, t))
            N = r'(\d+(?:[.,]\d+)?)'; k = g(N + r'\s*ккал'); bb = g(r'Б\s*-\s*' + N); zh = g(r'Ж\s*-\s*' + N); u = g(r'У\s*-\s*' + N)
            kbju = {'k': k, 'b': bb, 'zh': zh, 'u': u} if k else None
            mode = None; continue
        if head.startswith('срок хранения'):
            store = re.sub(r'^срок хранения\s*[:\-–]?\s*', '', clean(b[0]), flags=re.I)
            rest = [clean(x) for x in b[1:] if clean(x)]
            for x in rest:
                if re.match(r'(как готовить|способ приготовления)', x.lower()):
                    cook.append(re.sub(r'^(как готовить|способ приготовления)\s*:?\s*', '', x, flags=re.I))
            mode = None; continue
        if re.match(r'(способ приготовления|как варить|как готовить)', head):
            for x in b:
                x = clean(x)
                if not x: continue
                x = re.sub(r'^(способ приготовления|как варить|как готовить)\s*[:?!]?\s*(проще простого!?)?\s*', '', x, flags=re.I)
                if x and not x.lower().startswith('срок хранения'): cook.append(x)
                elif x.lower().startswith('срок хранения'): store = re.sub(r'^срок хранения\s*[:\-–]?\s*', '', x, flags=re.I)
            mode = 'cook'; continue
        if head.startswith('упаковка'):
            continue
        if head.startswith('преимущества') or head.startswith('почему наши') or head.startswith('✨ почему'):
            mode = 'pros'
            for x in b[1:]:
                if clean(x): pros.append(clean(x))
            continue
        if mode == 'pros' and all(clean(x).startswith(('Домашний', 'Здоровое', 'Легкость', 'Чистый', 'Быстро', 'Универс', 'Честное', 'Правильный', 'Нежная', 'Аккуратная', 'Бережная')) or x.strip().startswith('•') for x in b if clean(x)):
            pros += [clean(x) for x in b if clean(x)]; continue
        if mode == 'cook' and len(b) == 1 and not b[0].strip().startswith('•') and len(intro) > 0 and 'Подавайте' in b[0]:
            cook.append(clean(b[0])); continue
        # first line repeating the product name (e.g. "Тефтели свиные(1кг.)")
        for x in b:
            cx = clean(x)
            if not cx: continue
            if not intro and not seen_first and len(cx) < 70 and not cx.endswith(('.', '!', '?')):
                seen_first = True; continue
            seen_first = True
            if cx.lower().startswith('упаковка'):
                continue
            intro.append(cx)
    # cooking advice hidden in pros (veg cutlets)
    if not cook:
        for p in pros:
            if p.lower().startswith(('легкость приготовления', 'быстро и удобно')):
                cook.append(re.sub(r'^[^:]+:\s*', '', p))
    store = store.rstrip('. ')
    cook = [c[0].upper() + c[1:] for c in cook if c]
    cooktxt = ' '.join(cook).lower()
    timer = []
    mm = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*мин', cooktxt)
    if mm:
        hi = int(mm.group(2))
        if 'всплы' in cooktxt:
            timer = [['Варим после всплытия', hi]]
        elif 'рисунк' in cooktxt:
            timer = [['Сторона с рисунком', hi], ['Вторая сторона', hi]] + ([['Под крышкой', 2]] if 'паре минут' in cooktxt else [])
        elif 'двух сторон' in cooktxt or 'каждой стороны' in cooktxt:
            timer = [['Первая сторона, под крышкой', hi], ['Переверните: вторая сторона', hi]]
        elif 'микроволнов' in cooktxt:
            timer = [['В микроволновке', hi]]
        elif 'туши' in cooktxt:
            timer = [['Тушим в соусе', hi]]
        else:
            timer = [['Готовим', hi]]
    por = 4 if unit == 'kg' else max(1, (pack or 2) // 2)
    photos = [p['id'] for p in it.get('photos', [])][:4]
    return {
        'id': it['id'], 'name': name, 'short': short, 'cat': cat, 'unit': unit, 'pack': pack, 'price': price,
        'pp': price * (pack or 1) if unit == 'pc' else price, 'por': por,
        'avail': it.get('availability', 0) == 0,
        'np': len(photos), 'intro': intro, 'pros': pros, 'sostav': sostav, 'kbju': kbju,
        'cook': cook, 'store': store, 'timer': timer,
    }


def build(items):
    cat = [parse(it) for it in items]
    cat.sort(key=lambda x: ORDER.index(x['cat']))
    return {'cats': [[k, t] for k, t, _ in CATS], 'items': cat}


if __name__ == '__main__':
    items = json.load(open(SRC))['response']['items']
    cat = [parse(it) for it in items]
    cat.sort(key=lambda x: ORDER.index(x['cat']))
    json.dump({'cats': [[k, t] for k, t, _ in CATS], 'items': cat}, open(OUT, 'w'), ensure_ascii=False, indent=1)
    for c in cat:
        print(c['cat'], '|', c['name'], '|', c['short'], '|', c['unit'], c['pack'], c['price'], c['pp'], 'por', c['por'], '| kbju', c['kbju'], '| timer', c['timer'])
        print('   sostav:', c['sostav'][:150])
        print('   cook:', ' / '.join(c['cook'])[:220])
        print('   store:', c['store'], '| pros', len(c['pros']), '| intro', ' / '.join(c['intro'])[:160])
