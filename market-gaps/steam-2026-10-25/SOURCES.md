# Steam market gaps — full 82k (2026-10-25)

- Live brief: https://lemon-paddle-m6n3.here.now/
- Apify run: FwiVYa7CgChoV7Tpc
- Dataset: CE2Yt6rGh8fmQ4Amv (82,535 items)
- Actor: collectivewin/steam-catalog-scraper 0.1.3 (collectivewinca/apify-actor-replacements PR #36)
- Method: tag triples where every pair exists and the triple never does; ranked by lowest nnSim (bge-small-en-v1.5). Empty ≠ sellable.
- Inspiration: https://x.com/SyntheticBeef/status/2112904858718367750
- Note: embeddings `.npy` omitted from git (too large); regenerate with the gap-engine scripts.
