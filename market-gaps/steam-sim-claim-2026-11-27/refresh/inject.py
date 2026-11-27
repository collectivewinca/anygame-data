"""Plan B for the SteamSpy listing outage: reuse finished 0-item runs of the same actor/build/input,
write a STATE record (listingDone + app chunk) into the run's own key-value store, then resurrect
the run. The actor's built-in resume path skips the SteamSpy listing and only enriches the chunk
(Steam appdetails + SteamSpy appdetails), exactly as in a normal run."""
import json, os, sys, urllib.request, glob
T = os.environ["APIFY_TOKEN"]; API = "https://api.apify.com/v2"
def call(method, path, body=None, raw=False):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {T}", "Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=120).read()
    return r if raw else json.loads(r)["data"] if r else None
m = json.load(open("manifest.json"))
covered = set()
for p, rs in m.items():
    for r in rs:
        if r["status"] in ("SUCCEEDED", "ABORTED") and r.get("items"):
            f = f"pages/{r['dataset']}.json"
            if not os.path.exists(f) or len(json.load(open(f))) != r["items"]:
                open(f, "wb").write(call("GET", f"/datasets/{r['dataset']}/items?clean=1&format=json", raw=True))
            covered |= {g["id"] for g in json.load(open(f))}
old = {g["id"]: g["title"] for g in json.load(open("/workspace/steam-gaps-full/games.json"))}
spy = {}
for f in glob.glob("spy/page*.json"):
    spy.update(json.load(open(f)))
apps = {i: {"appid": int(i), "name": t} for i, t in old.items()}
for i, v in spy.items(): apps[i] = v  # real SteamSpy listing row where we have it
rem = sorted(i for i in apps if i not in covered)
donors = [r for p, rs in m.items() for r in rs if r["status"] == "SUCCEEDED" and r.get("items") == 0 and not r.get("resurrected")]
n = int(sys.argv[1]) if len(sys.argv) > 1 else len(donors)
donors = donors[:n]
size = -(-len(rem) // len(donors))
print("covered", len(covered), "listing", len(apps), "new vs Oct", len(set(apps) - set(old)), "remaining", len(rem), "chunks", len(donors), "size", size)
for k, r in enumerate(donors):
    chunk = rem[k * size:(k + 1) * size]
    if not chunk: break
    st = {"page": 0, "apps": {i: apps[i] for i in chunk}, "done": [], "listingDone": True}
    run = call("GET", f"/actor-runs/{r['run']}")
    kv = run["defaultKeyValueStoreId"]
    call("PUT", f"/key-value-stores/{kv}/records/STATE", st, raw=True)
    d = call("POST", f"/actor-runs/{r['run']}/resurrect")
    r.update({"status": d["status"], "resurrected": True, "chunk": len(chunk)})
    print("resurrected", r["run"], len(chunk), d["status"])
json.dump(m, open("manifest.json", "w"), indent=1)
