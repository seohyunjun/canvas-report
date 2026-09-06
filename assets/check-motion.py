#!/usr/bin/env python3
"""Verify that a report's charts actually move.

A screenshot can never answer this. `--force-prefers-reduced-motion` omits the
animation by design, and `--virtual-time-budget` freezes requestAnimationFrame,
so every trace taken that way reads a single constant value. This drives Chrome
over the DevTools protocol on a real clock instead.

    python3 assets/check-motion.py report.html

Exits non-zero if any chart never moves, or moves and never lands on its final
state. Needs the `websockets` package and a `google-chrome` on PATH.
"""
import asyncio, json, os, shutil, subprocess, sys, tempfile, urllib.request

PROBE = r"""
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const cs = [...document.querySelectorAll('canvas')].filter(c => c.__chart);
  let raf = 0; (function f(){ raf++; requestAnimationFrame(f); })();
  const H = () => document.body.scrollHeight;
  // Walk the page the way a reader does, so every chart crosses the viewport.
  for (let i = 0; i < 10; i++) { window.scrollTo(0, H() * i / 9); await sleep(420); }
  window.scrollTo(0, 0); await sleep(400);
  // __played is set by chart.play() however it was wired: this is the wiring gate.
  const wired = cs.map(c => !!c.__chart.__played);
  // Then drive each chart directly to confirm it animates and lands on 1.
  const seen = cs.map(() => new Set());
  cs.forEach(c => c.__chart.play(700));
  for (let i = 0; i < 22; i++) {
    cs.forEach((c, j) => seen[j].add(Math.round(c.__chart.t * 1000) / 1000));
    await sleep(55);
  }
  return JSON.stringify({
    raf: raf,
    reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
    charts: cs.map((c, j) => ({
      id: c.id || '(unnamed)',
      wired: wired[j],
      steps: seen[j].size,
      final: Math.round(c.__chart.t * 1000) / 1000
    }))
  });
})()
"""
async def probe(url, port):
    import websockets
    prof = tempfile.mkdtemp(prefix="cr-motion-")
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or "google-chrome"
    p = subprocess.Popen([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                          "--hide-scrollbars", "--force-device-scale-factor=1",
                          "--window-size=1240,2400", "--user-data-dir=" + prof,
                          "--remote-debugging-port=%d" % port, url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(80):
            try:
                for t in json.load(urllib.request.urlopen(
                        "http://127.0.0.1:%d/json" % port, timeout=1)):
                    if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                        ws_url = t["webSocketDebuggerUrl"]
                        break
                if ws_url:
                    break
            except Exception:
                pass
            await asyncio.sleep(.25)
        if not ws_url:
            raise SystemExit("could not reach Chrome on port %d" % port)
        async with websockets.connect(ws_url, max_size=None) as ws:
            await asyncio.sleep(.8)
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
                "expression": PROBE, "awaitPromise": True,
                "returnByValue": True, "timeout": 40000}}))
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), 60))
                if m.get("id") == 1:
                    r = m.get("result", {})
                    if "exceptionDetails" in r:
                        raise SystemExit("page threw: " + json.dumps(r["exceptionDetails"])[:400])
                    return json.loads(r["result"]["value"])
    finally:
        p.terminate()
        try:
            p.wait(5)
        except Exception:
            p.kill()
        shutil.rmtree(prof, ignore_errors=True)

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = os.path.abspath(sys.argv[1])
    if not os.path.exists(path):
        raise SystemExit("no such file: " + path)
    port = int(os.environ.get("CR_CDP_PORT", "9412"))
    res = asyncio.run(probe("file://" + path, port))

    if res["reduced"]:
        raise SystemExit("Chrome reported prefers-reduced-motion; drop that flag and rerun.")
    if res["raf"] < 10:
        raise SystemExit("requestAnimationFrame did not run (%d frames). Virtual time is on; "
                         "motion cannot be measured." % res["raf"])
    if not res["charts"]:
        raise SystemExit("no charts found on the page.")

    bad = []
    print("%-22s %-9s %-7s %-7s %s" % ("chart", "on entry", "steps", "final", "verdict"))
    for c in res["charts"]:
        able = c["steps"] > 2 and abs(c["final"] - 1) < 1e-6
        if not able:
            v = "BROKEN: " + ("never moves" if c["steps"] <= 2 else "did not finish")
        elif not c["wired"]:
            v = "static: nothing plays it"
        else:
            v = "ok"
        if v != "ok":
            bad.append(c["id"])
        print("%-22s %-9s %-7d %-7s %s"
              % (c["id"], "yes" if c["wired"] else "no", c["steps"], c["final"], v))
    print("\n%d/%d charts play once on entry and land on their final state (%d rAF frames)."
          % (len(res["charts"]) - len(bad), len(res["charts"]), res["raf"]))
    if bad:
        raise SystemExit("gate 46 fails: " + ", ".join(bad))

if __name__ == "__main__":
    main()
