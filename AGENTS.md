# AGENTS.md — anygame-data
- Platform pipeline: scrape (collectivewin actors in apify-actor-replacements) → `tools/<platform>/merge.py` → `derive_tags.py` → `find_gaps.py` (bge-small-en-v1.5) → brief. Notes per platform in `platforms/`.
- Gaps are not demand: always say **empty ≠ sellable** and cite nearest real games.
- Cite Apify run and dataset ids for every catalog. Do not start paid runs without approval.
- Keep README.md, CHANGELOG.md and AGENTS.md in step with what ships.
- Steam: SteamSpy `request=all` can fail intermittently ("Too many connections"); the actor then ends its listing early. See `market-gaps/steam-sim-claim-2026-11-27/refresh/` for the page-split + STATE-resume workaround.
