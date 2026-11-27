"""Run collectivewin/steam-catalog-scraper 0.1.3 page-by-page (startPage=p, maxPages=1), same
settings as the Oct run otherwise; retry pages where SteamSpy's listing failed or came back short."""
import json, os, time, urllib.request, sys
T = os.environ["APIFY_TOKEN"]; ACT = "ZuaZezhwnuEpuBhEO"; API = "https://api.apify.com/v2"
PAGES = range(0, 84); CONC = 12; MAXTRY = 10
MAN = "/workspace/anygame-steam-refresh-2026-11-27/manifest.json"
def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {T}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["data"]
man = json.load(open(MAN)) if os.path.exists(MAN) else {}
def save(): json.dump(man, open(MAN, "w"), indent=1)
def start(p):
    inp = {"maxGames": 0, "startPage": p, "maxPages": 1, "enrich": True, "concurrency": 12, "perIpDelaySecs": "1.0",
           "proxyConfiguration": {"useApifyProxy": True}}
    d = call("POST", f"/acts/{ACT}/runs?build=0.1.3&memory=4096", inp)
    man.setdefault(str(p), []).append({"run": d["id"], "dataset": d["defaultDatasetId"], "status": "RUNNING"}); save()
    print("start", p, d["id"], flush=True)
def page_ok(p):
    runs = man.get(str(p), [])
    if any(r["status"] == "SUCCEEDED" and r.get("items", 0) >= (1000 if p < 82 else 1) for r in runs): return True
    part = [r["items"] for r in runs if r["status"] == "SUCCEEDED" and r.get("items")]
    return any(part.count(x) >= 2 for x in part)  # same short page twice = SteamSpy really returns a short page
lastp = None
while True:
    running = 0
    for p, runs in man.items():
        for r in runs:
            if r["status"] in ("RUNNING", "READY"):
                d = call("GET", f"/actor-runs/{r['run']}")
                r["status"] = d["status"]
                if d["status"] not in ("RUNNING", "READY"):
                    r["items"] = call("GET", f"/datasets/{r['dataset']}")["itemCount"]; r["usd"] = d.get("usageTotalUsd")
                    print("done", p, r["status"], r["items"], flush=True); save()
                else: running += 1
    todo = [p for p in PAGES if not page_ok(p) and not any(r["status"] in ("RUNNING", "READY") for r in man.get(str(p), []))
            and len(man.get(str(p), [])) < MAXTRY]
    # stop expanding past the end: a page that SUCCEEDED with 0 items twice is past the end of the list
    end = [p for p in PAGES if sum(1 for r in man.get(str(p), []) if r["status"] == "SUCCEEDED" and r.get("items") == 0) >= 3]
    if end: todo = [p for p in todo if p < min(end)]
    for p in todo[: max(0, CONC - running)]:
        start(p); running += 1; time.sleep(65)  # space out SteamSpy request=all calls (1/min)
    if running == 0 and not todo: break
    time.sleep(30)
print("ALL DONE", flush=True)
