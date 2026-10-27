# Apple App Store — catalog inventory

Status: **charts-only catalog scraped + tagged** (2026-10-26). Actor `collectivewin/appstore-games-scraper` is built; see [Catalog runs](#catalog-runs-2026-10-26) below. Sections further down are the original inventory notes.

Next storefront after Steam in the scrape → normalize → gap → brief order. See [`methodology/platform-scrape-pipeline.md`](../methodology/platform-scrape-pipeline.md).

## Existing actors / repos

- No App Store / iTunes / iOS actor in `collectivewinca/apify-actor-replacements` (only `steam-catalog-scraper` is game-related).
- No first-party `collectivewinca` App Store / iTunes repo.
- Do not buy a paid Store actor. Do not scrape `apps.apple.com` HTML at scale for v1.

## Public sources (probed 2026-10-26)

These are first-party Apple endpoints. Prefer them over HTML.

1. **iTunes Lookup** — `https://itunes.apple.com/lookup?id=<ids,comma,≤~200>&country=us`  
   Works. Record fields include `trackId`, `trackName`, `description`, `genres[]` / `genreIds`, `primaryGenreName`, `artistName`, `sellerName`, `releaseDate`, `price`, `currency`, `formattedPrice`, `averageUserRating`, `userRatingCount`, `artworkUrl512`, `trackViewUrl`, `features`, `advisories`, `contentAdvisoryRating`, `isGameCenterEnabled`.

2. **iTunes Search** — `https://itunes.apple.com/search?term=&entity=software&genreId=6014&limit=200`  
   Max 200 results per query; documented ~20 req/min. Use term sweeps (a–z, keywords) plus game subgenre ids `7001`–`7019` for discovery. `6014` is Games; other `60xx` ids are non-game app categories.

3. **Legacy RSS charts** — `https://itunes.apple.com/us/rss/{topfreeapplications,toppaidapplications,topgrossingapplications}/limit=200/genre=<id>/json`  
   Works, but Apple caps the feed at **100 entries** per genre even when `limit=200`. Game subgenres `7001`–`7019` (Action, Adventure, Casual, Board, Card, Casino, Dice, Educational, Family, Music, Puzzle, Racing, RPG, Simulation, Sports, Strategy, Trivia, Word; `7010` is unused) × 3 charts × N countries ≈ a few thousand unique seed ids.

4. **New Marketing Tools RSS** — `https://rss.marketingtools.apple.com/api/v2/...`  
   Works, but no genre filter and max 100. Low value versus the legacy feed.

5. **apps.apple.com** — genre browse pages 404 (removed). Per-app pages (`apps.apple.com/us/app/id<id>`) still exist for “similar apps” / developer-other-apps expansion. HTML scraping; heavier; **out of scope for v1**.

Discovery expansion: Lookup `?id=<artistId>&entity=software` returns all apps by a developer → snowball from chart seeds. Realistic reach: **20–60k games** over phases.

## Schema mapping

Normalize to the same platform-agnostic game record the Steam actor already emits. `platform=appstore`.

| Record key | App Store source |
|---|---|
| `id` | `trackId` |
| `title` | `trackName` |
| `type` | `"game"` |
| `description` | `description` |
| `about` | `null` (or first paragraph) |
| `genres` | `genres[]` minus `"Games"` |
| `categories` | `features` + `advisories` + `contentAdvisoryRating` |
| `developers` | `[artistName]` |
| `publishers` | `[sellerName]` |
| `releaseDate` | `releaseDate` |
| `comingSoon` | `false` (preorders not exposed) |
| `isFree` | `price == 0` |
| `priceCents` | `round(price * 100)` |
| `currency` | `currency` |
| `reviews` | `{positive: null, negative: null, total: userRatingCount, score: averageUserRating / 5}` |
| `owners` | `null` (chart rank is a weak proxy only) |
| `url` | `trackViewUrl` |
| `image` | `artworkUrl512` |

### Gaps (especially tags)

- **`tags[]` / `tagVotes{}` — none.** Apple has no user tags. The gap-engine is tag-triple based (`nnSim` / `bge-small-en-v1.5`; empty ≠ sellable), so App Store records need **derived tags** before they are useful.
- Planned derivation (offline, not in the actor): subgenres + keyword / LLM-free extraction from `description` against the Steam tag vocabulary (embedding nearest Steam tags via local `bge-small`). Home for that script: gap-engine `derive_tags.py` in this repo when it lands.
- `owners` missing.
- No positive/negative review split.
- IAP not in these APIs.

## Planned actor: `collectivewin/appstore-games-scraper`

**Not built yet.** Planned Python actor (`apify==4.1.0`) mirroring `collectivewin/steam-catalog-scraper`, to live in `collectivewinca/apify-actor-replacements`.

Intended input:

- `countries[]` (default `["us"]`)
- `genreIds[]` (`7001`–`7019`)
- `charts[]`
- `seedSearchTerms[]`
- `expandDevelopers` (bool)
- `maxGames`
- `lookupBatch` (150)
- `delaySecs` (3.5)
- `proxyConfiguration`

Intended phases:

1. Seeds — RSS genre charts + search sweeps
2. Developer snowball
3. Batched Lookup → `record()` with the keys above
4. Resumable `STATE` in the key-value store

**Tag derivation stays off-actor** so the scrape run has no embedding / model dependency. Do that in the gap-engine after normalize.

Planned rollout (none of this has started): local dry run (no Apify) on ~500 games → later smoke + larger pulls, only with owner go. No deploy, no here.now, no Apify runs from this notes PR.

## Catalog runs (2026-10-26)

Charts-only (RSS top free / paid / grossing × genres `7001`–`7019`), `expandDevelopers: false`, `delaySecs: 3.5`, 1024 MB, three country batches:

| Countries | Apify run | Dataset | Games |
|---|---|---|---|
| US, GB, CA | `H5F2LhiHfhsSkdtnE` | `aNhPtgQvNjT49JV4U` | 4,343 |
| DE, FR | `Gx3BgNFSJLdGTBZQH` | `sLM9DT5HcB04yRJAK` | 3,750 |
| JP, AU | `VmmIXZOuTjGFYftxS` | `DNYpt7S5cJGjBuEes` | 4,622 |

The actor dedupes within a run, so a game appears under the first country of its batch only.

### Merge — `tools/app-store/merge.py`

Merges the three batch `games.json` files by `(platform, id)` → **7,224 unique games** (4,372 free / 2,852 paid). Keeps the US/English record when present and adds `countries[]` and `chartHits[]` (`cc/chart/genreId/#rank`). Overlap: 3,859 games in one batch, 1,239 in two, 2,126 in all three. The merged JSON (~23 MB) is not committed; rebuild it from the datasets above.

### Offline tags — `tools/app-store/derive_tags.py` (v0)

`python3 derive_tags.py games.json games.tagged.json` fills `tags[]` / `tagVotes{}` in the Steam record shape:

- chart `genreId` → English genre (weight 2), plus English `genres[]` strings
- regex keyword tags (about 40; English plus some DE/FR/JP terms) over title / about / description

Coverage on the 7,224-game merge: 100% of games have ≥1 tag (the chart genre is always present), 87.7% have ≥1 keyword tag, and games average 3.44 tags. This is a v0 keyword tagger, **not** the embedding-to-Steam-vocabulary approach planned above. Broad keyword matches (e.g. Story Rich, Educational, Offline) are noisy, and non-English descriptions get fewer keyword tags.
