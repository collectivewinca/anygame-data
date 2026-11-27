import json, os, urllib.request
T = os.environ["APIFY_TOKEN"]; API = "https://api.apify.com/v2"
def call(path):
    return json.load(urllib.request.urlopen(urllib.request.Request(API + path, headers={"Authorization": f"Bearer {T}"}), timeout=60))["data"]
m = json.load(open("manifest.json"))
for p, rs in m.items():
    for r in rs:
        if r["status"] not in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT") or r.get("resurrected"):
            d = call(f"/actor-runs/{r['run']}"); r["status"] = d["status"]; r["usd"] = d.get("usageTotalUsd")
            r["items"] = call(f"/datasets/{r['dataset']}")["itemCount"]
json.dump(m, open("manifest.json", "w"), indent=1)
for p, rs in sorted(m.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
    print(p, [(r["run"], r["status"], r.get("items")) for r in rs])
print("usd", round(sum(r.get("usd") or 0 for rs in m.values() for r in rs), 2))
