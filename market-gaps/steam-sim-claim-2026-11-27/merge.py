"""Normalize: merge the page-by-page steam-catalog-scraper datasets into one games.json.

Usage: python merge.py manifest.json page_dir/ out_games.json [--fallback-tags old_games.json]
- Dedupes by Steam appid; prefers the record that has store data (type) and user tags.
- Records whose Steam appdetails call failed (no `type`) take store fields (type, dates, price, publisher, art)
  from the older snapshot; fresh SteamSpy reviews/tags are kept.
- Records with no SteamSpy tags (SteamSpy appdetails failed) can take tags from an older
  snapshot via --fallback-tags; the count is printed and written to out_games.json.meta.json.
Records keep the scraper's platform-agnostic shape (platform, id, title, tags, reviews, url, image, ...).
"""
import json, sys, os
man, pdir, outp = sys.argv[1:4]
fb = {}
if "--fallback-tags" in sys.argv:
    fb = {g["id"]: g for g in json.load(open(sys.argv[sys.argv.index("--fallback-tags") + 1]))}
man = json.load(open(man))
best, runs = {}, []
def q(g): return (1 if g.get("type") else 0) + (1 if g.get("tags") else 0)
for p, rs in sorted(man.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 10**6):
    for r in rs:
        if r["status"] not in ("SUCCEEDED", "ABORTED") or not r.get("items"): continue
        runs.append({"page": p, **r})
        for g in json.load(open(os.path.join(pdir, r["dataset"] + ".json"))):
            if g["id"] not in best or q(g) > q(best[g["id"]]): best[g["id"]] = g
filled = storefill = 0
STORE_KEYS = ("type", "title", "description", "about", "genres", "categories", "developers", "publishers", "releaseDate",
              "comingSoon", "isFree", "priceCents", "currency", "image")
for g in best.values():
    if not g.get("type") and g["id"] in fb and fb[g["id"]].get("type"):
        # Steam appdetails failed this time (proxy 429s): keep fresh SteamSpy reviews/tags, take store fields from Oct
        for k in STORE_KEYS: g[k] = fb[g["id"]].get(k)
        g["storeFrom"] = "2026-10-25 snapshot"; storefill += 1
    if not g.get("tags") and g["id"] in fb and fb[g["id"]].get("tags"):
        g["tags"], g["tagVotes"], g["tagsFrom"] = fb[g["id"]]["tags"], fb[g["id"]].get("tagVotes", {}), "2026-10-25 snapshot"
        filled += 1
games = list(best.values())
json.dump(games, open(outp, "w"))
meta = {"records": len(games), "runs": runs, "tagsFilledFromOldSnapshot": filled, "storeFieldsFilledFromOldSnapshot": storefill,
        "noTags": sum(1 for g in games if not g.get("tags")), "noStoreData": sum(1 for g in games if not g.get("type"))}
json.dump(meta, open(outp + ".meta.json", "w"), indent=1)
print({k: v for k, v in meta.items() if k != "runs"}, "runs used:", len(runs))
