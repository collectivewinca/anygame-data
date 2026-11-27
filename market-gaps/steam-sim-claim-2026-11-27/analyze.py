"""Test the 'ugly spreadsheet sims' claim against the AnyGame Steam catalog.

Usage: python analyze.py games.json out.json [--list-prices older_games.json]

games.json = collectivewin/steam-catalog-scraper records (platform-agnostic shape).
--list-prices: an older snapshot; per app we use max(old, new) price as a list-price proxy,
because the scraper stores Steam's *current* price (price_overview.final), which is
discounted during seasonal sales.

Revenue is an ESTIMATE, never sales data:
  est. gross (USD) = total Steam reviews x M x list price
  M = 20 (low) / 30 (mid) / 60 (high) copies per review, the range GameDiscoverCo
  reported for post-2020 Steam games (Carless, 3 Aug 2020 and 14 Nov 2022).
  This ignores discounts, regional pricing, refunds and Steam's cut, so it reads high
  for heavily-discounted games and low for older games (pre-2017 multiples were ~74).
"""
import json, sys, re, statistics, collections, datetime as dt

M = {"low": 20, "mid": 30, "high": 60}
TOPN = 10  # a game belongs to a bucket if the tag is in its top-10 user tags (SteamSpy order)
BUCKETS = {
    "Automation / factory": ["Automation"],
    "Colony sim": ["Colony Sim"],
    "Management / tycoon": ["Management", "Resource Management", "Economy", "Capitalism", "City Builder"],
    "Idle / incremental": ["Idler", "Clicker", "Incremental"],
    "2D platformer": ["2D Platformer"],
    "Metroidvania": ["Metroidvania"],
    "Story-rich / narrative": ["Story Rich"],
    "Visual novel": ["Visual Novel"],
    "Puzzle": ["Puzzle"],
}
SIM = ["Automation / factory", "Colony sim", "Management / tycoon", "Idle / incremental"]
BIG_PUBS = {"electronic arts", "ubisoft", "sega", "square enix", "2k", "bandai namco entertainment",
            "paradox interactive", "devolver digital", "thq nordic", "team17", "tinybuild", "kwalee",
            "raw fury", "annapurna interactive", "focus entertainment", "nacon", "microids", "playway s.a.",
            "curve games", "humble games", "frontier developments", "kepler interactive", "hooded horse",
            "koei tecmo games co., ltd.", "capcom", "xbox game studios", "sony interactive entertainment",
            "warner bros. games", "activision", "bethesda softworks", "deep silver", "krafton, inc.",
            "nexon", "netease games", "tencent games", "505 games", "plaion", "astragon entertainment",
            "untold tales", "coffee stain publishing", "playstack", "fireshine games", "no more robots", "landfall publishing"}
TODAY = dt.date(2026, 11, 27)

def rdate(s):
    if not s: return None
    s = s.strip().replace("Sept", "Sep")
    for f in ("%b %d, %Y", "%d %b, %Y", "%B %d, %Y", "%d %B, %Y", "%b %Y", "%B %Y", "%Y"):
        try: return dt.datetime.strptime(s, f).date()
        except ValueError: pass
    return None  # e.g. 'Coming soon', 'Q3 2025', non-English dates

def pct(xs, q):
    xs = sorted(xs)
    if not xs: return None
    k = (len(xs) - 1) * q; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def main():
    args = sys.argv[1:]
    old = {}
    if "--list-prices" in args:
        i = args.index("--list-prices"); old = {g["id"]: g.get("priceCents") for g in json.load(open(args[i + 1]))}
        args = args[:i] + args[i + 2:]
    games = json.load(open(args[0]))
    pubcount = collections.Counter(p.lower() for g in games for p in (g.get("publishers") or []))
    rows, discounted = [], 0
    for g in games:
        if g.get("type") not in ("game", None) or g.get("comingSoon"): continue
        new = g.get("priceCents") or 0
        price = max(new, old.get(g["id"]) or 0) if old else new
        if old and (old.get(g["id"]) or 0) > new: discounted += 1
        if g.get("isFree") or price <= 0: continue  # paid games only (F2P revenue can't be estimated from reviews)
        r = g.get("reviews") or {}
        tot = r.get("total") or 0
        tags = g.get("tags") or []
        pubs = [p for p in (g.get("publishers") or []) if p]
        devs = [d for d in (g.get("developers") or []) if d]
        selfpub = bool(pubs) and all(p in devs for p in pubs)
        major = any(p.lower() in BIG_PUBS or pubcount[p.lower()] >= 40 for p in pubs) and not selfpub
        rows.append({"id": g["id"], "title": g["title"], "url": g["url"], "image": g.get("image"),
                     "price": price / 100, "reviews": tot, "score": r.get("score"), "tags": tags[:TOPN],
                     "date": rdate(g.get("releaseDate")), "dev": devs, "pub": pubs, "selfpub": selfpub, "major": major,
                     "owners": g.get("owners"),
                     "est": {k: tot * m * price / 100 for k, m in M.items()},
                     "buckets": [b for b, ts in BUCKETS.items() if any(t in tags[:TOPN] for t in ts)]})
    out = {"paidGames": len(rows), "discountedVsOldSnapshot": discounted, "multipliers": M, "topN": TOPN}

    def dist(rs):
        if not rs: return None
        d = {"n": len(rs), "medianReviews": pct([r["reviews"] for r in rs], .5)}
        for k in M:
            e = [r["est"][k] for r in rs]
            d[k] = {"median": pct(e, .5), "p25": pct(e, .25), "p75": pct(e, .75),
                    "shareUnder10k": sum(x < 10_000 for x in e) / len(e),
                    "shareOver1M": sum(x >= 1_000_000 for x in e) / len(e)}
        return d

    # (a) whole paid catalog + the 2019 cohort used by Zukowski / VG Insights
    out["a_allPaid"] = dist(rows)
    out["a_cohort2019"] = dist([r for r in rows if r["date"] and r["date"].year == 2019])

    # bucket comparison
    comp = {}
    for b in BUCKETS:
        rs = [r for r in rows if b in r["buckets"]]
        rs100 = [r for r in rs if r["reviews"] >= 100]
        sc = [r["score"] for r in rs100 if r["score"] is not None]
        comp[b] = {"n": len(rs), "share100plus": len(rs100) / len(rs) if rs else None,
                   "medianReviews": pct([r["reviews"] for r in rs], .5),
                   "medianPrice": pct([r["price"] for r in rs], .5),
                   "estMedianAll": {k: pct([r["est"][k] for r in rs], .5) for k in M},
                   "estMedian100plus": {k: pct([r["est"][k] for r in rs100], .5) for k in M},
                   "n100plus": len(rs100),
                   "medianScore100plus": pct(sc, .5),
                   "share85plus100plus": sum(s >= .85 for s in sc) / len(sc) if sc else None}
    simrows = [r for r in rows if set(r["buckets"]) & set(SIM)]
    s100 = [r for r in simrows if r["reviews"] >= 100]
    sc = [r["score"] for r in s100 if r["score"] is not None]
    comp["ALL SIM (4 buckets)"] = {"n": len(simrows), "share100plus": len(s100) / len(simrows),
        "medianReviews": pct([r["reviews"] for r in simrows], .5), "medianPrice": pct([r["price"] for r in simrows], .5),
        "estMedianAll": {k: pct([r["est"][k] for r in simrows], .5) for k in M},
        "estMedian100plus": {k: pct([r["est"][k] for r in s100], .5) for k in M}, "n100plus": len(s100),
        "medianScore100plus": pct(sc, .5), "share85plus100plus": sum(s >= .85 for s in sc) / len(sc)}
    a100 = [r for r in rows if r["reviews"] >= 100]; sc = [r["score"] for r in a100 if r["score"] is not None]
    comp["ALL PAID GAMES"] = {"n": len(rows), "share100plus": len(a100) / len(rows),
        "medianReviews": pct([r["reviews"] for r in rows], .5), "medianPrice": pct([r["price"] for r in rows], .5),
        "estMedianAll": {k: pct([r["est"][k] for r in rows], .5) for k in M},
        "estMedian100plus": {k: pct([r["est"][k] for r in a100], .5) for k in M}, "n100plus": len(a100),
        "medianScore100plus": pct(sc, .5), "share85plus100plus": sum(s >= .85 for s in sc) / len(sc)}
    out["comparison"] = comp

    # (b) rank every tag with >=150 paid games at 100+ reviews by median est. gross (mid)
    bytag = collections.defaultdict(list)
    for r in a100:
        for t in r["tags"]: bytag[t].append(r["est"]["mid"])
    rank = sorted(((t, len(v), pct(v, .5)) for t, v in bytag.items() if len(v) >= 150), key=lambda x: -x[2])
    out["b_tagRank100plus"] = [{"tag": t, "n": n, "medianMid": m} for t, n, m in rank]

    # (c) 300-2,000 reviews
    band = [r for r in rows if 300 <= r["reviews"] <= 2000]
    out["c_band300to2000"] = {"all": dist(band), "sim": dist([r for r in band if set(r["buckets"]) & set(SIM)]),
                              "medianPrice": pct([r["price"] for r in band], .5)}

    # (d) positive share; playtime is NOT in the dataset
    out["d_playtimeInDataset"] = False

    # shortlist: screenshot filter
    cut = TODAY - dt.timedelta(days=548)
    sl = [r for r in simrows if r["date"] and cut <= r["date"] <= TODAY and 300 <= r["reviews"] <= 2000
          and (r["score"] or 0) >= .85 and not r["major"]]
    sl.sort(key=lambda r: -r["reviews"])
    out["shortlist"] = [{k: (str(v) if k == "date" else v) for k, v in r.items()} for r in sl]
    out["shortlistCutoff"] = str(cut)
    json.dump(out, open(args[1], "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("paidGames", "discountedVsOldSnapshot")}))
    for b, v in comp.items():
        print(f"{b:24s} n={v['n']:6d} 100+={v['share100plus']:.1%} medRev={v['medianReviews']:.0f} $={v['medianPrice']:.2f} "
              f"estMed100+ mid=${v['estMedian100plus']['mid']:,.0f} pos85+={v['share85plus100plus']:.1%}")
    print("a all:", {k: (round(v['median']), round(v['shareUnder10k'], 3), round(v['shareOver1M'], 3)) for k, v in out['a_allPaid'].items() if k in M})
    print("a 2019:", out['a_cohort2019']['n'], {k: (round(v['median']), round(v['shareUnder10k'], 3), round(v['shareOver1M'], 3)) for k, v in out['a_cohort2019'].items() if k in M})
    print("b top tags:", [(x['tag'], round(x['medianMid'])) for x in out['b_tagRank100plus'][:15]])
    print("c:", {k: (round(v['median']), round(v['p25']), round(v['p75'])) for k, v in out['c_band300to2000']['all'].items() if k in M})
    print("shortlist:", len(sl), [(r['title'], r['reviews'], r['pub']) for r in sl[:40]])

if __name__ == "__main__":
    main()
