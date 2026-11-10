# Reads the community's public VK market the way a logged-out visitor sees it:
# headless Chrome opens the page, we parse the rendered DOM (no VK token needed).
# VK robots.txt allows /market-<gid> and /market/product/... for all agents.
import html as htmllib, json, os, re, subprocess, sys, tempfile
from html.parser import HTMLParser

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


def dump(url, height=2400, budget=25000):
    """Rendered DOM of a public page (JS executed) or '' on failure."""
    prof = tempfile.mkdtemp(prefix='vkprof')
    cmd = [os.environ.get('CHROME_BIN', 'google-chrome'), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--lang=ru-RU',
           f'--user-data-dir={prof}', f'--window-size=1300,{height}', f'--virtual-time-budget={budget}', '--dump-dom', url]
    if os.environ.get('CI'):
        cmd.insert(1, '--no-sandbox')
    try:
        return subprocess.run(cmd, capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
    except Exception as e:  # noqa: BLE001
        print('chrome failed:', type(e).__name__)
        return ''
    finally:
        subprocess.run(['rm', '-rf', prof])


class _Grab(HTMLParser):
    """Collects the text and the attributes of elements marked with data-testid."""

    def __init__(self, want):
        super().__init__(convert_charrefs=True)
        self.want = want          # testid -> max number of matches to collect
        self.out = {k: [] for k in want}
        self.open = []            # [testid, depth, text parts]
        self.attrs = {k: [] for k in want}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for o in self.open:
            if tag not in VOID:
                o[1] += 1
            if tag == 'br':
                o[2].append('\n')
            elif tag == 'img' and a.get('alt'):
                o[2].append(a['alt'])
        tid = a.get('data-testid')
        if tid in self.want and len(self.attrs[tid]) < self.want[tid]:
            self.attrs[tid].append(a)
            if tag not in VOID:
                self.open.append([tid, 1, []])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for o in list(self.open):
            o[1] -= 1
            if o[1] == 0:
                self.out[o[0]].append(''.join(o[2]))
                self.open.remove(o)

    def handle_data(self, data):
        for o in self.open:
            o[2].append(data)


def _price(text):
    m = re.search(r'(\d[\d\s  ]*)\s*₽', text or '')
    return int(re.sub(r'\D', '', m.group(1))) if m else None


def _key(url):
    """Stable part of a VK photo URL: the path without host and query."""
    return re.sub(r'^https?://[^/]+', '', url.split('?')[0])


def parse_list(html, gid):
    """Storefront page -> {'count': N from the page title or None, 'items': [{'id','title','price','href','thumb'}]}"""
    t = re.search(r'<title>(.*?)</title>', html, re.S)
    title = htmllib.unescape(t.group(1)) if t else ''
    m = re.search(r'(\d+)[\s ]+(?:items?|товар)', title)
    items = []
    chunks = re.split(r'(?=<div[^>]*data-testid="market_storefront_product_list_item_\d+")', html)[1:]
    for ch in chunks:
        i = re.search(r'data-draggable-item-id="(\d+)"', ch[:600])
        href = re.search(r'href="(https://vk\.(?:ru|com)/market/product/[^"?]+-%d-(\d+))' % gid, ch)
        if not (i or href):
            continue
        pid = int(i.group(1)) if i else int(href.group(2))
        g = _Grab({'miniproductcard-name': 1, 'miniproductcard-price': 1, 'miniproductcard-photo': 1})
        g.feed(ch)
        name = (g.out['miniproductcard-name'] or [''])[0].strip() or (g.attrs['miniproductcard-photo'] or [{}])[0].get('aria-label', '')
        img = re.search(r'<img[^>]+src="([^"]+)"', ch)
        items.append({'id': pid, 'title': name.strip(), 'price': _price((g.out['miniproductcard-price'] or [''])[0]),
                      'href': href.group(1) if href else f'https://vk.ru/product-{gid}_{pid}',
                      'thumb': _key(htmllib.unescape(img.group(1))) if img else ''})
    seen, uniq = set(), []
    for it in items:
        if it['id'] not in seen:
            seen.add(it['id']); uniq.append(it)
    return {'count': int(m.group(1)) if m else None, 'title': title, 'items': uniq}


def parse_product(html):
    """Product page -> {'title','price','description','photos':[url]} or None if the page did not render."""
    g = _Grab({'market_item_page_title': 1, 'market_item_page_price': 1, 'market_item_page_description': 1, 'showmoretext-in': 1})
    g.feed(html)
    title = (g.out['market_item_page_title'] or [''])[0].strip()
    price = _price((g.out['market_item_page_price'] or [''])[0])
    if not title or price is None:
        return None
    desc = (g.out['showmoretext-in'] or g.out['market_item_page_description'] or [''])[0]
    photos, keys = [], set()
    for m in re.finditer(r'<[^>]+data-testid="item_page_photo_\d+"[^>]*>', html):
        u = re.search(r'imageurl="([^"]+)"', m.group(0))
        if u:
            url = htmllib.unescape(u.group(1))
            if _key(url) not in keys:
                keys.add(_key(url)); photos.append(url)
    if not photos:
        u = re.search(r'data-testid="item_page_main_photo"[^>]*>\s*<img[^>]+src="([^"]+)"', html)
        if u:
            photos.append(htmllib.unescape(u.group(1)))
    return {'title': title, 'price': price, 'description': desc.strip('\n'), 'photos': photos}


def big(url, width=1280):
    """Largest version up to `width` px of a VK photo URL that carries an as= size list."""
    m = re.search(r'[?&]as=([0-9x,%C]+)', url)
    if not m:
        return url
    sizes = [tuple(map(int, s.split('x'))) for s in m.group(1).replace('%2C', ',').split(',') if 'x' in s]
    ok = [s for s in sizes if s[0] <= width] or sizes
    w = max(ok)[0]
    return re.sub(r'([?&])cs=\d+x\d+', r'\g<1>cs=%dx0' % w, url) if re.search(r'[?&]cs=', url) else url + '&cs=%dx0' % w


if __name__ == '__main__':  # probe: python3 vkpage.py <gid> [out.json]
    gid = int(sys.argv[1])
    lst = parse_list(dump(f'https://vk.com/market-{gid}', height=9000), gid)
    res = {'title': lst['title'][:120], 'count': lst['count'], 'parsed': len(lst['items']), 'first': lst['items'][:2]}
    if lst['items']:
        p = parse_product(dump(lst['items'][0]['href']))
        res['product'] = p and {'title': p['title'], 'price': p['price'], 'desc_len': len(p['description']), 'photos': len(p['photos']),
                                'photo0': p['photos'][0][:90] if p['photos'] else ''}
    out = json.dumps(res, ensure_ascii=False, indent=1)
    print(out)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w', encoding='utf-8').write(out + '\n')
