# Sim-thesis check + 10-store refresh (2026-11-27)

Tests the froessell / Gemini "ugly spreadsheet sims" claim (https://x.com/froessell/status/2126319483279093926, posted 2026-11-27 9:17 AM ET) against fresh scrapes of all 10 storefronts, with a sim-category timeline.

- Brief (locked, noindex, off-profile): https://sable-ravine-hc34.here.now/ — source `index.html` (store art in `img/` is not committed; `build_brief.py` re-downloads it).
- Verdicts on Steam: (a) median paid game earnings — Supported; (b) sims highest median revenue — Partly (colony/city/factory high, idle/clicker last of 206 tags); (c) 300–2,000 reviews ≈ $150k–$800k — Partly; (d) playtime forgives ugly art — can't test (no playtime field), and sims are less often 85%+ positive.

## Runs
- Steam: `collectivewin/steam-catalog-scraper` 0.1.3, same input as Oct run FwiVYa7CgChoV7Tpc. SteamSpy's `request=all` listing kept failing ("Too many connections"), so the first same-input run `9bBfwOliPCfx0mQeK` (dataset `w2KKxCu9X9J1mXpkV`) stopped at 2,292 apps. Refreshed with 24 runs of the same actor/build: page-by-page runs (`startPage=p, maxPages=1`) plus runs resumed through the actor's own STATE record with the Oct app list + 45 box-fetched SteamSpy pages (enrich only). All ids: `refresh/runs-steam-2026-11-27.json`. Merged: 83,468 apps (`steam-catalog-2026-11-27.meta.json`); 8,709 apps whose Steam appdetails call failed keep fresh SteamSpy reviews/tags with store fields from the Oct snapshot.
- Other 9 stores: every Oct production batch re-run with identical input/build/memory/timeout; `skipDatasetIds` remapped to the new datasets. Old → new run/dataset ids: `refresh/runs-other-stores-2026-11-27.json`. Normalized with each store's `tools/<store>/merge.py` (+ `fix_free.py`) + `derive_tags.py` (`refresh/normalize_all.py`).
- Apify spend: about $11.3 Steam (parallel 4 GB runs) + $1.9 other stores.

## Files
| File | What |
|---|---|
| `merge.py` | Steam: merge page datasets, dedupe, Oct fallback for failed appdetails |
| `analyze.py` | Steam claims (a)–(d), genre comparison, screenshot-filter shortlist → `analysis.json` |
| `find_sim_gaps.py` | Gap engine limited to triples with a sim tag (bge-small-en-v1.5; reuses unchanged Oct embeddings) → `sim-gaps.json` |
| `analyze_stores.py` | Per-store sim mapping (`SIM_MAP`), sim vs other on each store's signals, timeline, breakouts → `stores.json` |
| `verdicts.py` → `verdicts.json` | Plain-language brief text; numbers read from the JSON outputs |
| `build_brief.py`, `brief.css` | Builds `index.html` + `robots.txt` |
| `refresh/` | Run drivers and run manifests |

Revenue = reviews × 20/30/60 copies per review (GameDiscoverCo 2020/2022 surveys) × list price; estimates, not sales. Empty ≠ sellable. Catalog JSON and `.npy` embeddings are not committed (rebuild from the datasets).
