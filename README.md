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

  methodology/
    engine-index-methodology.md
    minigame-terms-methodology.md
```

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
| `collectivewinca/anygame-data` (this) | **Public** | Engine index + minigame terms + public methodology |
| `collectivewinca/anygame-panel` | **Private** | PB schemas, migrations, panel runbooks, recruitment |
| `collectivewinca/anygamedev-ai-hub` | Private | anygame.dev SPA + Vercel APIs |

## License

Public data and methodology for the anygame.dev / VE Lab project. Attribution appreciated; no warranty.
