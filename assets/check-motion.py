#!/usr/bin/env python3
"""Validate declared canvas motion in a report.

    python3 assets/check-motion.py report.html [--json]

Each canvas must declare ``data-motion-enabled="true|false"`` and
``data-motion-reason``.  Enabled charts must be wired, animate, and finish;
disabled charts must stay visually static and explain why.
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request


PROBE = r"""
(async () => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const canvases = [...document.querySelectorAll('canvas')];
  const snap = canvas => {
    try { return canvas.toDataURL(); } catch (_) { return null; }
  };
  let raf = 0; (function frame() { raf++; requestAnimationFrame(frame); })();
  const height = () => document.body.scrollHeight;
  for (let i = 0; i < 10; i++) {
    window.scrollTo(0, height() * i / 9); await sleep(420);
  }
  window.scrollTo(0, 0); await sleep(400);
  const results = canvases.map(canvas => ({
    id: canvas.id || "(unnamed)",
    enabled: canvas.getAttribute("data-motion-enabled"),
    reason: canvas.getAttribute("data-motion-reason"),
    hasChart: !!canvas.__chart,
    wired: !!(canvas.__chart && canvas.__chart.__played),
    before: snap(canvas),
    steps: 0,
    final: null
  }));
  const seen = results.map(() => new Set());
  canvases.forEach((canvas, index) => {
    if (results[index].enabled === "true" && canvas.__chart &&
        typeof canvas.__chart.play === "function") canvas.__chart.play(700);
  });
  for (let i = 0; i < 22; i++) {
    canvases.forEach((canvas, index) => {
      if (canvas.__chart) seen[index].add(Math.round(canvas.__chart.t * 1000) / 1000);
    });
    await sleep(55);
  }
  results.forEach((result, index) => {
    const chart = canvases[index].__chart;
    result.after = snap(canvases[index]);
    result.steps = seen[index].size;
    result.final = chart ? Math.round(chart.t * 1000) / 1000 : null;
  });
  return JSON.stringify({ raf, reduced: matchMedia("(prefers-reduced-motion: reduce)").matches,
                          canvases: results });
})()
"""


def diagnostic(identifier, location, problem, suggested_fix):
    return {"severity": "error", "id": identifier, "location": location,
            "problem": problem, "suggested_fix": suggested_fix}


async def probe(url, port):
    import websockets
    profile = tempfile.mkdtemp(prefix="cr-motion-")
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or "google-chrome"
    process = subprocess.Popen(
        [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", "--window-size=1240,2400",
         "--user-data-dir=" + profile, "--remote-debugging-port=%d" % port, url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(80):
            try:
                pages = json.load(urllib.request.urlopen(
                    "http://127.0.0.1:%d/json" % port, timeout=1))
                ws_url = next((page.get("webSocketDebuggerUrl") for page in pages
                               if page.get("type") == "page" and page.get("webSocketDebuggerUrl")),
                              None)
                if ws_url:
                    break
            except Exception:
                pass
            await asyncio.sleep(.25)
        if not ws_url:
            raise RuntimeError("could not reach Chrome on port %d" % port)
        async with websockets.connect(ws_url, max_size=None) as socket:
            await asyncio.sleep(.8)
            await socket.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
                "expression": PROBE, "awaitPromise": True, "returnByValue": True,
                "timeout": 40000}}))
            while True:
                message = json.loads(await asyncio.wait_for(socket.recv(), 60))
                if message.get("id") == 1:
                    result = message.get("result", {})
                    if "exceptionDetails" in result:
                        raise RuntimeError("page threw: " +
                                           json.dumps(result["exceptionDetails"])[:400])
                    return json.loads(result["result"]["value"])
    finally:
        process.terminate()
        try:
            process.wait(5)
        except Exception:
            process.kill()
        shutil.rmtree(profile, ignore_errors=True)


def parse_args(argv):
    json_output = "--json" in argv
    args = [arg for arg in argv if arg != "--json"]
    if len(args) != 1:
        raise ValueError("usage: check-motion.py REPORT.html [--json]")
    return args[0], json_output


def validate(result, path):
    diagnostics = []
    if result["reduced"]:
        diagnostics.append(diagnostic("motion.reduced-mode", path,
            "Chrome reported reduced-motion mode, so animation cannot be measured.",
            "Run without a reduced-motion Chrome flag."))
    if result["raf"] < 10:
        diagnostics.append(diagnostic("motion.raf-unavailable", path,
            "requestAnimationFrame did not advance (%d frames)." % result["raf"],
            "Disable virtual time before running this validator."))
    if not result["canvases"]:
        diagnostics.append(diagnostic("motion.no-canvas", path, "The page has no canvas elements.",
            "Add declared report canvases or remove this motion validation from the report workflow."))
    for canvas in result["canvases"]:
        location = "%s canvas#%s" % (path, canvas["id"])
        if canvas["enabled"] not in ("true", "false"):
            diagnostics.append(diagnostic("motion.declaration-missing", location,
                "data-motion-enabled must be exactly true or false.",
                'Set data-motion-enabled="true" for animated charts, otherwise "false".'))
        if canvas["reason"] is None:
            diagnostics.append(diagnostic("motion.reason-missing", location,
                "data-motion-reason is missing.",
                'Add data-motion-reason describing why this canvas animates or is static.'))
        elif not canvas["reason"].strip():
            diagnostics.append(diagnostic("motion.reason-empty", location,
                "The canvas has no motion rationale.",
                'Set a nonempty data-motion-reason explaining the enabled or static decision.'))
        if canvas["enabled"] == "true":
            if not canvas["hasChart"]:
                diagnostics.append(diagnostic("motion.engine-missing", location,
                    "An enabled canvas has no chart animation engine.",
                    'Attach the chart engine or declare data-motion-enabled="false" with a reason.'))
            elif not canvas["wired"]:
                diagnostics.append(diagnostic("motion.entry-not-wired", location,
                    "The chart was not played while the reader traversed the page.",
                    "Wire chart.play() to the report's entry/reveal behavior."))
            if canvas["steps"] <= 2:
                diagnostics.append(diagnostic("motion.never-moves", location,
                    "The enabled chart did not produce multiple animation states.",
                    "Make chart.play() advance chart.t over time."))
            elif canvas["final"] != 1:
                diagnostics.append(diagnostic("motion.does-not-finish", location,
                    "The enabled chart ended at %s instead of 1." % canvas["final"],
                    "Ensure chart.play() lands at its final state (t === 1)."))
        elif canvas["enabled"] == "false" and canvas["before"] != canvas["after"]:
            diagnostics.append(diagnostic("motion.static-changed", location,
                "A canvas declared static changed while the page was observed.",
                'Stop its animation or declare data-motion-enabled="true".'))
    return diagnostics


def main():
    try:
        report, json_output = parse_args(sys.argv[1:])
        path = os.path.abspath(report)
        if not os.path.isfile(path):
            raise ValueError("no such file: " + path)
        result = asyncio.run(probe("file://" + path, int(os.environ.get("CR_CDP_PORT", "9412"))))
        diagnostics = validate(result, path)
    except (OSError, RuntimeError, ValueError) as error:
        diagnostics = [diagnostic("motion.validator-failed", "check-motion.py", str(error),
                                  "Install Chrome and the websockets dependency, then rerun.")]
        json_output = "--json" in sys.argv[1:]
    if json_output:
        print(json.dumps({"diagnostics": diagnostics}, indent=2))
    else:
        for item in diagnostics:
            print("%s %s: %s\n  Fix: %s" %
                  (item["severity"].upper(), item["location"], item["problem"],
                   item["suggested_fix"]))
        if not diagnostics:
            print("Motion validation passed.")
    if diagnostics:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
