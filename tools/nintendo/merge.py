"""merge.py (Nintendo) — merge per-batch games.json. Step 1 by nsuid (shared inside a region: US/CA, GB/DE/FR) incl.
SEEN_ELSEWHERE "cc/id" hits. Step 2 cross-region by normalized title (US/EU/JP nsuids differ for the same game); first
record kept (batch order us, gb-ca, de-fr, jp-au), `countries` unioned, `altIds` keeps the other regions' nsuids.
Usage: python3 merge.py out.json us=../anygame-nintendo-catalog-us gb-ca=... de-fr=... jp-au=..."""
import json,sys,os,re,unicodedata,collections
def norm(t):
    t=unicodedata.normalize('NFKC',t or '').lower()
    t=re.sub(r'[™®©]','',t); t=re.sub(r'\s*[-–:]?\s*(for )?nintendo switch( 2)?( edition)?\s*$','',t)
    return re.sub(r'[^\w]+','',t)
byid,cc,order={}, collections.defaultdict(set),[]
for a in sys.argv[2:]:
    b,p=a.split('=',1)
    for g in json.load(open(p+'/games.json')):
        cc[g['id']].add(g.get('country'))
        if g['id'] in byid: continue
        g['batch']=b; byid[g['id']]=g; order.append(g['id'])
    s=p+'/seen-elsewhere.json'
    if os.path.exists(s):
        for x in json.load(open(s)): c,i=x.split('/',1); cc[i].add(c)
out,key={},{}
for i in order:
    g=byid[i]; k=norm(g['title']) or i
    if k in key:
        h=out[key[k]]; h['countries']=sorted(set(h['countries'])|cc[i]); h.setdefault('altIds',[]).append(i)
        if not h.get('genres') and g.get('genres'): h['genres']=g['genres']
        continue
    g['countries']=sorted(cc[i]); key[k]=i; out[i]=g
L=list(out.values())
json.dump(L,open(sys.argv[1],'w'),ensure_ascii=False)
print(len(byid),'unique nsuids;',len(L),'unique titles;',sum(g.get('isFree') is True for g in L),'free;',sum(g.get('isFree') is False for g in L),'paid;',sum(g.get('isFree') is None for g in L),'price-unknown')
print(collections.Counter(g['batch'] for g in L)); print(collections.Counter(c for g in L for c in g['countries']))
