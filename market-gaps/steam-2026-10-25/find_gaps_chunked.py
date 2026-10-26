"""Embed games, propose tag-combo concepts, keep the ones farthest from any real game.
Usage: python find_gaps.py games.json out.json  (games = platform-agnostic records)"""
import json, sys, random, itertools, collections, numpy as np
from fastembed import TextEmbedding
random.seed(7)
games = [g for g in json.load(open(sys.argv[1])) if g.get("type") in (None, "game") and (g.get("description") or g.get("tags"))]
def text(g): return f"Tags: {', '.join(g['tags'][:12])}. Genres: {', '.join(g['genres'])}. {g['description']}"
m = TextEmbedding("BAAI/bge-small-en-v1.5")
E = np.load(sys.argv[2] + ".emb.npy")


# catalog density: mean cosine distance to 10 nearest neighbours
def knn(Q, k, B=500):
    I, V = [], []
    for a in range(0, len(Q), B):
        S = Q[a:a+B] @ E.T; idx = np.argpartition(-S, k, axis=1)[:, :k]
        s = np.take_along_axis(S, idx, 1); o = np.argsort(-s, 1)
        I.append(np.take_along_axis(idx, o, 1)); V.append(np.take_along_axis(s, o, 1))
    return np.vstack(I), np.vstack(V)
# tag stats
tc = collections.Counter(t for g in games for t in g["tags"][:12])
pc = collections.Counter(p for g in games for p in itertools.combinations(sorted(g["tags"][:12]), 2))
vocab = [t for t, c in tc.most_common(350) if c >= 15]
cands = set()
while len(cands) < 8000:
    combo = tuple(sorted(random.sample(vocab, 3)))
    pairs = list(itertools.combinations(combo, 2))
    # plausible: every pair seen at least twice, but whole triple never in one game's tags
    if all(pc[p] >= 2 for p in pairs): cands.add(combo)
cands = list(cands)
_cs = set(cands); tripseen = set(t for g in games for t in itertools.combinations(sorted(g["tags"][:12]), 3) if t in _cs)
cands = [c for c in cands if c not in tripseen]
Q = np.array(list(m.embed([f"Tags: {', '.join(c)}." for c in cands], batch_size=256)), dtype=np.float32)
Q /= np.linalg.norm(Q, axis=1, keepdims=True)
# baseline: same kind of tag-only query for real games, to calibrate distances
base = np.array(list(m.embed([f"Tags: {', '.join(g['tags'][:3])}." for g in random.sample(games, 1500)])), dtype=np.float32)
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
