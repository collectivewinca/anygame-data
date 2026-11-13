"""derive_tags.py (Nintendo) — offline tag derivation for the merged Nintendo eShop catalog (US/GB/DE/FR/JP).
Usage: python3 derive_tags.py games.json games.tagged.json
Primary: Xbox store categories (weight 2; compound ones like 'Action & adventure' split via XB). Game Pass not a tag.
Fallback: keyword regexes over title/about/description, reused from the App Store derive_tags.py (EN text, hl=en).
Writes tags (list, by weight) + tagVotes ({tag: weight}) in the Steam record shape; writes TAG_STATS.json."""
import json,sys,collections,re,os
# keyword rules copied unchanged from App Store derive_tags.py v0
KW={'Roguelike':r'rogue-?li[kt]e|ローグライ','Idle':r'\bidle\b|放置','Match 3':r'match[- ]?3|match three|3[- ]gewinnt|マッチ3','Merge':r'\bmerge\b|fusion|マージ','Tower Defense':r'tower defen[cs]e|タワーディフェンス','Survival':r'surviv|サバイバル|überleb','Zombies':r'zombie|ゾンビ','Multiplayer':r'multiplayer|multijoueur|mehrspieler|pvp|online battle|対戦','Co-op':r'\bco-?op\b|coopérat|協力','Puzzle':r'puzzle|パズル|rätsel|casse-tête','Shooter':r'shoot|fps|シューティング|tir\b','Battle Royale':r'battle royale','MOBA':r'\bmoba\b','Gacha':r'gacha|ガチャ|summon heroes','Anime':r'anime|アニメ','Card Battler':r'deck|card battle|カードバトル','Solitaire':r'solitaire|patience|ソリティア','Word':r'\bwords?\b|crossword|wort|mots','Trivia':r'trivia|quiz|クイズ','Racing':r'\bracing\b|\brace\b|レース|course','Farming':r'\bfarm|農場|ferme|bauernhof','City Builder':r'city build|build your city|街づくり','Simulation':r'simulat|シミュレーション','Tycoon':r'tycoon|経営','Sandbox':r'sandbox|open world|オープンワールド','Horror':r'horror|ホラー|horreur','Platformer':r'platformer|jump and run','Hidden Object':r'hidden object|wimmelbild|objets cachés','Hyper-Casual':r'one[- ]tap|hyper[- ]?casual','Strategy':r'strateg|戦略','RPG':r'\brpg\b|role[- ]?playing|ロールプレイング|jeu de rôle','Sports':r'soccer|football|basketball|golf|tennis|baseball|サッカー|野球','Casino':r'casino|slots?\b|poker|blackjack|カジノ','Educational':r'learn|educat|kids|lernen|éducati','Physics':r'physics|physik','Pixel Graphics':r'pixel','Story Rich':r'story|narrative|ストーリー|histoire|geschichte','Turn-Based':r'turn-based|tour par tour|rundenbasiert|ターン制','Fantasy':r'fantasy|ファンタジー|fantastique','Sci-fi':r'sci-?fi|space|宇宙|espace|weltraum','Music':r'rhythm|music|リズム|musique|musik','Offline':r'offline|オフライン|hors ligne'}
KW.update({'Open World':r'open[- ]world','Souls-like':r'souls-?like|soulslike','Metroidvania':r'metroidvania','Stealth':r'stealth','Hack and Slash':r'hack[- ]and[- ]slash|hack ?n ?slash','Visual Novel':r'visual novel','Local Co-op':r'local co-?op|couch co-?op|split[- ]?screen','Cozy':r'\bcozy\b|\bcosy\b|relaxing','Dungeon Crawler':r'dungeon','Bullet Hell':r'bullet hell|shmup|shoot.em.up','Detective':r'detective|mystery|investigat','Mech':r'\bmechs?\b|\bmecha\b','Pirates':r'pirate','Western':r'wild west|cowboy|\bwestern\b','Ninja':r'ninja|samurai','Post-apocalyptic':r'post-?apocalyp','Medieval':r'medieval|knight','Cyberpunk':r'cyberpunk','Dating Sim':r'dating|romance','Fishing':r'fishing','Cooking':r'cooking|chef|restaurant','Space Sim':r'spaceship|starship','Military':r'military|soldier|warfare','Monster Taming':r'tame|collect monsters|creatures to'})
KW.update({'Educational':r'educational|learning game|learn to (read|count|spell)','Music':r'rhythm|music game|beat the','Story Rich':r'story-driven|narrative-driven|branching story|story rich'})
KWc={k:re.compile(v,re.I) for k,v in KW.items()}
NORM={'Role Playing Games':'RPG','Driving/Racing':'Racing','Sport':'Sports','Simulator':'Simulation','Music/Rhythm':'Music','Unique':None,'Adult':None,'Role Playing':'RPG','Role-playing':'RPG','Role playing':'RPG'}
XB={'Action & adventure':['Action','Adventure'],'Family & kids':['Family'],'Kids & family':['Family'],'Puzzle & trivia':['Puzzle'],
    'Role playing':['RPG'],'Racing & flying':['Racing'],'Card & board':['Card Game','Board Game'],'Classics':['Retro'],
    'Multi-Player Online Battle Arena':['MOBA'],'Other':[],'Tools':[],'Entertainment':[],'Hobbies & toys':[]}

# Nintendo genre labels (US Algolia, NoE GB/DE/FR, JP) -> shared tag names; store/app buckets dropped
NORM.update({'Shooting':'Shooter','Narrative adventure':'Story Rich','Tabletop':'Board Game','Application':None,'Education':'Educational',
 'Other':None,'Lifestyle':None,'Communication':None,'Study':'Educational','Utility':None,'System Tool':None,'Shop Shop':None,'Training':'Fitness',
 'Health & Fitness':'Fitness','Languages':'Educational','Animal Life':'Animals','Football':'Sports','Golf':'Sports','Tennis':'Sports','Basketball':'Sports',
 'Boxing':'Sports','Extreme':'Sports','Other sports':'Sports','American Football':'Sports','Multiplayer':'Multiplayer','Pinball':'Arcade',
 'アドベンチャー':'Adventure','アクション':'Action','アーケード':'Arcade','パズル':'Puzzle','シミュレーション':'Simulation','ロールプレイング':'RPG',
 'その他':None,'パーティー':'Party','ストラテジー':'Strategy','シューティング':'Shooter','学習':'Educational','トレーニング':'Fitness','実用':None,
 'テーブル':'Board Game','レース':'Racing','スポーツ':'Sports','格闘':'Fighting','コミュニケーション':None,'音楽':'Music',
 'Abenteuer':'Adventure','Rennspiel':'Racing','Lernspiel':'Educational','Brettspiel':'Board Game','Kampf':'Fighting','Musik':'Music','Andere':None,
 'Aventure':'Adventure','Casse-tête':'Puzzle','Course':'Racing','Plateforme':'Platformer','Stratégie':'Strategy','Tir':'Shooter','Fête':'Party','Combat':'Fighting','Musique':'Music','Autre':None})
XB['First-Person Shooter']=['Shooter','FPS']
KWc['Flight']=re.compile(r'flight sim|\bpilot|aircraft|airplane',re.I)

# US Algolia gameFeatureLabels / waysToPlayLabels (carried in categories) -> tags, weight 1
FEAT={'Pixel art':'Pixel Graphics','Play for a high score':'Score Attack','Puzzle-solving elements':'Puzzle','Platforming':'Platformer',
 'Raise your stats':'RPG','Survival':'Survival','Start over if you fail':'Roguelike','Random maps & levels':'Procedural Generation',
 'Romance':'Dating Sim','Free roaming':'Open World','First-person':'First-Person','Explore to open up new areas':'Metroidvania',
 'Choose your own path':'Choices Matter','Stealth':'Stealth','Create and play':'Sandbox','Defend your territory':'Tower Defense',
 'Minigames':'Minigames','Rhythmic gameplay':'Music','Motion controls':'Motion Controls','Character customization':'Character Customization',
 'Play for the fastest time':'Time Attack','30+ player battles':'Battle Royale','Online co-op':'Co-op','Compete online':'Multiplayer',
 'Play together on one console':'Local Multiplayer','Meet up and play together':'Local Multiplayer','Cross-platform play':'Cross-Platform'}

def tags_for(g):
    v=collections.Counter()
    for x in g.get('categories') or []:
        if x in FEAT: v[FEAT[x]]+=1
    for p in g.get('platforms') or []:
        if 'VR' in p: v['VR']+=3
    for x in g.get('genres') or []:
        for n in XB.get(x,[NORM.get(x,x)]):
            if n: v[n]+=2
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
    st={'games':N,'withTag':sum(1 for g in d if g['tags']),'withGenres':sum(1 for g in d if g.get('genres')),
        'avgTags':round(sum(len(g['tags']) for g in d)/N,2),'distinctTags':len(c),'top40':c.most_common(40)}
    st['coveragePct']=round(100*st['withTag']/N,1)
    json.dump(st,open(os.path.join(os.path.dirname(sys.argv[2]) or '.','TAG_STATS.json'),'w'),indent=1)
    print({k:v for k,v in st.items() if k!='top40'});print(c.most_common(25))
