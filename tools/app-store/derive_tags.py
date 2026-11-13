"""derive_tags.py v0 (new; no prior script existed) — offline App Store tag derivation.
Usage: python3 derive_tags.py games.json games.tagged.json
Tags = English genre names from Apple genreIds seen in chartHits (owners 'cc/chart/genreId/#rank')
     + English genre strings already on the record + keyword tags from title/about/description (EN + some DE/FR/JP).
Writes tags (list) and tagVotes ({tag: hit count}) in the Steam record shape."""
import json,re,sys,collections
GID={'7001':'Action','7002':'Adventure','7003':'Arcade','7004':'Board','7005':'Card','7006':'Casino','7007':'Dice','7008':'Educational','7009':'Family','7011':'Music','7012':'Puzzle','7013':'Racing','7014':'RPG','7015':'Simulation','7016':'Sports','7017':'Strategy','7018':'Trivia','7019':'Word'}
EN={'Action','Adventure','Arcade','Board','Card','Casino','Dice','Educational','Family','Music','Puzzle','Racing','Role Playing','Simulation','Sports','Strategy','Trivia','Word','Casual'}
KW={'Roguelike':r'rogue-?li[kt]e|ローグライ','Idle':r'\bidle\b|放置','Match 3':r'match[- ]?3|match three|3[- ]gewinnt|マッチ3','Merge':r'\bmerge\b|fusion|マージ','Tower Defense':r'tower defen[cs]e|タワーディフェンス','Survival':r'surviv|サバイバル|überleb','Zombies':r'zombie|ゾンビ','Multiplayer':r'multiplayer|multijoueur|mehrspieler|pvp|online battle|対戦','Co-op':r'\bco-?op\b|coopérat|協力','Puzzle':r'puzzle|パズル|rätsel|casse-tête','Shooter':r'shoot|fps|シューティング|tir\b','Battle Royale':r'battle royale','MOBA':r'\bmoba\b','Gacha':r'gacha|ガチャ|summon heroes','Anime':r'anime|アニメ','Card Battler':r'deck|card battle|カードバトル','Solitaire':r'solitaire|patience|ソリティア','Word':r'\bwords?\b|crossword|wort|mots','Trivia':r'trivia|quiz|クイズ','Racing':r'\bracing\b|\brace\b|レース|course','Farming':r'\bfarm|農場|ferme|bauernhof','City Builder':r'city build|build your city|街づくり','Simulation':r'simulat|シミュレーション','Tycoon':r'tycoon|経営','Sandbox':r'sandbox|open world|オープンワールド','Horror':r'horror|ホラー|horreur','Platformer':r'platformer|jump and run','Hidden Object':r'hidden object|wimmelbild|objets cachés','Hyper-Casual':r'one[- ]tap|hyper[- ]?casual','Strategy':r'strateg|戦略','RPG':r'\brpg\b|role[- ]?playing|ロールプレイング|jeu de rôle','Sports':r'soccer|football|basketball|golf|tennis|baseball|サッカー|野球','Casino':r'casino|slots?\b|poker|blackjack|カジノ','Educational':r'learn|educat|kids|lernen|éducati','Physics':r'physics|physik','Pixel Graphics':r'pixel','Story Rich':r'story|narrative|ストーリー|histoire|geschichte','Turn-Based':r'turn-based|tour par tour|rundenbasiert|ターン制','Fantasy':r'fantasy|ファンタジー|fantastique','Sci-fi':r'sci-?fi|space|宇宙|espace|weltraum','Music':r'rhythm|music|リズム|musique|musik','Offline':r'offline|オフライン|hors ligne'}
KWc={k:re.compile(v,re.I) for k,v in KW.items()}
def tags_for(g):
    v=collections.Counter()
    for h in g.get('chartHits') or [g.get('owners') or '']:
        p=h.split('/')
        if len(p)>2 and p[2] in GID: v[GID[p[2]]]+=2
    for x in g.get('genres') or []:
        if x in EN and x!='Games': v['RPG' if x=='Role Playing' else x]+=1
    t=' '.join(str(g.get(k) or '') for k in ('title','about','description'))
    for k,r in KWc.items():
        n=len(r.findall(t))
        if n: v[k]+=n
    return v
if __name__=='__main__':
    d=json.load(open(sys.argv[1]))
    for g in d:
        v=tags_for(g); g['tags']=[k for k,_ in v.most_common()]; g['tagVotes']=dict(v.most_common())
    json.dump(d,open(sys.argv[2],'w'),ensure_ascii=False)
    n=sum(1 for g in d if g['tags']);kw=sum(1 for g in d if any(t in KW for t in g['tags']) and set(g['tags'])-set(GID.values()))
    c=collections.Counter(t for g in d for t in g['tags'])
    print(len(d),n,round(100*n/len(d),1),'avg',round(sum(len(g['tags']) for g in d)/len(d),2),'kw-any',sum(1 for g in d if any(k in g['tagVotes'] and KWc[k].search(' '.join(str(g.get(x) or '') for x in('title','about','description'))) for k in KW)))
    print(c.most_common(30))
