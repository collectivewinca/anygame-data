"""merge.py (Google Play) — merge per-batch games.json by package id; first record kept; adds `batch`.
Usage: python3 merge.py out.json us=../anygame-googleplay-catalog-us/games.json gb-ca=... de-fr=... jp-au=..."""
import json,sys
out,seen=[],set()
for a in sys.argv[2:]:
    b,p=a.split('=',1)
    for g in json.load(open(p)):
        if g['id'] in seen: continue
        seen.add(g['id']); g['batch']=b; out.append(g)
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False)
print(len(out),'unique;',sum(1 for g in out if g.get('isFree')),'free')
