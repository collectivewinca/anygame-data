"""Build the locked hub brief: index.html + robots.txt + official store art in img/.
Inputs (this folder): analysis.json (Steam claims), stores.json (all stores + timeline), sim-gaps.json,
verdicts.json (hand-written plain-language text, numbers come from the JSON files).
Usage: python build_brief.py outdir"""
import json, sys, html, urllib.request, pathlib, hashlib
HERE = pathlib.Path(__file__).parent
out = pathlib.Path(sys.argv[1]); (out / "img").mkdir(parents=True, exist_ok=True)
A = json.load(open(HERE / "analysis.json")); ST = json.load(open(HERE / "stores.json"))
G = json.load(open(HERE / "sim-gaps.json")); V = json.load(open(HERE / "verdicts.json"))
e = html.escape
NAMES = {"steam": "Steam", "app-store": "App Store", "google-play": "Google Play", "playstation": "PlayStation Store", "xbox": "Xbox Store",
         "nintendo": "Nintendo eShop", "epic": "Epic Games Store", "gog": "GOG", "itch": "itch.io", "roblox": "Roblox"}
def money(x):
    if x is None: return "–"
    return f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1e3:,.0f}k" if x >= 1e3 else f"${x:,.0f}"
def num(x): return "–" if x is None else f"{x:,.0f}"
def pc(x): return "–" if x is None else f"{x:.0%}"
def rng(d): return f"{money(d['low'])}–{money(d['high'])}"
def art(url):
    if not url: return None
    name = hashlib.sha1(url.encode()).hexdigest()[:16] + ".jpg"; p = out / "img" / name
    if not p.exists():
        try: p.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
        except Exception as ex: print("art fail", url[:80], ex); return None
    return f"img/{name}"
def card(title, url, img, lines):
    src = art(img); im = f"<img src='{src}' alt='{e(title)} store art' loading='lazy'>" if src else "<div class='noimg'>no store art in data</div>"
    return f"<a class='game' href='{e(url)}' target='_blank' rel='noopener'>{im}<div class='gn'><b>{e(title)}</b><br>{'<br>'.join(lines)}</div></a>"
def bars(tl, key, fmt, color="#2563eb", h=110):
    ys = [y for y in sorted(tl, key=int) if int(y) >= 2006]
    vals = [tl[y][key] or 0 for y in ys]; mx = max(vals) or 1; w = 26
    s = [f"<svg viewBox='0 0 {len(ys)*w+10} {h+34}' class='chart' role='img'>"]
    for i, (y, v) in enumerate(zip(ys, vals)):
        bh = v / mx * h; x = 5 + i * w
        s.append(f"<rect x='{x}' y='{h-bh+12}' width='{w-6}' height='{bh}' fill='{color}'><title>{y}: {fmt(v)}</title></rect>")
        s.append(f"<text x='{x+(w-6)/2}' y='{h+26}' font-size='8' text-anchor='middle'>{str(y)[2:]}</text>")
        if v == mx or i == len(ys) - 1: s.append(f"<text x='{x+(w-6)/2}' y='{h-bh+9}' font-size='8' text-anchor='middle'>{fmt(v)}</text>")
    return "".join(s) + "</svg>"
css = open(HERE / "brief.css").read()
h = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>{e(V['title'])}</title><style>{css}</style></head><body><div class="wrap">
<p class="kicker">AnyGame brief · {e(V['date'])} · private draft</p><h1>{e(V['title'])}</h1><p class="lede">{V['lede']}</p>
<nav class='toc'>{" · ".join(f"<a href='#{a}'>{t}</a>" for a, t in [("bottom","Bottom line"),("claims","The claims"),("stores","10 stores"),("timeline","Timeline"),("shortlist","Shortlist"),("gaps","Gaps"),("method","Method & runs"),("caveats","Caveats")])}</nav>
<div class="verdict" id="bottom"><p class="kicker">Bottom line</p>{V['bottomLine']}</div>"""]
h.append(f"<h2>Where the claim comes from</h2>{V['origin']}")
h.append("<h2 id='claims'>The four claims, tested on Steam</h2><table><tr><th>Claim</th><th>Verdict</th><th>What our data shows</th></tr>")
for c in V["claims"]:
    h.append(f"<tr><td>{c['claim']}</td><td><span class='pill {c['cls']}'>{e(c['verdict'])}</span></td><td>{c['evidence']}</td></tr>")
h.append("</table>")
h.append(f"<h3>Steam: sims next to other genres</h3>{V['compIntro']}<div class='scroll'><table><tr><th>Genre (tag in a game's top 10)</th><th>Paid games</th><th>Share with 100+ reviews</th><th>Median reviews</th><th>Median price</th><th>Est. median gross, all</th><th>Est. median gross, 100+ reviews</th><th>85%+ positive (100+ reviews)</th></tr>")
for b, v in A["comparison"].items():
    h.append(f"<tr{' class=hl' if b.startswith('ALL') else ''}><td>{e(b)}</td><td>{v['n']:,}</td><td>{pc(v['share100plus'])}</td><td>{v['medianReviews']:.0f}</td><td>${v['medianPrice']:.2f}</td><td>{rng(v['estMedianAll'])}</td><td>{rng(v['estMedian100plus'])}</td><td>{pc(v['share85plus100plus'])}</td></tr>")
h.append(f"</table></div><p class='meta'>{V['compNote']}</p>")
# cross-store
h.append(f"<h2 id='stores'>All 10 stores: does 'sim' do better?</h2>{V['storesIntro']}<div class='scroll'><table><tr><th>Store</th><th>Signal we have</th><th>Games</th><th>Sims (share)</th><th>Median ratings: sim / other</th><th>100+ ratings: sim / other</th><th>Median score (100+): sim / other</th><th>Verdict</th></tr>")
for st, d in ST["stores"].items():
    s, o = d["sim"], d["other"]; vv = V["storeVerdicts"].get(st, {})
    rat = f"{num(s['medianRatings'])} / {num(o['medianRatings'])}" if s["rated"] else "no ratings"
    if st == "roblox": rat += f"<br><span class='muted'>visits {num(s.get('medianVisits'))} / {num(o.get('medianVisits'))}</span>"
    if st == "nintendo": rat = f"popularity rank {num(s.get('medianPopularityRank'))} / {num(o.get('medianPopularityRank'))} (lower = more popular)"
    sc = f"{pc(s['medianScore100plus'])} / {pc(o['medianScore100plus'])}" if s["medianScore100plus"] is not None else "–"
    h.append(f"<tr><td><a href='#store-{st}'>{NAMES[st]}</a></td><td>{e(d['signals'])}</td><td>{d['games']:,}</td><td>{s['n']:,} ({s['n']/d['games']:.1%})</td><td>{rat}</td>"
             f"<td>{pc(s['share100plus']) if s['rated'] else '–'} / {pc(o['share100plus']) if o['rated'] else '–'}</td><td>{sc}</td><td><span class='pill {vv.get('cls','na')}'>{e(vv.get('verdict','Can’t test'))}</span></td></tr>")
h.append(f"</table></div><p class='meta'>{V['storesNote']}</p>")
for st, d in ST["stores"].items():
    vv = V["storeVerdicts"].get(st, {}); run = V["runs"].get(st, "")
    h.append(f"<div class='store' id='store-{st}'><h3>{NAMES[st]}</h3><p>{vv.get('text','')}</p>"
             f"<p class='meta'>Sim tags used ({NAMES[st]} taxonomy): " + ", ".join(f"{e(t)} ({n:,})" for t, n in d["tagCounts"].items()) + f". Data: {run}</p>")
    if d["breakouts"]:
        h.append("<div class='games'>")
        for b in d["breakouts"][:6]:
            ln = [f"Released {b['year']}"]
            if b.get("ratings"): ln.append(f"{b['ratings']:,} ratings" + (f" · {b['score']:.0%}" if b.get('score') is not None else ""))
            if b.get("visits"): ln.append(f"{b['visits']:,} visits")
            if st == "nintendo" and b.get("popularityRank"): ln.append(f"eShop popularity rank {b['popularityRank']}")
            ln.append(f"<span class='muted'>{e(', '.join(b['simTags']))}</span>")
            h.append(card(b["title"], b["url"], b.get("image"), ln))
        h.append("</div>")
    h.append("</div>")
# timeline
stl = ST["stores"]["steam"]["timeline"]
h.append(f"<h2 id='timeline'>Timeline: how the sim category grew</h2>{V['timelineIntro']}"
         f"<div class='two'><div><p class='kicker'>Steam: sim releases per year (games still listed)</p>{bars(stl,'sim',lambda v:f'{v:,}')}</div>"
         f"<div><p class='kicker'>Steam: sims as a share of that year's releases</p>{bars(stl,'simShare',lambda v:f'{v:.1%}','#16a34a')}</div></div>")
h.append("<div class='scroll'><table><tr><th>Release year</th>" + "".join(f"<th>{NAMES[s]}</th>" for s in ST["stores"]) + "<th>All 10 combined</th></tr>")
for y in range(2010, 2027):
    cells = []
    for s, d in ST["stores"].items():
        t = d["timeline"].get(str(y)) or d["timeline"].get(y)
        cells.append(f"<td>{t['sim']:,} <span class='muted'>({t['simShare']:.0%})</span></td>" if t else "<td>–</td>")
    tots = [d["timeline"].get(str(y)) for d in ST["stores"].values()]; R = sum(t["releases"] for t in tots if t); S = sum(t["sim"] for t in tots if t)
    cells.append(f"<td><b>{S:,}</b> <span class='muted'>({S/R:.0%})</span></td>" if R else "<td>–</td>")
    h.append(f"<tr><td>{y}</td>{''.join(cells)}</tr>")
h.append(f"</table></div><p class='meta'>{V['timelineNote']}</p>")
h.append("<h3>Steam: median reviews by release year, sims vs everything else</h3><div class='scroll'><table><tr><th>Year</th><th>Sim releases</th><th>Median reviews, sims</th><th>Median reviews, other games</th></tr>")
for y in range(2010, 2027):
    t = stl.get(str(y)) or stl.get(y)
    if t: h.append(f"<tr><td>{y}</td><td>{t['sim']:,}</td><td>{num(t['simMedianRatings'])}</td><td>{num(t['otherMedianRatings'])}</td></tr>")
h.append("</table></div>")
h.append(f"<h3>Dated milestones for the idea</h3><table><tr><th>Date</th><th>What</th><th>Source</th></tr>")
for m in V["milestones"]:
    h.append(f"<tr><td>{e(m['date'])}</td><td>{m['what']}</td><td>{m['src']}</td></tr>")
h.append(f"</table><p class='meta'>{V['milestoneNote']}</p>")
# shortlist
sl = A["shortlist"]
h.append(f"<h2 id='shortlist'>The screenshot's filter, run on Steam: {len(sl)} games</h2>{V['shortIntro']}<div class='games'>")
for r in sl:
    h.append(card(r["title"], r["url"], r.get("image"), [f"{r['reviews']:,} reviews · {r['score']:.0%} positive · ${r['price']:.2f}",
              f"<span class='muted'>Released {e(str(r['date']))} · {e(', '.join(r['pub']) or '–')}{' (self-published)' if r['selfpub'] else ''}</span>",
              f"<span class='muted'>Est. gross {money(r['est']['low'])}–{money(r['est']['high'])}</span>"]))
h.append(f"</div><p class='meta'>{V['shortNote']}</p>")
h.append(f"<h2 id='gaps'>Ten empty sim combinations on Steam</h2>{V['gapIntro']}")
for i, gp in enumerate(G["gaps"][:10], 1):
    near = "; ".join(f"<a href='{e(n['url'])}' target='_blank' rel='noopener'>{e(n['title'])}</a>" + (f" ({n['reviews']:,} reviews)" if n.get('reviews') is not None else "") for n in gp["nearest"])
    pairs = ", ".join(f"{e(k.replace('+', ' + '))}: {v:,}" for k, v in gp["pairCounts"].items())
    h.append(f"<div class='gap'><span class='rank'>{i}</span><div><b>{e(' + '.join(gp['tags']))}</b> <span class='muted'>· closest match {gp['nnSim']:.3f}</span><br><span class='muted'>Games with each pair: {pairs}</span><br>Nearest real games: {near}</div></div>")
h.append(f"<p class='meta'>{V['gapNote']}</p>")
h.append(f"<h2>What this means for AnyGame</h2>{V['soWhat']}")
h.append(f"<h2 id='method'>Method and runs</h2>{V['method']}")
h.append(f"<h2 id='caveats'>Caveats</h2>{V['caveats']}<h2>Sources</h2>{V['sources']}<footer>{V['footer']}</footer></div></body></html>")
(out / "index.html").write_text("\n".join(h))
(out / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
print("wrote", out / "index.html")
