"""Download each store's re-run datasets into the same batch layout as October and run the repo's
own tools/<store>/merge.py (+ fix_free.py) + derive_tags.py. Output: <store>/games.tagged.json"""
import json, os, sys, subprocess, urllib.request, shutil
T = os.environ["APIFY_TOKEN"]; API = "https://api.apify.com/v2"; TOOLS = "/workspace/anygame-data/tools"
R = os.path.dirname(os.path.abspath(__file__))
BATCH = {"H5F2LhiHfhsSkdtnE": "us-gb-ca", "Gx3BgNFSJLdGTBZQH": "de-fr", "VmmIXZOuTjGFYftxS": "jp-au",
 "KHHsswQscLF5cfV3m": "us", "QFc9hwwPOd5P5YdnS": "us2", "LxEfDeoiIzHkwTMI5": "gb-ca", "FUK7ts2t9mYoyse9i": "de-fr", "bbVVoVGGCTOiu0SbF": "jp-au",
 "UcfcRLfZODNYFgUaS": "us", "qcVBTvuZu0bdcWSup": "us2", "hz02oJyRMJs3KNbCX": "us3", "VRVvy0PcQawjmswDk": "gb-ca", "knHU8cuoDrdJ2v6jO": "de-fr", "5e7CDCjDgTFhfNMhk": "jp-au",
 "IOYAstNbgyZZaNdmz": "us", "dVwPIBdCxc30HNynQ": "gb-ca", "BJI3oauEcjGzewhVm": "de-fr", "Z1SRSfE1wmMx3AdFP": "jp-au",
 "P9LJmy5flOl9XPSD1": "us", "Ulhgqf7Ec63Iy5Bom": "gb-ca", "CcNh8ULsPRATf472h": "de-fr", "jFKiLxceTEBaQFPc5": "jp-au",
 "k94BULhbnEdJGPmg9": "us", "eUrlQe2hWH6DzTFAh": "gb-ca", "EOYN2xaVaZjLY6JL3": "de-fr", "IwXNLSpLg1lNdpA6X": "jp-au",
 "WQ8lhMbBe6zZItIO8": "us", "EbevAfQmPGzDDMmM6": "gb-ca", "p9eaKfv6afed6G7wq": "de-fr", "2Q5jrDJd5fAVZ8pZP": "jp-au",
 "cVDQAhlsUJxNTK8jo": "full", "tPDrVwDaJdi4h3bCu": "full", "NHdzWj3IEIXRNciEy": "topup"}
TOOLDIR = {"app-store": "app-store", "google-play": "google-play", "playstation": "playstation", "xbox": "xbox", "nintendo": "nintendo",
           "epic": "epic", "gog": "gog", "itch": "itch", "roblox": "roblox"}
def get(path, raw=False):
    r = urllib.request.urlopen(urllib.request.Request(API + path, headers={"Authorization": f"Bearer {T}"}), timeout=300).read()
    return r if raw else json.loads(r)
man = json.load(open(os.path.join(R, "manifest.json")))
only = sys.argv[1:]
for store in TOOLDIR:
    if only and store not in only: continue
    runs = [(rid, v) for rid, v in man.items() if v["store"] == store]
    if any(v.get("newStatus") in (None, "READY", "RUNNING") for _, v in runs): print(store, "still running"); continue
    sd = os.path.join(R, store); os.makedirs(sd, exist_ok=True)
    batches = []
    for rid, v in runs:
        b = BATCH[rid]; bd = os.path.join(sd, f"anygame-appstore-catalog-batch-{b}" if store == "app-store" else b); os.makedirs(bd, exist_ok=True)
        if v.get("newItems"):
            f = os.path.join(bd, "games.json")
            if not os.path.exists(f):
                open(f, "wb").write(get(f"/datasets/{v['newDataset']}/items?clean=1&format=json", raw=True))
            try:
                kv = get(f"/actor-runs/{v['newRun']}")["data"]["defaultKeyValueStoreId"]
                open(os.path.join(bd, "seen-elsewhere.json"), "wb").write(get(f"/key-value-stores/{kv}/records/SEEN_ELSEWHERE", raw=True))
            except Exception: pass
            batches.append((b, bd))
        else:
            print(store, rid, "no items", v.get("newStatus"))
    out = os.path.join(sd, "games.json"); tagged = os.path.join(sd, "games.tagged.json")
    t = os.path.join(TOOLS, TOOLDIR[store])
    if store == "app-store":
        md = os.path.join(sd, "merged"); os.makedirs(md, exist_ok=True)
        subprocess.run([sys.executable, os.path.join(t, "merge.py")], cwd=md, check=True)  # reads ../anygame-appstore-catalog-batch-*/games.json
        shutil.copy(os.path.join(md, "games.json"), out)
    elif store == "google-play":
        subprocess.run([sys.executable, os.path.join(t, "merge.py"), out] + [f"{b}={bd}/games.json" for b, bd in batches], check=True)
    elif store in ("itch",):
        shutil.copy(os.path.join(batches[0][1], "games.json"), out)
    elif store == "roblox":
        seen, L = set(), []
        for b, bd in batches:
            for g in json.load(open(os.path.join(bd, "games.json"))):
                if g["id"] not in seen: seen.add(g["id"]); L.append(g)
        json.dump(L, open(out, "w"), ensure_ascii=False)
    else:
        if store == "xbox": subprocess.run([sys.executable, os.path.join(t, "fix_free.py")] + [f"{bd}/games.json" for _, bd in batches], check=True, cwd="/workspace/apify-actor-replacements")
        subprocess.run([sys.executable, os.path.join(t, "merge.py"), out] + [f"{b}={bd}" for b, bd in batches], check=True)
        if store == "epic": subprocess.run([sys.executable, os.path.join(t, "fix_free.py"), out], check=True)
    subprocess.run([sys.executable, os.path.join(t, "derive_tags.py"), out, tagged], check=True, cwd=sd)
    print(store, "OK", len(json.load(open(tagged))))
