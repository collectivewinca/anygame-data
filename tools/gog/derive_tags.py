"""derive_tags.py (GOG) — offline tag derivation for the merged GOG catalog.
Usage: python3 derive_tags.py games.json games.tagged.json
Primary: GOG catalog tags + genres (weight 2). Compound genres split via XB map.
Fallback: keyword regexes over title (EN), reused from Epic/App Store derive_tags.
Writes tags (list, by weight) + tagVotes; writes TAG_STATS.json."""
import json,sys,collections,re,os
KW={'Roguelike':r'rogue-?li[kt]e|ローグライ','Idle':r'\bidle\b|放置','Match 3':r'match[- ]?3|match three|3[- ]gewinnt|マッチ3','Merge':r'\bmerge\b|fusion|マージ','Tower Defense':r'tower defen[cs]e|タワーディフェンス','Survival':r'surviv|サバイバル|überleb','Zombies':r'zombie|ゾンビ','Multiplayer':r'multiplayer|multijoueur|mehrspieler|pvp|online battle|対戦','Co-op':r'\bco-?op\b|coopérat|協力','Puzzle':r'puzzle|パズル|rätsel|casse-tête','Shooter':r'shoot|fps|シューティング|tir\b','Battle Royale':r'battle royale','MOBA':r'\bmoba\b','Gacha':r'gacha|ガチャ|summon heroes','Anime':r'anime|アニメ','Card Battler':r'deck|card battle|カードバトル','Solitaire':r'solitaire|patience|ソリティア','Word':r'\bwords?\b|crossword|wort|mots','Trivia':r'trivia|quiz|クイズ','Racing':r'\bracing\b|\brace\b|レース|course','Farming':r'\bfarm|農場|ferme|bauernhof','City Builder':r'city build|build your city|街づくり','Simulation':r'simulat|シミュレーション','Tycoon':r'tycoon|経営','Sandbox':r'sandbox|open world|オープンワールド','Horror':r'horror|ホラー|horreur','Platformer':r'platformer|jump and run','Hidden Object':r'hidden object|wimmelbild|objets cachés','Hyper-Casual':r'one[- ]tap|hyper[- ]?casual','Strategy':r'strateg|戦略','RPG':r'\brpg\b|role[- ]?playing|ロールプレイング|jeu de rôle','Sports':r'soccer|football|basketball|golf|tennis|baseball|サッカー|野球','Casino':r'casino|slots?\b|poker|blackjack|カジノ','Educational':r'learn|educat|kids|lernen|éducati','Physics':r'physics|physik','Pixel Graphics':r'pixel','Story Rich':r'story|narrative|ストーリー|histoire|geschichte','Turn-Based':r'turn-based|tour par tour|rundenbasiert|ターン制','Fantasy':r'fantasy|ファンタジー|fantastique','Sci-fi':r'sci-?fi|space|宇宙|espace|weltraum','Music':r'rhythm|music|リズム|musique|musik','Offline':r'offline|オフライン|hors ligne'}
KW.update({'Open World':r'open[- ]world','Souls-like':r'souls-?like|soulslike','Metroidvania':r'metroidvania','Stealth':r'stealth','Hack and Slash':r'hack[- ]and[- ]slash|hack ?n ?slash','Visual Novel':r'visual novel','Local Co-op':r'local co-?op|couch co-?op|split[- ]?screen','Cozy':r'\bcozy\b|\bcosy\b|relaxing','Dungeon Crawler':r'dungeon','Bullet Hell':r'bullet hell|shmup|shoot.em.up','Detective':r'detective|mystery|investigat','Mech':r'\bmechs?\b|\bmecha\b','Pirates':r'pirate','Western':r'wild west|cowboy|\bwestern\b','Ninja':r'ninja|samurai','Post-apocalyptic':r'post-?apocalyp','Medieval':r'medieval|knight','Cyberpunk':r'cyberpunk','Dating Sim':r'dating|romance','Fishing':r'fishing','Cooking':r'cooking|chef|restaurant','Space Sim':r'spaceship|starship','Military':r'military|soldier|warfare','Monster Taming':r'tame|collect monsters|creatures to'})
KW.update({'Educational':r'educational|learning game|learn to (read|count|spell)','Music':r'rhythm|music game|beat the','Story Rich':r'story-driven|narrative-driven|branching story|story rich'})
KWc={k:re.compile(v,re.I) for k,v in KW.items()}
NORM={'Role Playing':'RPG','Role-playing':'RPG','Role playing':'RPG','Role Playing Games':'RPG','Driving/Racing':'Racing','Sport':'Sports','Simulator':'Simulation','Music/Rhythm':'Music','Unique':None,'Adult':None,'Point-and-click':None,'Point & Click':'Point and Click','Point and Click':'Point and Click'}
XB={'Action-Adventure':['Action','Adventure'],'Turn-Based Strategy':['Turn-Based','Strategy'],'Rogue-Lite':['Roguelike'],'Rogue-like':['Roguelike'],'Narration':['Story Rich'],'First Person':['First-Person'],'RTS':['Strategy','RTS'],'Action & adventure':['Action','Adventure'],'Family & kids':['Family'],'Kids & family':['Family'],'Puzzle & trivia':['Puzzle'],'Role playing':['RPG'],'Racing & flying':['Racing'],'Card & board':['Card Game','Board Game'],'Classics':['Retro'],'Multi-Player Online Battle Arena':['MOBA'],'Other':[],'Tools':[],'Entertainment':[],'Hobbies & toys':[]}
KWc['Flight']=re.compile(r'flight sim|\bpilot|aircraft|airplane',re.I)
STOP_GOG={'GOG','DRM-Free','Controller support','Single-player','Achievements','Cloud Saves','Overlay','In Development','Early Access'}
def tags_for(g):
    v=collections.Counter()
    for p in g.get('platforms') or []:
        pl=str(p).lower()
        if 'vr' in pl: v['VR']+=3
        if 'linux' in pl: v['Linux']+=1
        if 'mac' in pl: v['Mac']+=1
    for x in (g.get('gogTags') or g.get('tags') or []):
        if not x or x in STOP_GOG: continue
        for n in XB.get(x,[NORM.get(x,x)]):
            if n: v[n]+=2
    for x in g.get('genres') or []:
        for n in XB.get(x,[NORM.get(x,x)]):
            if n: v[n]+=2
    for x in g.get('categories') or []:
        if x in ('Single-player','Multi-player','Co-op','Local Co-op','Online Co-op','Controller support'):
            n=NORM.get(x,x)
            if n and n not in STOP_GOG: v[n]+=1
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
    n=sum(1 for g in d if g['tags'])
    c=collections.Counter(t for g in d for t in g['tags'])
    stats={'n':len(d),'tagged':n,'pct':round(100*n/len(d),1),'avg':round(sum(len(g['tags']) for g in d)/len(d),2),'top':c.most_common(40)}
    json.dump(stats,open('TAG_STATS.json','w'),indent=2)
    print(stats['n'],stats['tagged'],stats['pct'],'avg',stats['avg'])
    print(stats['top'][:20])
