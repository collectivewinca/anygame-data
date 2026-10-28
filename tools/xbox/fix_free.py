"""fix_free.py — apply the 0.1.2 Game Pass false-free guard (resolve_free) to records scraped with build 0.1.1 (US run)."""
import json,sys
sys.path.insert(0,'/workspace/xbox-actor/xbox-games-scraper')
from src.catalog import resolve_free
for f in sys.argv[1:]:
    d=json.load(open(f));n=0
    for g in d:
        v=resolve_free(g.get('isFree'),g.get('gamePass'),g.get('title'),g.get('description'))
        if v!=g.get('isFree'): g['isFree']=v;g['priceNote']='game-pass $0, not marked free';n+=1
    json.dump(d,open(f,'w'),ensure_ascii=False);print(f,'changed',n,'free now',sum(g.get('isFree') is True for g in d),'paid',sum(g.get('isFree') is False for g in d),'unknown',sum(g.get('isFree') is None for g in d))
