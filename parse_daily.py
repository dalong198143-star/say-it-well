import json, os

base = os.path.expanduser("~/AppData/Local/Temp")
files = {
    'finance': os.path.join(base, 'finance.json'),
    'oss': os.path.join(base, 'oss.json'),
    'cn_law': os.path.join(base, 'cn_law.json')
}
for label, path in files.items():
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = data.get('data', {}).get('results', [])
    print('\n===== {} ({} results) ====='.format(label.upper(), len(results)))
    for i, r in enumerate(results[:5]):
        print('#{}: {}'.format(i+1, r['title']))
        print('   URL: {}'.format(r['url']))
        print('   {}'.format(r.get('content','')[:300]))
        print()
