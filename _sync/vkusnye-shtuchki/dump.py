# One-shot dump of public data of club197509207 (Лавка «Вкусные штучки») for building her site.
# Runs in GitHub Actions with VK_TOKEN (service token). Writes JSON into _sync/vkusnye-shtuchki/data/.
import json, os, time, urllib.parse, urllib.request
GID = 197509207
OUT = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0'}
def api(method, **params):
    params.update(access_token=os.environ['VK_TOKEN'], v='5.199')
    req = urllib.request.Request('https://api.vk.com/method/' + method, data=urllib.parse.urlencode(params).encode(), headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    time.sleep(0.4)
    if 'error' in d:
        print(method, 'ERROR', d['error'].get('error_msg'))
        return None
    return d['response']
def save(name, obj):
    with open(os.path.join(OUT, name), 'w') as f:
        json.dump(obj, f, ensure_ascii=False)
    print('saved', name)
save('group.json', api('groups.getById', group_id=GID, fields='description,contacts,addresses,links,site,phone,cover,status,city,activity,main_section,market,counters'))
posts, off = [], 0
while True:
    r = api('wall.get', owner_id=-GID, count=100, offset=off)
    if not r or not r['items']: break
    posts += r['items']; off += 100
    if off >= r['count'] or off >= 3000: break
save('wall.json', posts)
albums = api('photos.getAlbums', owner_id=-GID, need_system=1, need_covers=1)
save('albums.json', albums)
photos = {}
for a in (albums or {}).get('items', []):
    aid = a['id']
    if aid in (-6, -7, -15): aid = {-6: 'profile', -7: 'wall', -15: 'saved'}[aid]
    items, off = [], 0
    while True:
        r = api('photos.get', owner_id=-GID, album_id=aid, count=1000, offset=off, rev=1, extended=1)
        if not r or not r['items']: break
        items += r['items']; off += 1000
        if off >= r['count']: break
    photos[str(a['id'])] = items
save('photos.json', photos)
topics = api('board.getTopics', group_id=GID, count=100, preview=1)
save('topics.json', topics)
comm = {}
for t in (topics or {}).get('items', []):
    items, off = [], 0
    while True:
        r = api('board.getComments', group_id=GID, topic_id=t['id'], count=100, offset=off, extended=1)
        if not r or not r['items']: break
        items += r['items']; off += 100
        if off >= r['count']: break
    comm[str(t['id'])] = {'title': t.get('title'), 'items': items, 'profiles': (r or {}).get('profiles', [])}
save('board.json', comm)
