# Engine-Share Index methodology

Status: stub for v0.1 (August 2026). Expand when the first snapshot ships.

## Purpose

Estimate engine share among recent Steam releases using public SteamDB technology detection plus Boxleiter-style revenue bands — not exact revenue.

## Sources

- Primary engine detection: SteamDB tech / app technology fields (manual monthly pull)
- Revenue proxy: review counts × genre-adjusted Boxleiter multipliers × price
- Window: trailing 12 months, top ~500 releases (exact N recorded per snapshot)

## Known limitations

- SteamDB undercounts some engines (Godot, GameMaker, Construct, LibGDX, HTML5, others) — call out on `/methodology` and in each snapshot `meta`
- Boxleiter ranges diverge across providers; we publish bands + confidence, not false precision
- Manual snapshot = point-in-time; not live

## Snapshot artifact

See `engine-index/engine-index-latest.json` schema (`schema_version`, `engines`, `titles`, `meta`).
