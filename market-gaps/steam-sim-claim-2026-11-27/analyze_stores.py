"""Cross-store test of the 'ugly sims' thesis + timeline. Usage:
  python analyze_stores.py out.json steam=games.json app-store=games.tagged.json google-play=... (any subset)
A game counts as 'sim' if any tag in SIM_MAP[store] is among its tags (Steam: top-10 user tags).
Every store's tags come from its own taxonomy (see SIM_MAP and platforms/*.md); keyword-derived tags
(PlayStation, Xbox, Nintendo, Epic, App Store) are noisier than Steam's user tags."""
import json, sys, re, statistics, collections, datetime as dt
SIM_MAP = {
 "steam": ["Automation", "Colony Sim", "Management", "Resource Management", "Economy", "Capitalism", "City Builder", "Idler", "Clicker", "Incremental"],
 "app-store": ["Idle", "Tycoon", "City Builder"],
 "google-play": ["Idle", "Idle RPG", "Management", "Tycoon", "Time management", "Business empire", "City Builder", "City-building", "Empire building", "Factory"],
 "playstation": ["Tycoon", "City Builder", "Idle"],
 "xbox": ["Tycoon", "City Builder", "Idle"],
 "nintendo": ["Tycoon", "City Builder", "Idle"],
 "epic": ["Tycoon", "City Builder", "Idle"],
 "gog": ["Management", "Resource Management", "Managerial", "City builder", "City Builder", "Economic", "Tycoon"],
 "itch": ["Idle", "Incremental", "Clicker", "Management", "City Builder", "Colony Sim", "Tycoon"],
 "roblox": ["Tycoon", "Incremental Simulator", "Idle", "Clicker", "Incremental", "City Builder"],
}
SIGNALS = {"steam": "Steam user reviews (count, % positive), price",
 "app-store": "App Store rating count + average stars (chart sample only), price",
 "google-play": "Play rating count + stars, install band (category-page sample only), price",
 "playstation": "PS Store star-rating count + average, price", "xbox": "Xbox rating count + average, price",
 "nintendo": "no ratings; eShop popularity rank, price", "epic": "no ratings or sales signal; price only",
 "gog": "GOG user-rating count + average (0-5), price", "itch": "no ratings (top-rated feed order only), price",
 "roblox": "likes/dislikes, visits, current players; free to play"}
def year(s):
    if not s: return None
    m = re.search(r"(19|20)\d\d", str(s))
    return int(m.group()) if m else None
def med(xs): return statistics.median(xs) if xs else None
def norm_score(store, s):
    if s is None: return None
    return s / 50 if store == "gog" else s / 100 if store == "roblox" else s
def main():
    outp = sys.argv[1]; res = {"simMap": SIM_MAP, "signals": SIGNALS, "stores": {}}
    for a in sys.argv[2:]:
        store, path = a.split("=", 1)
        games = [g for g in json.load(open(path)) if g.get("type") in (None, "game", "experience")]
        if store == "steam": games = [g for g in games if not g.get("comingSoon")]
        tags = lambda g: (g.get("tags") or [])[:10] if store == "steam" else (g.get("tags") or [])
        sim = set(SIM_MAP[store])
        rows = []
        for g in games:
            r = g.get("reviews") or {}
            rows.append({"g": g, "sim": bool(sim & set(tags(g))), "y": year(g.get("releaseDate")), "n": r.get("total") or 0,
                         "s": norm_score(store, r.get("score")), "price": (g.get("priceCents") or 0) / 100 if not g.get("isFree") else 0,
                         "visits": int(g.get("visits") or 0), "pop": g.get("popularityRank"), "inst": int(g.get("minInstalls") or 0)})
        def stats(rs):
            rated = [r for r in rs if r["n"]]
            r100 = [r for r in rs if r["n"] >= 100]
            sc = [r["s"] for r in r100 if r["s"] is not None]
            paid = [r["price"] for r in rs if r["price"] > 0]
            d = {"n": len(rs), "rated": len(rated), "medianRatings": med([r["n"] for r in rated]),
                 "share100plus": len(r100) / len(rs) if rs else None, "medianScore100plus": med(sc),
                 "share85plus100plus": sum(s >= .85 for s in sc) / len(sc) if sc else None,
                 "medianPaidPrice": med(paid), "sharePaid": len(paid) / len(rs) if rs else None}
            if store == "roblox": d["medianVisits"] = med([r["visits"] for r in rs])
            if store == "google-play": d["medianInstalls"] = med([r["inst"] for r in rs if r["inst"]])
            if store == "nintendo":
                ps = [int(r["pop"]) for r in rs if r["pop"] not in (None, "")]
                d["medianPopularityRank"] = med(ps)
            return d
        S = [r for r in rows if r["sim"]]; O = [r for r in rows if not r["sim"]]
        tl = {}
        for y in range(2006, 2027):
            ya = [r for r in rows if r["y"] == y]; ys = [r for r in ya if r["sim"]]
            if not ya: continue
            tl[y] = {"releases": len(ya), "sim": len(ys), "simShare": len(ys) / len(ya),
                     "simMedianRatings": med([r["n"] for r in ys if r["n"]]), "otherMedianRatings": med([r["n"] for r in ya if not r["sim"] and r["n"]])}
        key = (lambda r: r["visits"]) if store == "roblox" else (lambda r: -int(r["pop"]) if r["pop"] not in (None, "") else -10**9) if store == "nintendo" else (lambda r: r["n"])
        # breakouts: Steam needs a sim tag in the top 5 user tags; keyword-tagged stores drop platform launchers
        NOT_GAMES = re.compile(r"^(roblox|fortnite|pso2|monopoly go)", re.I)
        cand = [r for r in S if r["y"] and not NOT_GAMES.match(r["g"]["title"] or "")
                and (store != "steam" or sim & set((r["g"].get("tags") or [])[:5]))]
        brk = sorted(cand, key=key, reverse=True)[:8] if store not in ("epic", "itch") else []
        res["stores"][store] = {"games": len(rows), "signals": SIGNALS[store], "sim": stats(S), "other": stats(O), "timeline": tl,
            "tagCounts": {t: sum(1 for r in rows if t in tags(r["g"])) for t in SIM_MAP[store]},
            "breakouts": [{"title": r["g"]["title"], "url": r["g"]["url"], "image": r["g"].get("image"), "year": r["y"], "release": r["g"].get("releaseDate"),
                           "ratings": r["n"], "score": r["s"], "visits": r["visits"] or None, "popularityRank": r["pop"],
                           "simTags": [t for t in tags(r["g"]) if t in sim]} for r in brk]}
        s, o = res["stores"][store]["sim"], res["stores"][store]["other"]
        print(f"{store:12s} n={len(rows):6d} sim={s['n']:5d} ({s['n']/len(rows):.1%}) medR sim={s['medianRatings']} oth={o['medianRatings']} "
              f"100+ sim={s['share100plus']:.1%} oth={o['share100plus']:.1%} score sim={s['medianScore100plus']} oth={o['medianScore100plus']}")
    json.dump(res, open(outp, "w"), indent=1, default=str)
main()
