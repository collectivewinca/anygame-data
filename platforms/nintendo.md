# Nintendo eShop — catalog runs, merge, tags, gaps

Status: **draft** (2026-10-28 ET). Actor `collectivewin/nintendo-eshop-games-scraper` (id `7evW6TQxMrCdeWqR5`, builds 0.1.1–0.1.2). Source: `collectivewinca/apify-actor-replacements` PR #52.

## Sources (public, no auth)

- **US, CA:** nintendo.com Algolia `store_game_en_us` / `store_game_en_ca`. Each query returns at most 1,000 hits, so the walker splits the catalog recursively by facet (platform → rating → price band → genre → players → availability → publisher → developer → features), with a NOT-remainder at each level. A $0 local probe got 20,795 of 20,795 listings in about 1.6k requests.
- **GB, DE, FR:** `searching.nintendo-europe.com/{en,de,fr}/select` Solr, filtered to `type:GAME`, Switch/Switch 2 (`playable_on_txt:(HAC OR BEE)`) and `eshop_removed_b:false` (build 0.1.2).
- **JP:** `search.nintendo.jp/nintendo_soft/search.json`, `1_HAC` + `05_BEE`, with `sctg` aoc/bundle dropped.
- **AU:** not supported. No public endpoint was reachable (NoE `/au` → 403), so the JP+AU batch contains JP only.

## Runs

| Batch | Run / dataset | Rows | New unique (after title merge) | Apify $ | Status |
|---|---|---|---|---|---|
| Smoke US+GB+JP | PmL5QT04NjA6a77Eq / 95hFGFh91dn1XDNiy | 300 | — | 0.0003 | SUCCEEDED (maxGames 100 each) |
| US | P9LJmy5flOl9XPSD1 / tVJ407HH6FXVRMbPc | 19,842 | 19,547 | 0.120 | SUCCEEDED (0.1.1, 1 GB) |
| GB+CA | Ulhgqf7Ec63Iy5Bom / fIjbAgVjv2Z9rD0Zd | 20,017 | 1,437 | 0.111 | SUCCEEDED (0.1.2, 512 MB, skip US) |
| DE+FR | CcNh8ULsPRATf472h / 1HQS0s7eSSNXJ4s51 | 69 | 34 | 0.009 | SUCCEEDED (skip GB) |
| JP+AU | jFKiLxceTEBaQFPc5 / lttYT0AqPMDRuFb9F | 16,247 | 10,133 | 0.089 | SUCCEEDED (JP only) |

Total is about $0.33. nsuids are shared within a region (US/CA, GB/DE/FR), so `skipDatasetIds` removes in-region repeats. The same game has different nsuids in US, EU and JP.

## Merge + tags (`tools/nintendo/`)

- `merge.py`: merges by nsuid (plus SEEN_ELSEWHERE), then across regions by normalized title. Result: 56,166 nsuids → **31,151 unique games**. Countries: gb 19,782 · de 19,770 · fr 19,603 · us 19,547 · ca 19,280 · jp 15,844. Price: 274 free (regular price exactly 0), 30,207 paid, 670 unknown.
- `derive_tags.py`: Xbox rules, plus Nintendo genre labels (US, EU EN/DE/FR, JP mapped to one vocabulary) and US gameplay-feature labels (weight 1). Coverage: 97.8% of games have at least one tag; average 2.86; 87 distinct tags.
- `find_gaps.py`: the Xbox gap engine, with an extended stoplist (Arcade, Local Multiplayer, Score/Time Attack …). Runtime about 10 min. Vocabulary 66, 3,221 unseen candidates, 16 gaps, baseline p5 nnSim 0.913. See [`nintendo-gaps-2026-10-28.md`](nintendo-gaps-2026-10-28.md).
- Draft brief (here.now): https://yearly-warden-5688.here.now/

## Caveats

- **An empty triple does not mean a game would sell.** A gap is a hole in tag space, not evidence of demand.
- The cross-region title merge misses Japanese-titled JP listings of Western games, which inflates the JP-only count.
- Each record keeps the currency of its first-fetched store. EU `price_lowest_f` can be a sale price.
- Nintendo has no player tags. Many tags come from keywords, so some are noise, and the Switch catalog is dense (neighbour sim 0.8–0.9).
