# Engine index — monthly snapshot runbook

Manual process (v0.1). Do **not** scrape SteamDB on a cron; ToS risk is high. See `methodology/engine-index-methodology.md`.

## Prerequisites

- Browser access to [steamdb.info/tech/](https://steamdb.info/tech/)
- LibreOffice (or compatible) for Boxleiter calcs
- This repo cloned; push access to `main`

## Steps

1. Create `engine-index/snapshot-YYYY-MM/` (e.g. `snapshot-2026-08/`) with `raw/`.
2. Export / capture top ~500 Steam releases, trailing 12 months, with engine detection, review counts, price, peak CCU as available.
3. Save raw export under `raw/` (CSV preferred).
4. Run Boxleiter estimates in spreadsheet (`boxleiter.ods` optional in the snapshot folder):
   - reviews × multiplier × price, genre-adjusted
   - record multiplier ranges used in methodology notes if they change
5. Produce `engine-index-YYYY-MM.json` in the snapshot folder.
6. Copy that file over `engine-index/engine-index-latest.json` (stable SPA URL).
7. Commit and push. Confirm raw URL serves the new payload:

   ```bash
   curl -sL https://raw.githubusercontent.com/collectivewinca/anygame-data/main/engine-index/engine-index-latest.json | head
   ```

8. Trigger or wait for `anygamedev-ai-hub` Vercel rebuild so the SPA picks it up (or rely on next deploy).

## Definition of done

- [ ] Dated snapshot folder committed
- [ ] `engine-index-latest.json` matches the dated publish
- [ ] Methodology notes still accurate (undercounts, confidence bands)
- [ ] SPA fallback copy in `anygamedev-ai-hub` updated if you maintain one
