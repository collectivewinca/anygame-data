# Changelog

## 2026-10-28

### NEW: GOG catalog + gaps + idea brief

Alet greenlit ("we have Gog… + run this version too"). Actor `collectivewin/gog-games-scraper` ([apify-actor-replacements#54](https://github.com/collectivewinca/apify-actor-replacements/pull/54), Apify id `5WeGrFRbrMQGPkgwg`). 6,572 unique games across US/GB/CA/DE/FR/JP/AU. Tools under [`tools/gog/`](./tools/gog). Platform notes [`platforms/gog.md`](./platforms/gog.md), gaps [`platforms/gog-gaps-2026-10-28.md`](./platforms/gog-gaps-2026-10-28.md). Draft brief: https://cosmic-vision-3ac3.here.now/

## 2026-10-28 — itch.io

Actor `collectivewin/itch-games-scraper` ([apify-actor-replacements#55](https://github.com/collectivewinca/apify-actor-replacements/pull/55), `l7yIXTWjTL5hNJlzs`). 30,287 unique games (top-rated sample of 110 tag feeds). Tools `tools/itch/`, notes `platforms/itch.md`, gaps `platforms/itch-gaps-2026-10-28.md`. Draft brief: https://mystic-aurora-q32t.here.now/

## 2026-10-28 — Roblox experiences

Actor `collectivewin/roblox-experiences-scraper ([aar#56](https://github.com/collectivewinca/apify-actor-replacements/pull/56))` (`tw3gPMN3uWG0c3ray`). 11,050 experiences (charts + search sample). Tools `tools/roblox/`, notes `platforms/roblox.md`, gaps `platforms/roblox-gaps-2026-10-28.md`. Draft brief: https://quiet-falcon-9yw7.here.now/

## Unreleased
- Epic Games Store: added `tools/epic/` (`merge.py`, `fix_free.py` pre-release $0 guard, `derive_tags.py`, `find_gaps.py`), `platforms/epic.md` (5 runs, about $0.06, 7,233 unique games) and `platforms/epic-gaps-2026-10-28.md` (19 gaps). Brief: https://keen-petal-4z6b.here.now/.
- Nintendo eShop: added `tools/nintendo/` (`merge.py` with cross-region title merge, `derive_tags.py`, `find_gaps.py`), `platforms/nintendo.md` (5 runs, about $0.33, 31,151 unique games) and `platforms/nintendo-gaps-2026-10-28.md` (16 gaps). Brief: https://yearly-warden-5688.here.now/.
- Xbox / Microsoft Store: added `tools/xbox/` (`merge.py`, `fix_free.py` Game Pass guard, `derive_tags.py`, `find_gaps.py`), `platforms/xbox.md` (5 runs/datasets, ~$0.23, 17,785 unique games) and `platforms/xbox-gaps-2026-10-28.md` (21 gaps); brief https://jolly-yarrow-t2xf.here.now/.
- PlayStation Store: added `tools/playstation/` (`merge.py` with countries, `derive_tags.py`, `find_gaps.py`), `platforms/playstation.md` (6 runs/datasets, ~$0.39, 13,511 unique games) and `platforms/playstation-gaps-2026-10-28.md` (21 gaps); brief https://stormy-willow-g6jc.here.now/.
- Google Play: added `tools/google-play/` (`merge.py`, `derive_tags.py` with playChips first, `find_gaps.py`), `platforms/google-play.md` (runs, datasets, merge, tag coverage, caveats) and `platforms/google-play-gaps-2026-10-28.md` (22 ranked gaps); added `AGENTS.md`.
- App Store: added `tools/app-store/merge.py` and `tools/app-store/derive_tags.py` (v0 offline tagger); documented the three 2026-10-26 charts-only runs and their datasets, and the merge and tag coverage, in `platforms/app-store.md`.
