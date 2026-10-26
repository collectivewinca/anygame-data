# Platform scrape → normalize → gap → brief

Status: draft. **Reports, gap-engine scripts, and methodology live in this repo.** Actors live in [`collectivewinca/apify-actor-replacements`](https://github.com/collectivewinca/apify-actor-replacements). This repo does not deploy.

Steam 82k gap artifacts (2026-10-25) are already in [PR #2](https://github.com/collectivewinca/anygame-data/pull/2) (`market-gaps/steam-2026-10-25/`). Do not duplicate them here.

## Order of operations

Never skip scrape. Never treat an empty region as a shippable product.

1. **Scrape** the platform catalog (first-party public APIs where they exist; otherwise an Apify actor).
2. **Normalize** to platform-agnostic game records (shared keys across storefronts).
3. **Gap-engine** — tag/genre triples; use the chunked runner if the full embed OOMs.
4. **Brief** — developer-facing write-up with nearest real games as novelty evidence.
5. **Publish artifacts here** under `market-gaps/<platform>-YYYY-MM-DD/`. Live web briefs (here.now / anygame.dev) are out of band and need owner go.

## Method

The gap-engine looks for **tag triples** where every pair already exists in the catalog and the triple never does. Candidates are ranked by lowest nearest-neighbour similarity (`nnSim`) against real games, using [`BAAI/bge-small-en-v1.5`](https://huggingface.co/BAAI/bge-small-en-v1.5) via fastembed.

- Lower `nnSim` = emptier neighborhood.
- **Empty ≠ sellable.** An unseen triple is a catalog hole, not a product brief and not a revenue forecast. Nearest real games are evidence of novelty, not of demand.

Steam 2026-10-25 run (done): dataset [`CE2Yt6rGh8fmQ4Amv`](https://console.apify.com/storage/datasets/CE2Yt6rGh8fmQ4Amv) (82,535 items); live brief [https://lemon-paddle-m6n3.here.now/](https://lemon-paddle-m6n3.here.now/).

## Top-10 storefront roster

| # | Platform | Status |
|---|----------|--------|
| 1 | Steam | **Done** — dataset `CE2Yt6rGh8fmQ4Amv`; brief https://lemon-paddle-m6n3.here.now/; artifacts in [PR #2](https://github.com/collectivewinca/anygame-data/pull/2) `market-gaps/steam-2026-10-25/` |
| 2 | Apple App Store | **Next** — inventory + planned actor; see [`platforms/app-store.md`](../platforms/app-store.md) |
| 3 | Google Play | Planned |
| 4 | PlayStation Store | Planned |
| 5 | Xbox / Microsoft Store | Planned |
| 6 | Nintendo eShop | Planned |
| 7 | Epic Games Store | Planned |
| 8 | GOG | Planned |
| 9 | itch.io | Planned |
| 10 | Roblox (experiences) | Planned |

**Skip keyshops** (Eneba, GAMIVO, Kinguin, and similar) for v1. Optional later: Meta Horizon, WeGame / TapTap, Humble.

## Home for reports and tooling

| What | Where |
|---|---|
| Pipeline + roster (this file) | `methodology/platform-scrape-pipeline.md` |
| Per-platform scrape notes | `platforms/<storefront>.md` |
| Dated gap briefs + gap-engine scripts | `market-gaps/<platform>-YYYY-MM-DD/` (Steam lands via [PR #2](https://github.com/collectivewinca/anygame-data/pull/2)) |
| Actors | `collectivewinca/apify-actor-replacements` |
| Live web briefs | out of band (here.now / anygame.dev), owner go required |

Embedding `.npy` matrices stay out of git; regenerate with the gap-engine scripts.
