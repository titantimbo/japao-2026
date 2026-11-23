import json, os, re, time, urllib.request, urllib.parse
figs = json.load(open('tools/figs.json'))
titles = sorted({f['w'] for f in figs})
UA = {'User-Agent': 'japao-2026-guia/1.0 (personal travel guide; github.com/titantimbo/japao-2026)'}
def get(url):
    for k in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            print('retry', url[:80], e); time.sleep(3 + 3 * k)
    return None
os.makedirs('fotos', exist_ok=True)
man = {}
for i in range(0, len(titles), 40):
    chunk = titles[i:i + 40]
    u = ('https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&prop=pageimages&piprop=thumbnail|name'
         '&pithumbsize=1000&pilimit=50&titles=' + urllib.parse.quote('|'.join(chunk)))
    d = json.loads(get(u))
    q = d['query']; norm = {}
    for n in q.get('normalized', []): norm[n['to']] = n['from']
    for r in q.get('redirects', []): norm[r['to']] = norm.get(r['from'], r['from'])
    for p in q['pages'].values():
        orig = norm.get(p['title'], p['title'])
        th = p.get('thumbnail')
        if not th: print('no image', orig); continue
        slug = re.sub(r'[^A-Za-z0-9]+', '_', orig).strip('_')[:60]
        ext = os.path.splitext(urllib.parse.urlparse(th['source']).path)[1].lower() or '.jpg'
        b = get(th['source'])
        if not b: continue
        fn = f'fotos/{slug}{ext}'
        open(fn, 'wb').write(b)
        man[orig] = {'file': fn, 'source': th['source'], 'name': p.get('pageimage'), 'w': th['width'], 'h': th['height']}
        time.sleep(0.3)
json.dump(man, open('fotos/manifest.json', 'w'), ensure_ascii=False, indent=1)
print(len(man), 'imagens')
