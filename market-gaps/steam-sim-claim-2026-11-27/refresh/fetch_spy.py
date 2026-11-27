"""Box-side SteamSpy request=all listing, 1 request/min, retrying pages that fail
('Connection failed: Too many connections'). Used only to find apps that are new since the
2026-10-25 snapshot. Stops after DEADLINE minutes."""
import json, os, time, urllib.request
D = "/workspace/anygame-steam-refresh-2026-11-27/spy"; DEADLINE = time.time() + 150 * 60
pages = list(range(0, 85)); empty = set()
while time.time() < DEADLINE:
    todo = [p for p in pages if not os.path.exists(f"{D}/page{p}.json") and p not in empty]
    if not todo: break
    p = todo[0]
    try:
        raw = urllib.request.urlopen(urllib.request.Request(f"https://steamspy.com/api.php?request=all&page={p}",
              headers={"User-Agent": "collectivewin-steam-catalog/0.1"}), timeout=60).read()
        d = json.loads(raw)
        if d: json.dump(d, open(f"{D}/page{p}.json", "w")); print(p, len(d), flush=True)
        else: empty.add(p); print(p, "empty", flush=True)
    except Exception as ex:
        print(p, "fail", str(ex)[:60], flush=True); pages.remove(p); pages.append(p)  # retry later
    time.sleep(61)
