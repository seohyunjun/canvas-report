#!/usr/bin/env python3
"""Generate assets/july.json (Lottie / bodymovin) from lab-data.js.

That this script has to exist is the limitation. Lottie takes no data at runtime —
the bar lengths are baked *at export time*. Change a number and the animation has to
be rebuilt, which is why the format does not belong in an analysis document.
(references/external-tools.md § C)
"""
import json, re, pathlib
here = pathlib.Path(__file__).parent
raw = (here / "lab-data.js").read_text(encoding="utf-8")
D = json.loads(re.search(r"window\.LAB_DATA=(.*);\s*$", raw, re.S).group(1))

W, H, ROW, FR, DUR = 420, 150, 26, 60, 55
mx = max(s["v"] for s in D["svc"])
RGB = [(0.71, 0.27, 0.10), (0.12, 0.44, 0.55)]

def layer(i, s):
    frac = s["v"] / mx
    start = i * 5
    return {
        "ddd": 0, "ind": i + 1, "ty": 4, "nm": s["k"], "sr": 1,
        "ks": {"o": {"a": 0, "k": 100}, "r": {"a": 0, "k": 0},
               "p": {"a": 0, "k": [12, 18 + i * ROW, 0]},
               "a": {"a": 0, "k": [0, 0, 0]},
               "s": {"a": 1, "k": [
                   {"i": {"x": [0.15], "y": [1]}, "o": {"x": [0.4], "y": [0]},
                    "t": start, "s": [0, 100, 100]},
                   {"t": start + DUR, "s": [frac * 100, 100, 100]}]}},
        "ao": 0,
        "shapes": [{"ty": "gr", "nm": "g", "it": [
            {"ty": "rc", "d": 1, "s": {"a": 0, "k": [W - 24, 17]},
             "p": {"a": 0, "k": [(W - 24) / 2, 0]}, "r": {"a": 0, "k": 5}},
            {"ty": "fl", "c": {"a": 0, "k": list(RGB[i % 2]) + [1]}, "o": {"a": 0, "k": 100}},
            {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
             "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}]}],
        "ip": 0, "op": FR * 3, "st": 0, "bm": 0}

doc = {"v": "5.12.2", "fr": FR, "ip": 0, "op": FR * 3, "w": W, "h": H,
       "nm": "july-cost", "ddd": 0, "assets": [],
       "layers": [layer(i, s) for i, s in enumerate(D["svc"])]}
out = here / "assets" / "july.json"
out.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"wrote {out} · {out.stat().st_size}B · layers={len(doc['layers'])}")
for s in D["svc"]:
    print(f"  baked {s['k']:<22} {s['v']/mx*100:5.1f}%")
