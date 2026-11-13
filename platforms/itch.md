# itch.io

Scraped 2026-10-28 (ET) via `collectivewin/itch-games-scraper` (Apify id [`l7yIXTWjTL5hNJlzs`](https://console.apify.com/actors/l7yIXTWjTL5hNJlzs), build 0.1.1).

## Source
Public browse RSS `https://itch.io/games/top-rated/tag-<tag>.xml?page=N` (36/page), 110 tag feeds × up to 15 pages. No login, no keyshops. Each item: title, short description, price/fullPrice/currency (USD), genre (title bracket), platforms, publish/update date, cover, URL. id = `author/slug`. Sample, not census (itch has 1M+ projects).

## Batches
| Batch | Run | Dataset | Items | USD |
|---|---|---|---|---|
| Smoke (2 tags × 2 pages) | [`4ezvrDIyQv0VL2AZM`](https://console.apify.com/view/runs/4ezvrDIyQv0VL2AZM) | `DLHk3opck2c6xQoHc` | 142 | ~$0.001 |
| Full (110 tags × 15 pages) | [`cVDQAhlsUJxNTK8jo`](https://console.apify.com/view/runs/cVDQAhlsUJxNTK8jo) | `cn6ttImygXhMUQMxw` | 30,287 | ~$0.026 |

Unique: **30,287** (26,987 free / 3,300 paid / 0 unknown; 923 on sale, priced at fullPrice). Single run, no merge step needed.

## Tags / gaps / brief
- `tools/itch/derive_tags.py` — 100% ≥1 tag, avg 2.9 (tag-feed membership + genre + keywords). Thin; expect false gaps.
- `tools/itch/find_gaps.py` (bge-small-en-v1.5, chunked kNN): 4,525 candidates → 30 gaps; baseline nnSim p5 0.902.
- Idea brief (draft): https://mystic-aurora-q32t.here.now/

Actor PR: [apify-actor-replacements#55](https://github.com/collectivewinca/apify-actor-replacements/pull/55).
