# PlayStation Store — catalog runs, merge, tags, gaps

Status: **draft** (2026-10-28 ET). Actor `collectivewin/playstation-games-scraper` (id `12Db4YeqNAtk9ovjQ`, build 0.1.4). Source: `collectivewinca/apify-actor-replacements` PR #50 (merged).

## Runs (Sony public GraphQL `categoryGridRetrieve` split by genre facet, plus product detail)

| Batch | Run / dataset | Rows | New unique | Apify $ | Status |
|---|---|---|---|---|---|
| US h1 | UcfcRLfZODNYFgUaS / 2dw1yA1ZcuFxRMCfh | 759 | 12,621 (US total) | 0.019 | FAILED (OOM at concurrency 20); rows kept |
| US h2 | qcVBTvuZu0bdcWSup / ey0ewEI6WxkFqaWhO | 4,952 | | 0.076 | FAILED (OOM); rows kept |
| US h3 | hz02oJyRMJs3KNbCX / BTJ9hoSh30NgyXrQC | 6,910 | | 0.137 | ABORTED at the $0.13 guard |
| GB+CA | VRVvy0PcQawjmswDk / uq6QdyM2ONYwLb2NT | 577 | 354 | 0.052 | SUCCEEDED |
| DE+FR | knHU8cuoDrdJ2v6jO / XYmhfDa2UGkdeukQR | 646 | 11 | 0.053 | SUCCEEDED |
| JP+AU | 5e7CDCjDgTFhfNMhk / OUgtwL69IQArsBPYR | 1,022 | 525 | 0.058 | SUCCEEDED |

About $0.39 total for these runs (US $0.23, countries $0.16), plus about $0.017 for an earlier failed US attempt (CNi3at2IpEMim5aVf) and the smoke run. Country batches used concurrency 5, delaySecs 0.4 and 1024 MB, with `skipDatasetIds` = the three US datasets. The three country batches ran in parallel, so they did not skip each other. Ids that were skipped are in each run's `SEEN_ELSEWHERE` KVS record.

**OOM lesson:** do not use concurrency 20. Use 5. Concept detail HTML is heavy.

## Merge + tags (`tools/playstation/`)

- `merge.py`: merges the batches by concept id and keeps the first record. It adds `batch` and `countries` (from the record country plus `SEEN_ELSEWHERE`). Output: **13,511 unique games** (226 free; 143 without price detail). Countries: ca 12,833 · us 12,621 · fr 12,610 · de 12,562 · au 12,521 · gb 12,309 · jp 9,471.
- `derive_tags.py`: Sony `localizedGenres` (normalized, weight 2; Unique/Adult dropped), a VR flag from platforms, then App Store v0 keyword rules plus console rules (Open World, Souls-like, Metroidvania, Stealth, Local Co-op, Cozy, Visual Novel, …). Coverage: 99.5% have ≥1 tag; avg 3.43; 101 distinct tags.
- `find_gaps.py`: the Google Play gap engine (BAAI/bge-small-en-v1.5). Stoplist: Action, Adventure, Casual, Family. Description is truncated to 600 chars. Runtime about 4 min on the box CPU. Vocab 82, 3,079 unseen candidates, 21 gaps, baseline p5 nnSim 0.770. See [`playstation-gaps-2026-10-28.md`](playstation-gaps-2026-10-28.md).
- Draft brief (here.now): https://stormy-willow-g6jc.here.now/

## Caveats

- **Empty ≠ sellable.** Gaps are holes in tag space, not demand.
- PlayStation has no player tags, so most tags are keyword-derived and noisy.
- US h3 stopped at the cost guard, so the US long tail may be slightly incomplete.
- JP-only titles have Japanese genre names (one gap is that artifact).
