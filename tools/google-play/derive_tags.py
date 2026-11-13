"""derive_tags.py (Google Play) — offline tag derivation for the merged GP catalog.
Usage: python3 derive_tags.py games.json games.tagged.json
Primary: playChips from the scrape (weight 3). Then genres / playCategory (weight 2).
Fallback: keyword regexes over title/about/description, reused from the App Store derive_tags.py (EN text, hl=en).
Writes tags (list, by weight) + tagVotes ({tag: weight}) in the Steam record shape; writes TAG_STATS.json."""
import json,sys,collections,re,os
# keyword rules copied unchanged from App Store derive_tags.py v0
KW={'Roguelike':r'rogue-?li[kt]e|ローグライ','Idle':r'\bidle\b|放置','Match 3':r'match[- ]?3|match three|3[- ]gewinnt|マッチ3','Merge':r'\bmerge\b|fusion|マージ','Tower Defense':r'tower defen[cs]e|タワーディフェンス','Survival':r'surviv|サバイバル|überleb','Zombies':r'zombie|ゾンビ','Multiplayer':r'multiplayer|multijoueur|mehrspieler|pvp|online battle|対戦','Co-op':r'\bco-?op\b|coopérat|協力','Puzzle':r'puzzle|パズル|rätsel|casse-tête','Shooter':r'shoot|fps|シューティング|tir\b','Battle Royale':r'battle royale','MOBA':r'\bmoba\b','Gacha':r'gacha|ガチャ|summon heroes','Anime':r'anime|アニメ','Card Battler':r'deck|card battle|カードバトル','Solitaire':r'solitaire|patience|ソリティア','Word':r'\bwords?\b|crossword|wort|mots','Trivia':r'trivia|quiz|クイズ','Racing':r'\bracing\b|\brace\b|レース|course','Farming':r'\bfarm|農場|ferme|bauernhof','City Builder':r'city build|build your city|街づくり','Simulation':r'simulat|シミュレーション','Tycoon':r'tycoon|経営','Sandbox':r'sandbox|open world|オープンワールド','Horror':r'horror|ホラー|horreur','Platformer':r'platformer|jump and run','Hidden Object':r'hidden object|wimmelbild|objets cachés','Hyper-Casual':r'one[- ]tap|hyper[- ]?casual','Strategy':r'strateg|戦略','RPG':r'\brpg\b|role[- ]?playing|ロールプレイング|jeu de rôle','Sports':r'soccer|football|basketball|golf|tennis|baseball|サッカー|野球','Casino':r'casino|slots?\b|poker|blackjack|カジノ','Educational':r'learn|educat|kids|lernen|éducati','Physics':r'physics|physik','Pixel Graphics':r'pixel','Story Rich':r'story|narrative|ストーリー|histoire|geschichte','Turn-Based':r'turn-based|tour par tour|rundenbasiert|ターン制','Fantasy':r'fantasy|ファンタジー|fantastique','Sci-fi':r'sci-?fi|space|宇宙|espace|weltraum','Music':r'rhythm|music|リズム|musique|musik','Offline':r'offline|オフライン|hors ligne'}
KWc={k:re.compile(v,re.I) for k,v in KW.items()}
NORM={'Role Playing':'RPG','Role-playing':'RPG','Role playing':'RPG'}
def tags_for(g):
    v=collections.Counter()
    for c in g.get('playChips') or []: v[NORM.get(c,c)]+=3
    for x in g.get('genres') or []: v[NORM.get(x,x)]+=2
    if not g.get('genres') and g.get('playCategory','').startswith('GAME_'):
        v[g['playCategory'][5:].replace('_',' ').title()]+=2
    t=' '.join(str(g.get(k) or '') for k in ('title','about','description'))
    for k,r in KWc.items():
        n=len(r.findall(t))
        if n: v[NORM.get(k,k)]+=min(n,3)
    return v
if __name__=='__main__':
    d=json.load(open(sys.argv[1]))
    for g in d:
        v=tags_for(g); g['tags']=[k for k,_ in v.most_common()]; g['tagVotes']=dict(v.most_common())
    json.dump(d,open(sys.argv[2],'w'),ensure_ascii=False)
    N=len(d);c=collections.Counter(t for g in d for t in g['tags'])
    st={'games':N,'withTag':sum(1 for g in d if g['tags']),'withPlayChips':sum(1 for g in d if g.get('playChips')),
        'avgTags':round(sum(len(g['tags']) for g in d)/N,2),'distinctTags':len(c),'top40':c.most_common(40)}
    st['coveragePct']=round(100*st['withTag']/N,1)
    json.dump(st,open(os.path.join(os.path.dirname(sys.argv[2]) or '.','TAG_STATS.json'),'w'),indent=1)
    print({k:v for k,v in st.items() if k!='top40'});print(c.most_common(25))
