# anygame-data

Public data plumbing for [anygame.dev](https://anygame.dev) — the published data layer behind the Steam Engine-Share Index and Minigame Distribution Terms Table.

**This repo does NOT deploy.** It holds pipelines, snapshots, and methodology. The anygame.dev SPA (`collectivewinca/anygamedev-ai-hub`) fetches JSON from this repo’s raw GitHub URLs at Vercel build time.

Panel ops (PocketBase schemas, recruitment, reminder emails, named contacts) live in the **private** sibling repo: [`collectivewinca/anygame-panel`](https://github.com/collectivewinca/anygame-panel). Anonymized panel aggregates may be published here under `panel-results/` when ready.

## Structure

```
anygame-data/
  engine-index/
    snapshot-YYYY-MM/           Monthly snapshot folder
      raw/                      Raw SteamDB tech page export (CSV)
      boxleiter.ods             LibreOffice spreadsheet with Boxleiter calcs (optional)
      engine-index-YYYY-MM.json Dated published snapshot
    engine-index-latest.json    Stable pointer for SPA build fetch
    fetch-snapshot.md           Manual runbook for the monthly snapshot

  minigame-terms/
    minigame-terms.json          Published terms table (WeChat, TikTok, Discord, …)
    snapshots/YYYY-MM/          Monthly diff-checker HTML captures
    changelog.md                Appended after monthly diff review

  panel-results/                Optional anonymized panel aggregates (public)
    panel-results-YYYY-MM.json

  platforms/
    app-store.md                Apple App Store inventory, runs, merge + tag notes
    google-play.md              Google Play runs, merge, tags, gaps (draft)
    google-play-gaps-2026-10-28.md  Ranked Google Play gap triples
    playstation.md              PlayStation Store runs, merge, tags, gaps (draft)
    playstation-gaps-2026-10-28.md  Ranked PlayStation gap triples
    xbox.md                     Xbox / Microsoft Store runs, merge, tags, gaps (draft)
    xbox-gaps-2026-10-28.md     Ranked Xbox gap triples
    nintendo.md                 Nintendo eShop runs, merge, tags, gaps (draft)
    nintendo-gaps-2026-10-28.md Ranked Nintendo gap triples
    epic.md                     Epic Games Store runs, merge, tags, gaps (draft)
    epic-gaps-2026-10-28.md     Ranked Epic gap triples

  tools/
    app-store/                  merge.py (batch merge) + derive_tags.py (offline tags v0)
    google-play/                merge.py + derive_tags.py (playChips first) + find_gaps.py
    playstation/                merge.py + derive_tags.py (Sony genres + keywords) + find_gaps.py
    xbox/                       merge.py + fix_free.py + derive_tags.py (Xbox categories + keywords) + find_gaps.py
    nintendo/                   merge.py (nsuid + title) + derive_tags.py (genres/features + keywords) + find_gaps.py

  methodology/
    engine-index-methodology.md
    minigame-terms-methodology.md
    platform-scrape-pipeline.md Scrape → normalize → gap-engine → brief
```

## Platform catalogs

Storefront scrape → normalize → gap-engine → brief, method (tag triples + `nnSim` / `bge-small`; **empty ≠ sellable**), and the top-10 roster: [`methodology/platform-scrape-pipeline.md`](methodology/platform-scrape-pipeline.md). Reports and gap-engine tooling belong in this repo.

App Store inventory, 7-country charts-only runs, and the merge + offline tag step (`tools/app-store/`): [`platforms/app-store.md`](platforms/app-store.md).

Google Play 7-country category runs, merge, playChips tags and gaps (`tools/google-play/`): [`platforms/google-play.md`](platforms/google-play.md).

PlayStation Store 7-storefront GraphQL runs, merge, tags and gaps (`tools/playstation/`): [`platforms/playstation.md`](platforms/playstation.md).

Xbox / Microsoft Store 7-storefront browse-API runs, merge, tags and gaps (`tools/xbox/`): [`platforms/xbox.md`](platforms/xbox.md).

Nintendo eShop 6-storefront runs (US/CA Algolia, GB/DE/FR NoE, JP), merge, tags and gaps (`tools/nintendo/`): [`platforms/nintendo.md`](platforms/nintendo.md).

GOG 7-storefront catalog API runs, merge, tags and gaps (`tools/gog/`): [`platforms/gog.md`](platforms/gog.md). Brief: https://cosmic-vision-3ac3.here.now/.

Steam 82k gap artifacts live in [PR #2](https://github.com/collectivewinca/anygame-data/pull/2) (`market-gaps/steam-2026-10-25/`) — do not duplicate them here. Live Steam brief: [https://lemon-paddle-m6n3.here.now/](https://lemon-paddle-m6n3.here.now/).

## Stable fetch URLs (SPA contract)

The SPA build should curl these paths on `main` (anonymous; this repo is public):

- `https://raw.githubusercontent.com/collectivewinca/anygame-data/main/engine-index/engine-index-latest.json`
- `https://raw.githubusercontent.com/collectivewinca/anygame-data/main/minigame-terms/minigame-terms.json`

Monthly publish steps:

1. Write the dated artifact under `engine-index/snapshot-YYYY-MM/`.
2. Copy/overwrite `engine-index/engine-index-latest.json` with the same payload.
3. Update `minigame-terms/minigame-terms.json` in place (keep history via git + `changelog.md`).

If the SPA fetch fails, it falls back to last-committed JSON in `anygamedev-ai-hub`’s `client/public/data/`.

## Sync mechanism

`anygamedev-ai-hub` Vercel build runs `scripts/fetch-snapshots.sh` before `vite build`. That script pulls the stable URLs above into `client/public/data/`.

## Related

| Repo | Visibility | Role |
|---|---|---|
| `collectivewinca/anygame-data` (this) | **Public** | Engine index + minigame terms + platform catalogs + public methodology |
| `collectivewinca/anygame-panel` | **Private** | PB schemas, migrations, panel runbooks, recruitment |
| `collectivewinca/anygamedev-ai-hub` | Private | anygame.dev SPA + Vercel APIs |

## License

Public data and methodology for the anygame.dev / VE Lab project. Attribution appreciated; no warranty.
