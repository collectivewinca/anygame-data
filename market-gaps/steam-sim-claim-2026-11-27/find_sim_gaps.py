"""Gap engine, sim slice. Same method as market-gaps/steam-2026-10-25/find_gaps*.py, but every
candidate triple must contain at least one sim tag (Automation, Colony Sim, Management, ...).

  candidate = tag triple where every pair appears in >=2 games but the triple never appears
              in any game's top-12 tags (checked against the FULL catalog, not just sims)
  rank      = lowest nnSim: cosine similarity of the triple ("Tags: a, b, c.") to its nearest real
              game, embedded with BAAI/bge-small-en-v1.5 (fastembed). Lower = emptier.
Empty != sellable: nearest real games are novelty evidence, not demand.

Usage: python find_sim_gaps.py games.json out.json [--emb existing.emb.npy]
Embeddings are computed in chunks of 4,000 (avoids the full-catalog OOM) and cached to out.json.emb.npy.
"""
import json, sys, random, itertools, collections, numpy as np
from fastembed import TextEmbedding
random.seed(7)
SIM_TAGS = ["Automation", "Colony Sim", "Management", "Resource Management", "Economy", "Capitalism",
            "City Builder", "Idler", "Clicker", "Incremental"]
args = sys.argv[1:]
emb_path = None
if "--emb" in args:
    i = args.index("--emb"); emb_path = args[i + 1]; args = args[:i] + args[i + 2:]
reuse = None
if "--reuse" in args:  # --reuse old_games.json old.emb.npy : reuse vectors whose embedded text is unchanged
    i = args.index("--reuse"); reuse = (args[i + 1], args[i + 2]); args = args[:i] + args[i + 3:]
games = [g for g in json.load(open(args[0])) if g.get("type") in (None, "game") and (g.get("description") or g.get("tags"))]
def text(g): return f"Tags: {', '.join(g['tags'][:12])}. Genres: {', '.join(g['genres'])}. {g['description']}"
m = TextEmbedding("BAAI/bge-small-en-v1.5")
if emb_path:
    E = np.load(emb_path)
else:
    texts = [text(g) for g in games]
    E = np.zeros((len(games), 384), dtype=np.float32); todo = list(range(len(games)))
    if reuse:
        og = [g for g in json.load(open(reuse[0])) if g.get("type") in (None, "game") and (g.get("description") or g.get("tags"))]
        OE = np.load(reuse[1], mmap_mode="r"); assert len(OE) == len(og)
        old = {text(g): k for k, g in enumerate(og)}
        todo = []
        for k, t in enumerate(texts):
            if t in old: E[k] = OE[old[t]]
            else: todo.append(k)
        print("reused", len(games) - len(todo), "to embed", len(todo), flush=True)
    for a in range(0, len(todo), 4000):
        idx = todo[a:a + 4000]
        x = np.array(list(m.embed([texts[k] for k in idx], batch_size=128)), dtype=np.float32)
        E[idx] = x / np.linalg.norm(x, axis=1, keepdims=True); print("embedded", a + len(idx), flush=True)
    np.save(args[1] + ".emb.npy", E)
assert len(E) == len(games), (len(E), len(games))

def knn(Q, k, B=500):
    I, V = [], []
    for a in range(0, len(Q), B):
        S = Q[a:a+B] @ E.T; idx = np.argpartition(-S, k, axis=1)[:, :k]
        s = np.take_along_axis(S, idx, 1); o = np.argsort(-s, 1)
        I.append(np.take_along_axis(idx, o, 1)); V.append(np.take_along_axis(s, o, 1))
    return np.vstack(I), np.vstack(V)

tc = collections.Counter(t for g in games for t in g["tags"][:12])
pc = collections.Counter(p for g in games for p in itertools.combinations(sorted(g["tags"][:12]), 2))
vocab = [t for t, c in tc.most_common(350) if c >= 15]
sims = [t for t in SIM_TAGS if t in vocab]
cands = set()
for s in sims:
    others = [t for t in vocab if t != s]
    for a, b in itertools.combinations(others, 2):
        c = tuple(sorted((s, a, b)))
        if all(pc[p] >= 2 for p in itertools.combinations(c, 2)): cands.add(c)
allc = len(cands)
seen = set(t for g in games for t in itertools.combinations(sorted(g["tags"][:12]), 3) if t in cands)
cands = sorted(c for c in cands if c not in seen)
unseen = len(cands)
if len(cands) > 20000: cands = random.sample(cands, 20000)
Q = np.array(list(m.embed([f"Tags: {', '.join(c)}." for c in cands], batch_size=256)), dtype=np.float32)
Q /= np.linalg.norm(Q, axis=1, keepdims=True)
base = np.array(list(m.embed([f"Tags: {', '.join(g['tags'][:3])}." for g in random.sample(games, 1500)])), dtype=np.float32)
base /= np.linalg.norm(base, axis=1, keepdims=True)
_, bs = knn(base, 3); thr = np.percentile(bs[:, 0], 5)
idx, simv = knn(Q, 3)
order = np.argsort(simv[:, 0])
out, used = [], collections.Counter()
for i in order:
    c = cands[i]
    # diversity: a non-sim tag once, a sim tag at most 3 times
    if any(used[t] >= (3 if t in SIM_TAGS else 1) for t in c): continue
    for t in c: used[t] += 1
    out.append({"tags": c, "nnSim": float(simv[i, 0]), "pairCounts": {"+".join(p): pc[p] for p in itertools.combinations(c, 2)},
                "nearest": [{"title": games[j]["title"], "url": games[j]["url"], "sim": float(s), "tags": games[j]["tags"][:6],
                             "reviews": (games[j].get("reviews") or {}).get("total")} for j, s in zip(idx[i], simv[i])]})
    if len(out) >= 40: break
json.dump({"games": len(games), "simTags": sims, "plausibleTriples": allc, "unseenTriples": unseen, "rankedCandidates": len(cands),
           "baselineNnSimP5": float(thr), "gaps": out}, open(args[1], "w"), indent=1)
print(len(games), allc, unseen, len(cands), thr)
for o in out[:15]: print(o["tags"], round(o["nnSim"], 3), [n["title"] for n in o["nearest"]])
