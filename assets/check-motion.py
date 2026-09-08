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
    "gsap": {"runtime": "gsap@3.15.0", "version": "3.15.0", "sha256": "92bb9a96476f983d212a2bc4f54c889039c1696dd4461d40a736860938570fbb"},
    "motion": {"runtime": "motion@11.11.17", "version": "11.11.17", "sha256": "61b3a38dabf65a31778bc7fa9e71936bfa36ec2f567e50de261b958a3037e84e"},
    "anime": {"runtime": "anime@3.2.2", "version": "3.2.2", "sha256": "bceef94f964481f7680d95e7fbbe5a8c20d3945a926a754874898a578db7c7ab"},
}

# Two viewports, because they answer two different questions. READER is a laptop
# window the report is opened into and left alone: it is the only way to see
# whether a reader meets any motion before touching the scroll wheel. TALL is
# where the wiring, engine and final-state checks below are measured, unchanged —
# the report is short enough to hold in one screen there, so nothing in those
# checks depends on where a fold happens to land. This gate used to run only in
# TALL, and so reported motion no reader at a normal window would ever see.
READER = (1280, 800)
TALL = (1240, 2400)


FIRST_SCREEN = r"""
(() => {
  const canvases = [...document.querySelectorAll('canvas')];
  return JSON.stringify({
    viewport: { width: innerWidth, height: innerHeight },
    canvases: canvases.map(canvas => ({
      id: canvas.id || "(unnamed)",
      enabled: canvas.getAttribute("data-motion-enabled"),
      played: !!(canvas.__chart && canvas.__chart.__played),
      top: Math.round(canvas.getBoundingClientRect().top + scrollY)
    }))
  });
})()
"""


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


def diagnostic(identifier, location, problem, suggested_fix, severity="error"):
    return {"severity": severity, "id": identifier, "location": location,
            "problem": problem, "suggested_fix": suggested_fix}


async def probe(url, port):
    import websockets
    profile = tempfile.mkdtemp(prefix="cr-motion-")
    chrome = os.environ.get("CR_CHROME") or shutil.which("google-chrome") or shutil.which("chromium") or "google-chrome"
    process = subprocess.Popen(
        [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", "--window-size=%d,%d" % READER,
         "--user-data-dir=" + profile, "--remote-debugging-port=%d" % port, "about:blank"],
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
            counter = [0]

            async def call(method, params=None, timeout=60):
                counter[0] += 1
                identifier = counter[0]
                await socket.send(json.dumps({"id": identifier, "method": method,
                                              "params": params or {}}))
                while True:
                    message = json.loads(await asyncio.wait_for(socket.recv(), timeout))
                    if message.get("id") == identifier:
                        if "error" in message:
                            raise RuntimeError("%s: %s" % (method, message["error"].get("message", "CDP error")))
                        return message.get("result", {})

            async def evaluate(expression):
                result = await call("Runtime.evaluate", {
                    "expression": expression, "awaitPromise": True,
                    "returnByValue": True, "timeout": 40000})
                if "exceptionDetails" in result:
                    raise RuntimeError("page threw: " + json.dumps(result["exceptionDetails"])[:400])
                return result.get("result", {}).get("value")

            async def evaluate_json(expression):
                return json.loads(await evaluate(expression))

            async def viewport(size):
                await call("Emulation.setDeviceMetricsOverride", {
                    "width": size[0], "height": size[1], "deviceScaleFactor": 1, "mobile": False})

            await call("Page.enable")
            await call("Runtime.enable")
            # Size the window before the report loads, so the first screen the
            # observer sees is the one a reader would open the file into.
            await viewport(READER)
            await call("Page.navigate", {"url": url})
            await asyncio.sleep(1.6)
            first_screen = await evaluate_json(FIRST_SCREEN)
            # Hand the rest of the checks the viewport they have always run in.
            await viewport(TALL)
            await evaluate("window.dispatchEvent(new Event('resize'))")
            await asyncio.sleep(.8)
            result = await evaluate_json(PROBE)
            result["first_screen"] = first_screen
            return result
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


def blocking(diagnostics):
    """Anything that is not explicitly a warning stops the run — the default is to fail."""
    return [item for item in diagnostics
            if not (isinstance(item, dict) and item.get("severity") == "warning")]


def first_screen_diagnostics(result, path):
    """What the reader gets on opening the file, before touching the scroll wheel.

    Motion below the fold is not a defect — on-view entry is the declared contract,
    and a Briefing leads with its masthead. It is a fact about the report the author
    should know, so it is reported as a warning and never blocks a ship.
    """
    observed = result.get("first_screen") or {}
    canvases = [item for item in observed.get("canvases", []) if item.get("enabled") == "true"]
    if not canvases or any(item.get("played") for item in canvases):
        return []
    view = observed.get("viewport", {})
    nearest = min(canvases, key=lambda item: item.get("top", 0))
    return [diagnostic("MOTION-VIEWPORT-001", path,
        "No chart with motion is on the first screen at %dx%d: the nearest starts %dpx down, "
        "so the report is still until the reader scrolls."
        % (view.get("width", 0), view.get("height", 0), nearest.get("top", 0)),
        "Keep it if the reading sequence intends it, or lift the first evidence chart above the "
        "fold; entry motion below the fold is only ever seen on the way past it.",
        severity="warning")]


def validate(result, path):
    diagnostics = first_screen_diagnostics(result, path)
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
        elif not blocking(diagnostics):
            print("Motion validation passed with warnings.")
    if blocking(diagnostics):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
