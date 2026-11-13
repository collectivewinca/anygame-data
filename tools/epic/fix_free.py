"""fix_free.py (Epic) — unreleased $0 titles without 'free' in title/description are unpriced pre-release, not F2P -> isFree=None.
Usage: python3 fix_free.py games.json (in place)"""
import json,re,sys
R=re.compile(r"free[- ]to[- ]play|\bfree\b|kostenlos|gratuit|無料",re.I)
d=json.load(open(sys.argv[1]));n=0
for g in d:
    if g.get('isFree') and g.get('comingSoon') and not R.search(f"{g.get('title') or ''} {g.get('description') or ''}"): g['isFree']=None;n+=1
json.dump(d,open(sys.argv[1],'w'),ensure_ascii=False);print('set unknown',n)
