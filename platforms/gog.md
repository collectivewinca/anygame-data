# GOG

Scraped 2026-10-28 (ET) via `collectivewin/gog-games-scraper` (Apify id [`5WeGrFRbrMQGPkgwg`](https://console.apify.com/actors/5WeGrFRbrMQGPkgwg), build 0.1.1).

## Source
Public `https://catalog.gog.com/v1/catalog` (`productType=in:game`, page+limit=48). No login, no per-game detail fetch. Each listing already carries genres, GOG tags, features, reviewsRating/reviewsCount, ratings, list/sale price, developer/publisher, OS, release date, covers, storeLink.

## Batches
| Batch | Run | Dataset | Items | Notes |
|---|---|---|---|---|
| Smoke US | [`qhZLMUHRDXheX9IN4`](https://console.apify.com/view/runs/qhZLMUHRDXheX9IN4) | `jMl1ydwWEbVinXxIN` | 96 | maxGames 60 |
| US | [`WQ8lhMbBe6zZItIO8`](https://console.apify.com/view/runs/WQ8lhMbBe6zZItIO8) | `aour8CAGOZ5s0BcGM` | 6,569 | full US |
| GB+CA | [`EbevAfQmPGzDDMmM6`](https://console.apify.com/view/runs/EbevAfQmPGzDDMmM6) | `cjtCrq3XWBu1UOSM6` | 0 | skip US; all seen |
| DE+FR | [`p9eaKfv6afed6G7wq`](https://console.apify.com/view/runs/p9eaKfv6afed6G7wq) | `nCiCKlcsBTA5cK3HB` | 2 | skip US |
| JP+AU | [`2Q5jrDJd5fAVZ8pZP`](https://console.apify.com/view/runs/2Q5jrDJd5fAVZ8pZP) | `f4ajcLifd6sAEuHlJ` | 1 | skip US+DE/FR |

Merged unique: **6,572** (435 free / 5,832 paid / 305 unknown). Price = list `baseMoney` only.

## Tags / gaps / brief
- Offline `tools/gog/derive_tags.py` — 100% ≥1 tag, avg 12.1 (GOG catalog tags + genres + title keywords).
- Gap engine `tools/gog/find_gaps.py` (bge-small-en-v1.5): 3,114 candidates → 40 ranked gaps; baseline nnSim p5 0.873.
- Idea brief (draft): https://zingy-birch-r95j.here.now/

Actor PR: [apify-actor-replacements#54](https://github.com/collectivewinca/apify-actor-replacements/pull/54).
