import json,collections
B=[('us-gb-ca','H5F2LhiHfhsSkdtnE','aNhPtgQvNjT49JV4U'),('de-fr','Gx3BgNFSJLdGTBZQH','sLM9DT5HcB04yRJAK'),('jp-au','VmmIXZOuTjGFYftxS','DNYpt7S5cJGjBuEes')]
m={};seen=collections.defaultdict(set)
for b,_,_ in B:
  for g in json.load(open(f'../anygame-appstore-catalog-batch-{b}/games.json')):
    k=(g.get('platform','appstore'),str(g['id']))
    cc=(g.get('owners') or '/').split('/')[0] or g['url'].split('apple.com/')[1][:2]
    seen[k].add(cc)
    if k not in m: m[k]=dict(g,chartHits=[]);
    if g.get('owners'): m[k]['chartHits'].append(g['owners'])
    if cc=='us' and m[k].get('currency')!='USD': m[k].update({x:g[x] for x in g if x not in('owners',)})  # prefer US/English record
for k,g in m.items(): g['countries']=sorted(seen[k])
out=list(m.values());json.dump(out,open('games.json','w'),ensure_ascii=False)
f=sum(1 for g in out if g.get('isFree'));cc=collections.Counter(c for g in out for c in g['countries'])
ov=collections.Counter(len(g['countries']) for g in out)
print(len(out),f,len(out)-f,dict(cc),dict(sorted(ov.items())))
