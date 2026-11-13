"""merge.py (Epic) — merge per-batch games.json by Store productId; first record kept; adds `batch`
and `countries` (own country + every SEEN_ELSEWHERE hit "cc/id" from the batch KVS).
Usage: python3 merge.py out.json us=../anygame-epic-catalog-us gb-ca=... de-fr=... jp-au=..."""
import json,sys,os,collections
out,seen,cc={},set(),collections.defaultdict(set)
for a in sys.argv[2:]:
    b,p=a.split('=',1)
    for g in json.load(open(p+'/games.json')):
        if 'title' not in g or 'isFree' not in g and not g.get('_detail',True): pass
        cc[g['id']].add(g.get('country') or 'us')
        if g['id'] in out: continue
        g['batch']=b; out[g['id']]=g
    s=p+'/seen-elsewhere.json'
    if os.path.exists(s):
        try:
            for x in json.load(open(s)): c,i=x.split('/',1); cc[i].add(c)
        except Exception: pass
L=list(out.values())
for g in L: g['countries']=sorted(cc[g['id']])
json.dump(L,open(sys.argv[1],'w'),ensure_ascii=False)
print(len(L),'unique;',sum(1 for g in L if g.get('isFree')),'free;',sum(1 for g in L if g.get('isFree') is None),'no-detail;',collections.Counter(g['batch'] for g in L))
print(collections.Counter(c for g in L for c in g['countries']))
