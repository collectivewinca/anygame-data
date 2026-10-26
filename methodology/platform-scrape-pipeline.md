# Platform scrape → gap pipeline

Order of operations (never skip scrape):

1. Scrape platform catalog (Apify actor / official APIs)
2. Normalize to platform-agnostic game records
3. Gap-engine (tag/genre triples; chunked runner if OOM)
4. Developer brief + nearest real games as novelty evidence
5. Publish (here.now / anygame.dev with owner go) and push artifacts here

## Top-10 roster

| # | Platform | Status |
|---|----------|--------|
| 1 | Steam | Done — see `market-gaps/steam-2026-10-25/` and https://lemon-paddle-m6n3.here.now/ |
| 2 | Apple App Store | Planned scrape |
| 3 | Google Play | Planned scrape |
| 4 | PlayStation Store | Planned scrape |
| 5 | Xbox / Microsoft Store | Planned scrape |
| 6 | Nintendo eShop | Planned scrape |
| 7 | Epic Games Store | Planned scrape |
| 8 | GOG | Planned scrape |
| 9 | itch.io | Planned scrape |
| 10 | Roblox (experiences) | Planned scrape |

Skip keyshops (Eneba, GAMIVO, etc.) for v1. Optional later: Meta Horizon, WeGame/TapTap, Humble.
