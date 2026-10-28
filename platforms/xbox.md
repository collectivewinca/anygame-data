# Xbox / Microsoft Store — catalog runs, merge, tags, gaps

Status: **draft** (2026-10-28 ET). Actor `collectivewin/xbox-games-scraper` (id `eDY2c3sG4cwh99q0F`, builds 0.1.1–0.1.3). Source: `collectivewinca/apify-actor-replacements` PR #51 (merged).

## Runs (public `POST emerald.xboxservices.com/xboxcomfd/browse`, cursor paging, 25/page, no detail crawl)

| Batch | Run / dataset | Rows | New unique | Apify $ | Status |
|---|---|---|---|---|---|
| Smoke US | 2ReihYwx1aoCG4uEz / GOZBXU9vlgQJUYelx | 100 | — | 0.001 | SUCCEEDED (maxGames 100) |
| US | IOYAstNbgyZZaNdmz / 4jW6D2kLnSYXnZSGJ | 17,336 | 17,336 | 0.134 | SUCCEEDED (build 0.1.1) |
| GB+CA | dVwPIBdCxc30HNynQ / 88LA5afD3PQ2ldbTe | 210 | 141 | 0.031 | SUCCEEDED |
| DE+FR | BJI3oauEcjGzewhVm / 3WQXEdqODbhALlFtu | 306 | 54 | 0.034 | SUCCEEDED |
| JP+AU | Z1SRSfE1wmMx3AdFP / TKzdMIdjDZF1l8ceu | 449 | 254 | 0.034 | SUCCEEDED |

About $0.23 total. A $0 local dry run of the US cursor first returned 17,342 unique products (of 17,937 listed). US cost breakdown: dataset writes $0.087, KV writes $0.035 (STATE every page; build 0.1.3 writes every 25 pages), compute $0.015. Country batches: build 0.1.3, concurrency 2 (one walker per locale), delaySecs 0.3, 512 MB, `skipDatasetIds` = the US dataset; they ran in parallel so did not skip each other. Skipped ids are in each run's `SEEN_ELSEWHERE` KVS record.

## Merge + tags (`tools/xbox/`)

- `merge.py`: merges by Store productId, first record kept, adds `batch` and `countries`. Output: **17,785 unique games**. Countries: ca 17,364 · us 17,336 · gb 17,332 · au 16,994 · fr 16,796 · de 16,759 · jp 15,392.
- `fix_free.py`: applies the build 0.1.2 Game Pass guard (`resolve_free`) to the US rows scraped with 0.1.1 (21 changed). Result: 267 free · 16,061 paid · 1,457 no retail price (mostly pass-only/unlisted). A $0 Game Pass title is free only if its text says free (CoD MW III / BO6 launchers are not).
- `derive_tags.py`: Xbox store categories (weight 2; "Action & adventure" → Action+Adventure, "Role playing" → RPG, "Classics" → Retro, MOBA; Other/Tools dropped), then the PlayStation keyword rules plus Flight. Coverage: 99.8% have ≥1 tag; avg 4.28; 97 distinct tags.
- `find_gaps.py`: the PlayStation gap engine, stoplist + Retro. Runtime ~5.5 min. Vocab 79, 2,939 unseen candidates, 21 gaps, baseline p5 nnSim 0.776. See [`xbox-gaps-2026-10-28.md`](xbox-gaps-2026-10-28.md).
- Draft brief (here.now): https://jolly-yarrow-t2xf.here.now/

## Caveats

- **Empty ≠ sellable.** Gaps are holes in tag space, not demand.
- Each edition / bundle / Windows SKU is its own Game product, so counts include editions and some nearest neighbours are bundles.
- Xbox has no player tags, so most tags are keyword-derived and noisy.
