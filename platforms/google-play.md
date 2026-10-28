# Google Play — catalog runs, merge, tags, gaps

Status: **draft** (2026-10-28 ET). Actor `collectivewin/googleplay-games-scraper` (id `cIvzURzdWXoYbrd5G`), source in `collectivewinca/apify-actor-replacements` draft PR #47.

## Runs (GAME_* category pages, hl=en)

| Batch | Run / dataset | New rows | Apify $ |
|---|---|---|---|
| US | KHHsswQscLF5cfV3m / cudodsrvC5Dwxck9W; QFc9hwwPOd5P5YdnS / sUgwtdHOOPK7lL2gQ; + 77-id local Educational top-up ($0) | 899 | 0.086 + 0.109 |
| GB+CA | LxEfDeoiIzHkwTMI5 / 19XeZM67LJ4xkErTd | 218 | 0.056 |
| DE+FR | FUK7ts2t9mYoyse9i / ZfBdXBCLHk5TPjUlq | 85 | 0.025 |
| JP+AU | bbVVoVGGCTOiu0SbF / l7LcmDaqAkwU9dgzW | 141 | 0.039 |

About $0.31 total (country batches ≈ $0.12). Non-US batches pass earlier datasets in `skipDatasetIds` (actor 0.1.4), so they fetch only new games. That is why later countries are cheap.

## Merge + tags (`tools/google-play/`)

- `merge.py`: merge batches by package id, first record kept, adds `batch`. Output: 1,312 unique games (1,275 free / 37 paid).
- `derive_tags.py`: Google `playChips` first (weight 3; 1,259 games have chips), then `genres` (2), then the App Store v0 keyword rules (copied unchanged). Coverage: 1,312/1,312 games have ≥1 tag; avg 9.84 tags; 386 distinct tags.
- `find_gaps.py`: App Store/Steam gap engine (BAAI/bge-small-en-v1.5 via fastembed). Changes: stoplist of generic chips (Single player, Stylized, Offline, Casual, Realistic, Immersive, Light-hearted, Cartoon), min tag count 10, baseline sample capped at catalog size. 131-tag vocab, 2,300 unseen candidates, 22 gaps, baseline p5 nnSim 0.724. See [`google-play-gaps-2026-10-28.md`](google-play-gaps-2026-10-28.md).
- Draft brief (here.now): https://dusky-sierra-jz6b.here.now/

## Caveats

- **Empty ≠ sellable.** Gaps are holes in tag space, not demand.
- GAME_CASINO is empty in all countries (list is JS/client-loaded).
- hl=en text everywhere; titles can still be local-language.
- Category pages only, about 50–80 games per category; not the full store.
- Country = first country that fetched the game (us 899, gb 127, jp 121, ca 66, de 57, fr 23, au 19).
