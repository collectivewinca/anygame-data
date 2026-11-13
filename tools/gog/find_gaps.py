"""Embed games, propose tag-combo concepts, keep the ones farthest from any real game.
Usage: python find_gaps.py games.json out.json  (games = platform-agnostic records)"""
import json, sys, random, itertools, collections, numpy as np
from fastembed import TextEmbedding
random.seed(7)
games = [g for g in json.load(open(sys.argv[1])) if g.get("type") in (None, "game") and (g.get("description") or g.get("tags"))]
def text(g): return f"Tags: {', '.join(g['tags'][:12])}. Genres: {', '.join((g.get("genres") or []))}. {(g.get("description") or "")[:600]}"
m = TextEmbedding("BAAI/bge-small-en-v1.5")
E = np.array(list(m.embed([text(g) for g in games], batch_size=256)), dtype=np.float32)
E /= np.linalg.norm(E, axis=1, keepdims=True)
np.save(sys.argv[2] + ".emb.npy", E)
# catalog density: mean cosine distance to 10 nearest neighbours
def knn(Q, k):
    S = Q @ E.T; idx = np.argpartition(-S, k, axis=1)[:, :k]
    s = np.take_along_axis(S, idx, 1); o = np.argsort(-s, 1)
    return np.take_along_axis(idx, o, 1), np.take_along_axis(s, o, 1)
# tag stats
tc = collections.Counter(t for g in games for t in g["tags"][:12])
pc = collections.Counter(p for g in games for p in itertools.combinations(sorted(g["tags"][:12]), 2))
STOP = {"Casual","Family","Action","Adventure","Retro","Indie","Classic","2D","3D","Atmospheric","Great Soundtrack","Linux","Mac","Controller support","Single-player"}  # GOG: storefront + platform noise
vocab = [t for t, c in tc.most_common(350) if c >= 10 and t not in STOP]
print('vocab', len(vocab))
cands = set(); _tries = 0
while len(cands) < 6000 and _tries < 400000:
    _tries += 1
    combo = tuple(sorted(random.sample(vocab, 3)))
    pairs = list(itertools.combinations(combo, 2))
    # plausible: every pair seen at least twice, but whole triple never in one game's tags
    if all(pc[p] >= 2 for p in pairs): cands.add(combo)
cands = list(cands)
tripseen = set(tuple(sorted(c)) for g in games for c in itertools.combinations(g["tags"][:12], 3))
cands = [c for c in cands if c not in tripseen]
Q = np.array(list(m.embed([f"Tags: {', '.join(c)}." for c in cands], batch_size=256)), dtype=np.float32)
Q /= np.linalg.norm(Q, axis=1, keepdims=True)
# baseline: same kind of tag-only query for real games, to calibrate distances
base = np.array(list(m.embed([f"Tags: {', '.join(g['tags'][:3])}." for g in random.sample(games, min(1500, len(games)))])), dtype=np.float32)
base /= np.linalg.norm(base, axis=1, keepdims=True)
_, bs = knn(base, 3); thr = np.percentile(bs[:, 0], 5)
idx, sims = knn(Q, 3)
order = np.argsort(sims[:, 0])  # lowest nearest-neighbour similarity = emptiest
out, used = [], collections.Counter()
for i in order:
    c = cands[i]
    if any(used[t] >= 1 for t in c): continue  # diversity: each tag once
    for t in c: used[t] += 1
    out.append({"tags": c, "nnSim": float(sims[i, 0]), "pairCounts": {"+".join(p): pc[p] for p in itertools.combinations(c, 2)},
                "nearest": [{"title": games[j]["title"], "url": games[j]["url"], "sim": float(s), "tags": games[j]["tags"][:6]} for j, s in zip(idx[i], sims[i])]})
    if len(out) >= 40: break
json.dump({"games": len(games), "candidates": len(cands), "baselineNnSimP5": float(thr), "gaps": out}, open(sys.argv[2], "w"), indent=1)
print(len(games), len(cands), thr); [print(o["tags"], round(o["nnSim"], 3), [n["title"] for n in o["nearest"]]) for o in out]
