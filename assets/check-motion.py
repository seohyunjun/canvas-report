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


RUNTIMES = {
    "gsap": {"runtime": "gsap@3.12.5", "version": "3.12.5", "sha256": "28033e449a31ebcc396e5be8b13b63152bf03094288fb5867034321927bce087"},
    "motion": {"runtime": "motion@11.11.17", "version": "11.11.17", "sha256": "61b3a38dabf65a31778bc7fa9e71936bfa36ec2f567e50de261b958a3037e84e"},
    "anime": {"runtime": "anime@3.2.2", "version": "3.2.2", "sha256": "bceef94f964481f7680d95e7fbbe5a8c20d3945a926a754874898a578db7c7ab"},
}


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
    kind: canvas.getAttribute("data-motion-kind"),
    trigger: canvas.getAttribute("data-motion-trigger"),
    duration: canvas.getAttribute("data-motion-duration"),
    easing: canvas.getAttribute("data-motion-easing"),
    source: canvas.getAttribute("data-motion-source"),
    integration: canvas.getAttribute("data-motion-integration"),
    runtime: canvas.__chart && canvas.__chart.__motionRuntime || null,
    hasChart: !!canvas.__chart,
    wired: !!(canvas.__chart && canvas.__chart.__played),
    before: snap(canvas),
    steps: 0,
    final: null
  }));
  const seen = results.map(() => new Set());
  canvases.forEach((canvas, index) => {
    if (results[index].enabled === "true" && typeof canvas.__reportReplay === "function") canvas.__reportReplay();
    else if (results[index].enabled === "true" && canvas.__chart &&
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
    result.runtime = chart && chart.__motionRuntime || result.runtime;
  });
  return JSON.stringify({ raf, reduced: matchMedia("(prefers-reduced-motion: reduce)").matches,
                          runtimes: [...document.querySelectorAll('script[data-canvas-report-runtime]')].map(node => ({tool:node.dataset.canvasReportRuntime,version:node.dataset.version,sha256:node.dataset.sha256})),
                          canvases: results });
})()
"""


def diagnostic(identifier, location, problem, suggested_fix):
    return {"severity": "error", "id": identifier, "location": location,
            "problem": problem, "suggested_fix": suggested_fix}


async def probe(url, port):
    import websockets
    profile = tempfile.mkdtemp(prefix="cr-motion-")
    chrome = os.environ.get("CR_CHROME") or shutil.which("google-chrome") or shutil.which("chromium") or "google-chrome"
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
        diagnostics.append(diagnostic("MOTION-TOOL-001", path,
            "Chrome reported reduced-motion mode, so animation cannot be measured.",
            "Run without a reduced-motion Chrome flag."))
    if result["raf"] < 10:
        diagnostics.append(diagnostic("MOTION-TOOL-002", path,
            "requestAnimationFrame did not advance (%d frames)." % result["raf"],
            "Disable virtual time before running this validator."))
    if not result["canvases"]:
        diagnostics.append(diagnostic("MOTION-CANVAS-001", path, "The page has no canvas elements.",
            "Add declared report canvases or remove this motion validation from the report workflow."))
    for canvas in result["canvases"]:
        location = "%s canvas#%s" % (path, canvas["id"])
        if canvas["enabled"] not in ("true", "false"):
            diagnostics.append(diagnostic("MOTION-INTENT-001", location,
                "data-motion-enabled must be exactly true or false.",
                'Set data-motion-enabled="true" for animated charts, otherwise "false".'))
        if canvas["reason"] is None:
            diagnostics.append(diagnostic("MOTION-INTENT-002", location,
                "data-motion-reason is missing.",
                'Add data-motion-reason describing why this canvas animates or is static.'))
        elif not canvas["reason"].strip():
            diagnostics.append(diagnostic("MOTION-INTENT-003", location,
                "The canvas has no motion rationale.",
                'Set a nonempty data-motion-reason explaining the enabled or static decision.'))
        if canvas["enabled"] == "true":
            if canvas["kind"] != "entry" or canvas["trigger"] != "on-view":
                diagnostics.append(diagnostic("MOTION-CONTRACT-002", location,
                    "Enabled motion is not the supported entry/on-view contract.",
                    "Rebuild from a plan using kind entry and trigger on-view."))
            try:
                duration = int(canvas["duration"])
            except (TypeError, ValueError):
                duration = 0
            if not 180 <= duration <= 1200:
                diagnostics.append(diagnostic("MOTION-CONTRACT-004", location,
                    "Enabled motion has no valid bounded duration.",
                    "Set duration_ms from 180 to 1200 and rebuild."))
            if canvas["easing"] not in ("linear", "outCubic", "inOutCubic", "outQuint", "outExpo", "outCirc", "inOutQuint"):
                diagnostics.append(diagnostic("MOTION-CONTRACT-005", location,
                    "Enabled motion does not declare a value-safe easing.",
                    "Use a non-overshooting easing from references/motion.md."))
            if canvas["source"] not in ("gsap", "motion", "anime"):
                diagnostics.append(diagnostic("MOTION-CONTRACT-006", location,
                    "Enabled motion does not identify a dedicated motion engine.",
                    "Set source_tool to GSAP, Motion, or anime.js; D3 and Plotly are visualization/state tools."))
            if canvas["integration"] == "vendored-runtime":
                expected = RUNTIMES.get(canvas["source"])
                marker = next((item for item in result.get("runtimes", []) if item.get("tool") == canvas["source"]), None)
                if not expected or canvas["runtime"] != expected["runtime"]:
                    diagnostics.append(diagnostic("MOTION-RUNTIME-001", location,
                        "Vendored motion was declared but the selected runtime did not drive the chart.",
                        "Inline the selected pinned motion engine and wire it to chart progress."))
                if not expected or not marker or marker.get("version") != expected["version"] or marker.get("sha256") != expected["sha256"]:
                    diagnostics.append(diagnostic("MOTION-RUNTIME-002", location,
                        "The vendored motion runtime marker is missing or does not match its pinned version and SHA-256.",
                        "Rebuild with the verified runtime recorded in lab/motion-engines/vendor/SHA256SUMS."))
            if not canvas["hasChart"]:
                diagnostics.append(diagnostic("MOTION-WIRING-001", location,
                    "An enabled canvas has no chart animation engine.",
                    'Attach the chart engine or declare data-motion-enabled="false" with a reason.'))
            elif not canvas["wired"]:
                diagnostics.append(diagnostic("MOTION-WIRING-002", location,
                    "The chart was not played while the reader traversed the page.",
                    "Wire chart.play() to the report's entry/reveal behavior."))
            if canvas["steps"] <= 2:
                diagnostics.append(diagnostic("MOTION-WIRING-003", location,
                    "The enabled chart did not produce multiple animation states.",
                    "Make chart.play() advance chart.t over time."))
            elif canvas["final"] != 1:
                diagnostics.append(diagnostic("MOTION-FINAL-STATE-001", location,
                    "The enabled chart ended at %s instead of 1." % canvas["final"],
                    "Ensure chart.play() lands at its final state (t === 1)."))
        elif canvas["enabled"] == "false" and canvas["before"] != canvas["after"]:
            diagnostics.append(diagnostic("MOTION-STATIC-001", location,
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
        diagnostics = [diagnostic("MOTION-TOOL-003", "check-motion.py", str(error),
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
