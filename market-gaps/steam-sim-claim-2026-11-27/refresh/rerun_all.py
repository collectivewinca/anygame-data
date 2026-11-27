"""Re-run every October production batch of the 9 non-Steam storefront actors with the same input,
build, memory and timeout. skipDatasetIds that pointed at October datasets are remapped to the
new datasets of the matching re-run, so a batch only starts once the batches it skips have finished."""
import json, os, time, urllib.request
T = os.environ["APIFY_TOKEN"]; API = "https://api.apify.com/v2"
OCT = {
 "app-store":   ("WckBf1ocAvad9YfCT", ["H5F2LhiHfhsSkdtnE", "Gx3BgNFSJLdGTBZQH", "VmmIXZOuTjGFYftxS"]),
 "google-play": ("cIvzURzdWXoYbrd5G", ["KHHsswQscLF5cfV3m", "QFc9hwwPOd5P5YdnS", "LxEfDeoiIzHkwTMI5", "FUK7ts2t9mYoyse9i", "bbVVoVGGCTOiu0SbF"]),
 "playstation": ("12Db4YeqNAtk9ovjQ", ["UcfcRLfZODNYFgUaS", "qcVBTvuZu0bdcWSup", "hz02oJyRMJs3KNbCX", "VRVvy0PcQawjmswDk", "knHU8cuoDrdJ2v6jO", "5e7CDCjDgTFhfNMhk"]),
 "xbox":        ("eDY2c3sG4cwh99q0F", ["IOYAstNbgyZZaNdmz", "dVwPIBdCxc30HNynQ", "BJI3oauEcjGzewhVm", "Z1SRSfE1wmMx3AdFP"]),
 "nintendo":    ("7evW6TQxMrCdeWqR5", ["P9LJmy5flOl9XPSD1", "Ulhgqf7Ec63Iy5Bom", "CcNh8ULsPRATf472h", "jFKiLxceTEBaQFPc5"]),
 "epic":        ("bMVnZ5K6cwjYFxuuQ", ["k94BULhbnEdJGPmg9", "eUrlQe2hWH6DzTFAh", "EOYN2xaVaZjLY6JL3", "IwXNLSpLg1lNdpA6X"]),
 "gog":         ("5WeGrFRbrMQGPkgwg", ["WQ8lhMbBe6zZItIO8", "EbevAfQmPGzDDMmM6", "p9eaKfv6afed6G7wq", "2Q5jrDJd5fAVZ8pZP"]),
 "itch":        ("l7yIXTWjTL5hNJlzs", ["cVDQAhlsUJxNTK8jo"]),
 "roblox":      ("tw3gPMN3uWG0c3ray", ["tPDrVwDaJdi4h3bCu", "NHdzWj3IEIXRNciEy"]),
}
def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {T}", "Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=60).read()
    try: return json.loads(r)["data"]
    except Exception: return json.loads(r)
MAN = "manifest.json"
man = json.load(open(MAN)) if os.path.exists(MAN) else {}
def save(): json.dump(man, open(MAN, "w"), indent=1)
if not man:
    for store, (act, runs) in OCT.items():
        for rid in runs:
            r = call("GET", f"/actor-runs/{rid}")
            inp = call("GET", f"/key-value-stores/{r['defaultKeyValueStoreId']}/records/INPUT")
            man[rid] = {"store": store, "actor": act, "octDataset": r["defaultDatasetId"], "build": r["options"].get("build"),
                        "memory": r["options"].get("memoryMbytes"), "timeout": r["options"].get("timeoutSecs"),
                        "maxCharge": r["options"].get("maxTotalChargeUsd"), "input": inp, "octStatus": r["status"],
                        "octItems": call("GET", f"/datasets/{r['defaultDatasetId']}")["itemCount"], "octUsd": r.get("usageTotalUsd")}
    save()
dsmap = {v["octDataset"]: v for v in man.values()}
while True:
    pending = 0
    for rid, v in man.items():
        if v.get("newRun") and v.get("newStatus") in (None, "READY", "RUNNING"):
            d = call("GET", f"/actor-runs/{v['newRun']}"); v["newStatus"] = d["status"]; v["newUsd"] = d.get("usageTotalUsd")
            if d["status"] not in ("READY", "RUNNING"):
                v["newItems"] = call("GET", f"/datasets/{v['newDataset']}")["itemCount"]; print("done", v["store"], rid, d["status"], v["newItems"], flush=True); save()
        if v.get("newRun") and v.get("newStatus") in ("READY", "RUNNING"): pending += 1
        if not v.get("newRun"):
            skips = v["input"].get("skipDatasetIds") or []
            deps = [dsmap.get(s) for s in skips]
            if any(dep and dep.get("newStatus") in (None, "READY", "RUNNING") for dep in deps):
                pending += 1; continue
            inp = dict(v["input"])
            if skips: inp["skipDatasetIds"] = [dsmap[s]["newDataset"] if s in dsmap else s for s in skips]
            q = f"build={v['build']}&memory={v['memory']}" + (f"&timeout={v['timeout']}" if v.get("timeout") else "") + \
                (f"&maxTotalChargeUsd={v['maxCharge']}" if v.get("maxCharge") else "")
            try:
                d = call("POST", f"/acts/{v['actor']}/runs?{q}", inp)
                v.update({"newRun": d["id"], "newDataset": d["defaultDatasetId"], "newStatus": d["status"], "newInput": inp})
                print("start", v["store"], rid, "->", d["id"], d["defaultDatasetId"], flush=True)
            except Exception as ex:
                v.update({"newStatus": "START_FAILED", "error": str(ex)[:200]}); print("startfail", v["store"], rid, ex, flush=True)
            save(); pending += 1
    if pending == 0: break
    time.sleep(30)
print("ALL DONE", flush=True)
