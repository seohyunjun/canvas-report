#!/usr/bin/env python3
"""Render a report through Chrome DevTools and validate its runtime surface.

    python3 assets/check-render.py REPORT.html [--json]

Requires Chrome/Chromium and the existing ``websockets`` dependency.
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request


SURFACE = r"""
(() => JSON.stringify({
  viewport: {width: innerWidth, height: innerHeight, scrollWidth: document.documentElement.scrollWidth},
  canvases: [...document.querySelectorAll('canvas')].map((canvas, index) => {
    const rect = canvas.getBoundingClientRect();
    return {id: canvas.id || '(canvas ' + (index + 1) + ')', left: rect.left, right: rect.right,
            top: rect.top, bottom: rect.bottom, logicalWidth: rect.width, logicalHeight: rect.height,
            backingWidth: canvas.width, backingHeight: canvas.height};
  })
}))()
"""


def diag(identifier, location, problem, suggested_fix):
    return {"severity": "error", "id": identifier, "location": location,
            "problem": problem, "suggested_fix": suggested_fix}


class DevTools:
    def __init__(self, socket):
        self.socket = socket
        self.next_id = 1
        self.exceptions = []
        self.log_errors = []
        self.failed_requests = []
        self.external_requests = []

    def event(self, message):
        method = message.get("method")
        params = message.get("params", {})
        if method == "Runtime.exceptionThrown":
            details = params.get("exceptionDetails", {})
            self.exceptions.append(details.get("text") or details.get("exception", {}).get("description") or "JavaScript exception")
        elif method == "Log.entryAdded" and params.get("entry", {}).get("level") in ("error", "warning"):
            entry = params["entry"]
            self.log_errors.append(entry.get("text", "browser log error"))
        elif method == "Network.loadingFailed":
            self.failed_requests.append(params.get("errorText", "network request failed"))
        elif method == "Network.requestWillBeSent":
            url = params.get("request", {}).get("url", "")
            if url and not url.startswith(("file:", "data:", "about:")):
                self.external_requests.append(url)

    async def call(self, method, params=None):
        ident = self.next_id
        self.next_id += 1
        await self.socket.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
        while True:
            message = json.loads(await asyncio.wait_for(self.socket.recv(), 45))
            if message.get("id") == ident:
                if "error" in message:
                    raise RuntimeError("%s: %s" % (method, message["error"].get("message", "CDP error")))
                return message.get("result", {})
            self.event(message)

    async def evaluate(self, expression):
        result = await self.call("Runtime.evaluate", {"expression": expression, "awaitPromise": True,
                                                       "returnByValue": True, "timeout": 40000})
        if "exceptionDetails" in result:
            raise RuntimeError("page evaluation failed")
        return result["result"].get("value")


async def connect(port):
    import websockets
    for _ in range(80):
        try:
            pages = json.load(urllib.request.urlopen("http://127.0.0.1:%d/json" % port, timeout=1))
            url = next((page.get("webSocketDebuggerUrl") for page in pages
                        if page.get("type") == "page" and page.get("webSocketDebuggerUrl")), None)
            if url:
                return await websockets.connect(url, max_size=None)
        except Exception:
            pass
        await asyncio.sleep(.25)
    raise RuntimeError("could not reach Chrome on port %d" % port)


async def inspect(path, port):
    profile = tempfile.mkdtemp(prefix="cr-render-")
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or "google-chrome"
    process = subprocess.Popen([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                                "--user-data-dir=" + profile, "--remote-debugging-port=%d" % port,
                                "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        socket = await connect(port)
        async with socket:
            cdp = DevTools(socket)
            for method in ("Runtime.enable", "Log.enable", "Network.enable", "Page.enable"):
                await cdp.call(method)
            url = "file://" + urllib.parse.quote(path)
            await cdp.call("Page.navigate", {"url": url})
            await asyncio.sleep(1)
            results = {}
            for theme in ("normal", "dark"):
                await cdp.call("Emulation.setEmulatedMedia", {"media": "screen", "features": [
                    {"name": "prefers-color-scheme", "value": "dark" if theme == "dark" else "light"}]})
                await cdp.evaluate("document.documentElement.setAttribute('data-theme', 'dark')" if theme == "dark"
                                   else "document.documentElement.removeAttribute('data-theme')")
                await asyncio.sleep(.1)
                for width in (1240, 768, 500):
                    await cdp.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": 900,
                        "deviceScaleFactor": 1, "mobile": False})
                    await cdp.evaluate("window.dispatchEvent(new Event('resize'))")
                    await asyncio.sleep(.15)
                    results[(theme, width, 1)] = json.loads(await cdp.evaluate(SURFACE))
            await cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1240, "height": 900,
                                                                     "deviceScaleFactor": 1, "mobile": False})
            await asyncio.sleep(.15)
            baseline = json.loads(await cdp.evaluate(SURFACE))
            await cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1240, "height": 900,
                                                                     "deviceScaleFactor": 2, "mobile": False})
            await cdp.evaluate("window.dispatchEvent(new Event('resize'))")
            await asyncio.sleep(.25)
            dpr_two = json.loads(await cdp.evaluate(SURFACE))
            await asyncio.sleep(.15)
            dpr_two_repeat = json.loads(await cdp.evaluate(SURFACE))
            return results, baseline, dpr_two, dpr_two_repeat, cdp
    finally:
        process.terminate()
        try:
            process.wait(5)
        except Exception:
            process.kill()
        shutil.rmtree(profile, ignore_errors=True)


def validate(path, rendered, baseline, dpr_two, dpr_two_repeat, cdp):
    diagnostics = []
    for text in cdp.exceptions:
        diagnostics.append(diag("render.runtime-exception", path, "Page JavaScript exception: " + text,
                                "Fix the reported JavaScript exception before publishing."))
    for text in cdp.log_errors:
        diagnostics.append(diag("render.browser-log", path, "Browser error: " + text,
                                "Fix the browser error; do not ship console errors."))
    for text in cdp.failed_requests:
        diagnostics.append(diag("render.request-failed", path, "A resource request failed: " + text,
                                "Bundle the resource in the report or correct its URL."))
    for url in sorted(set(cdp.external_requests)):
        diagnostics.append(diag("render.external-request", path, "Report requested an external URL: " + url,
                                "Inline or locally bundle this resource; generated reports make zero external requests."))
    for (theme, width, _), surface in rendered.items():
        view = surface["viewport"]
        location = "%s %s theme at %dpx" % (path, theme, width)
        if view["scrollWidth"] > view["width"] + 1:
            diagnostics.append(diag("render.horizontal-overflow", location,
                "Document scroll width is %dpx but viewport is %dpx." % (view["scrollWidth"], view["width"]),
                "Make report content responsive so it does not overflow horizontally."))
        for canvas in surface["canvases"]:
            canvas_location = "%s canvas#%s" % (location, canvas["id"])
            if canvas["logicalWidth"] <= 0 or canvas["logicalHeight"] <= 0:
                diagnostics.append(diag("render.canvas-empty", canvas_location, "Canvas has zero visible bounds.",
                                        "Give the canvas a positive rendered width and height."))
            if canvas["left"] < -1 or canvas["right"] > view["width"] + 1:
                diagnostics.append(diag("render.canvas-out-of-bounds", canvas_location,
                    "Canvas horizontal bounds %.1f..%.1f exceed the viewport." % (canvas["left"], canvas["right"]),
                    "Constrain the canvas to its responsive container."))
    first = {item["id"]: item for item in baseline["canvases"]}
    second = {item["id"]: item for item in dpr_two["canvases"]}
    repeated = {item["id"]: item for item in dpr_two_repeat["canvases"]}
    for identifier, one in first.items():
        two = second.get(identifier)
        again = repeated.get(identifier)
        location = "%s canvas#%s at DPR 2" % (path, identifier)
        if not two or not again:
            diagnostics.append(diag("render.canvas-dpr-missing", location, "Canvas disappeared after DPR changed.",
                                    "Keep canvas elements stable during resize handling."))
            continue
        if abs(one["logicalWidth"] - two["logicalWidth"]) > 1 or abs(one["logicalHeight"] - two["logicalHeight"]) > 1:
            diagnostics.append(diag("render.canvas-logical-unstable", location,
                "Canvas logical size changed when DPR changed.", "Keep CSS canvas dimensions independent of device pixel ratio."))
        if two["backingWidth"] <= 0 or two["backingHeight"] <= 0 or two["backingWidth"] != again["backingWidth"] or two["backingHeight"] != again["backingHeight"]:
            diagnostics.append(diag("render.canvas-backing-unstable", location,
                "Canvas backing dimensions are invalid or changed between stable DPR 2 samples.",
                "Resize the backing store once from the current logical size and DPR."))
    return diagnostics


def main():
    json_output = "--json" in sys.argv[1:]
    args = [arg for arg in sys.argv[1:] if arg != "--json"]
    try:
        if len(args) != 1:
            raise ValueError("usage: check-render.py REPORT.html [--json]")
        path = os.path.abspath(args[0])
        if not os.path.isfile(path):
            raise ValueError("no such file: " + path)
        rendered, baseline, dpr_two, repeated, cdp = asyncio.run(inspect(path, int(os.environ.get("CR_CDP_PORT", "9413"))))
        diagnostics = validate(path, rendered, baseline, dpr_two, repeated, cdp)
    except (OSError, RuntimeError, ValueError) as error:
        diagnostics = [diag("render.validator-failed", "check-render.py", str(error),
                            "Install Chrome and the websockets dependency, then rerun.")]
    if json_output:
        print(json.dumps({"diagnostics": diagnostics}, indent=2))
    elif diagnostics:
        for item in diagnostics:
            print("%s %s: %s\n  Fix: %s" % (item["severity"].upper(), item["location"], item["problem"], item["suggested_fix"]))
    else:
        print("Render validation passed.")
    if diagnostics:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
