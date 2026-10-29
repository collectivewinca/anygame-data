# Roblox (experiences)

Scraped 2026-10-28 (ET) via `collectivewin/roblox-experiences-scraper ([aar#56](https://github.com/collectivewinca/apify-actor-replacements/pull/56))` (Apify id [`tw3gPMN3uWG0c3ray`](https://console.apify.com/actors/tw3gPMN3uWG0c3ray), build 0.1.1).

## Source
Discovery: `apis.roblox.com/explore-api/v1/get-sorts` (locations all/us/gb/br/de/jp/ph/mx, 15 sort pages each) + `apis.roblox.com/search-api/omni-search` (140 keywords x up to 5 pages of 40). Detail: `games.roblox.com/v1/games` (50 universeIds/call). Schema: `platform: roblox`, `type: experience`, `id` = universeId, `placeId` = root place. Price = Robux paid access only (null = free to join); game passes/dev products are not price.

## Batches
| Batch | Run | Dataset | Items | USD |
|---|---|---|---|---|
| Smoke | [`pciS2DqUgI9wgvIdR`](https://console.apify.com/view/runs/pciS2DqUgI9wgvIdR) | `Wa4LJ5vYmIT9f08ZI` | 626 | ~$0.004 |
| Full | [`tPDrVwDaJdi4h3bCu`](https://console.apify.com/view/runs/tPDrVwDaJdi4h3bCu) | `br1sPU8eCBUvfZ9pI` | 11,050 | ~$0.132 (aborted by budget guard; data kept) |

Unique: **11,050** of 11,387 discovered (10,975 free to join / 74 paid access / 1 unknown). Search got many HTTP 429s; next run use concurrency 2, delay >=1s.

## Tags / gaps / brief
- `tools/roblox/derive_tags.py` — 99.9% >=1 tag, avg 4.3 (genre_l1/l2 + search keyword hits + text keywords).
- `tools/roblox/find_gaps.py` (bge-small-en-v1.5, chunked kNN): 4,020 candidates -> 40 gaps; baseline nnSim p5 0.828.
- Idea brief (draft): https://quiet-falcon-9yw7.here.now/
