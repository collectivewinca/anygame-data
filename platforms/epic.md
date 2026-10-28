# Epic Games Store — catalog runs, merge, tags, gaps

Status: **draft** (2026-10-28 ET). Actor `collectivewin/epic-games-store-scraper` (id `bMVnZ5K6cwjYFxuuQ`, builds 0.1.1–0.1.2). Source: `collectivewinca/apify-actor-replacements` PR #53 (merged).

## Runs (public `store.epicgames.com/graphql` searchStoreQuery, persisted query, `games/edition/base`, 40/page, offset paging, no detail crawl)

| Batch | Run / dataset | Rows | New unique | Apify $ | Status |
|---|---|---|---|---|---|
| Smoke US | kVVifvlymj0jGGyyu / Ul9H64Fic4XhCqZ9g | 80 | — | 0.001 | SUCCEEDED (maxGames 60) |
| US | k94BULhbnEdJGPmg9 / gkAf69T2P7IyZl2RF | 7,210 | 7,210 | 0.039 | SUCCEEDED (build 0.1.1) |
| GB+CA | eUrlQe2hWH6DzTFAh / HDoCBokoWXDBJDaTA | 9 | 6 | 0.008 | SUCCEEDED (0.1.2, skip US) |
| DE+FR | EOYN2xaVaZjLY6JL3 / OlikrfEdkBAAONrhZ | 9 | 7 | 0.008 | SUCCEEDED (0.1.2, skip US) |
| JP+AU | IwXNLSpLg1lNdpA6X / J50vvm4rpiVqpsA8z | 17 | 10 | 0.008 | SUCCEEDED (0.1.2, skip US) |

About $0.06 total. A $0 local dry run of the full US listing first returned all 7,210 listed base games. The three country batches ran in parallel, so they did not skip each other.

## Merge + tags (`tools/epic/`)
- `merge.py`: merges by Epic offer id and adds `batch` and `countries`. Output: **7,233 unique games**.
- `fix_free.py`: an unreleased $0 title with no "free" in its text is unpriced pre-release, so isFree=None (244 changed; build 0.1.2 does this in the actor). Result: 656 free · 6,333 paid · 244 unknown. List price only: the weekly free promo never counts as free.
- `derive_tags.py`: Epic genre tags (weight 2; Action-Adventure → Action+Adventure, Rogue-Lite → Roguelike, Turn-Based Strategy → Turn-Based+Strategy, Narration → Story Rich), then the Xbox keyword rules. Coverage: 99.9% have ≥1 tag; avg 3.59; 81 distinct tags.
- `find_gaps.py`: the Xbox gap engine, with Indie added to the stoplist. See [`epic-gaps-2026-10-28.md`](epic-gaps-2026-10-28.md).
- Draft brief (here.now): https://keen-petal-4z6b.here.now/

## Caveats
- **Empty ≠ sellable.** Gaps are holes in tag space, not demand.
- Epic's catalog is small (~7.2k base games), there are no review counts, and the genre tags are coarse, so fine tags are keyword-derived and noisy.
- JPY has no decimals, so `priceCents` holds yen for JP. AU uses the en-US locale.
