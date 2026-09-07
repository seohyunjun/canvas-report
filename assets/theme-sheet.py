#!/usr/bin/env python3
"""Render every theme against one report and compose the contact sheet.

    python3 assets/theme-sheet.py REPORT.html --output docs/themes.png

The sheet in docs/ is how a reader sees what twenty-six themes actually buy, so it
has to be regenerated whenever a theme is added or a design row changes. It takes a
report that already passed its gates, applies each theme to a copy, lays the copies
out as an iframe grid, and screenshots the grid in one pass. There is no image
library involved: Chrome composes the page, which is the same renderer the reader
uses, so a tile cannot drift from the real thing.

Requires Chrome/Chromium and the ``websockets`` dependency ``check-render.py``
already needs.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TILE_WIDTH = 440
LABEL_HEIGHT = 20
# The report renders at desktop width and is scaled into the tile, so a tile shows a
# real reading width rather than a squeezed one. FRAME_HEIGHT decides how far down
# the page a tile reaches; the first chart has to be inside it.
FRAME_WIDTH = 1200
FRAME_HEIGHT = 1180
TILE_HEIGHT = LABEL_HEIGHT + round(FRAME_HEIGHT * TILE_WIDTH / FRAME_WIDTH)

PAGE = """<!doctype html><meta charset="utf-8"><title>themes</title>
<style>
  html,body{margin:0;background:#0b0d10;font:12px/1 "DejaVu Sans",system-ui,sans-serif}
  .sheet{display:grid;grid-template-columns:repeat(%(columns)d,%(tile_w)dpx);width:max-content}
  figure{margin:0;width:%(tile_w)dpx;height:%(tile_h)dpx;overflow:hidden;position:relative;background:#0b0d10}
  figcaption{position:absolute;inset:0 0 auto 0;height:%(label)dpx;z-index:2;
             display:flex;align-items:center;gap:8px;padding:0 8px;box-sizing:border-box;
             background:#0b0d10;color:#e9edf1;letter-spacing:.02em}
  figcaption b{font-weight:700}
  figcaption span{color:#8b939c;font-size:11px}
  iframe{position:absolute;top:%(label)dpx;left:0;border:0;
         width:%(frame_w)dpx;height:%(frame_h)dpx;
         transform:scale(%(scale)s);transform-origin:0 0}
</style>
<div class="sheet">%(tiles)s</div>
"""


def tiles(themes: list[tuple[str, str, str]]) -> str:
    out = []
    for name, suits, path in themes:
        out.append(
            '<figure><figcaption><b>%s</b><span>%s</span></figcaption>'
            '<iframe scrolling="no" src="%s"></iframe></figure>'
            % (html.escape(name), html.escape(suits), html.escape(os.path.basename(path)))
        )
    return "".join(out)


async def connect(port: int):
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


async def call(socket, state, method, params=None):
    state["id"] += 1
    ident = state["id"]
    await socket.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
    while True:
        message = json.loads(await asyncio.wait_for(socket.recv(), 60))
        if message.get("id") == ident:
            if "error" in message:
                raise RuntimeError("%s: %s" % (method, message["error"].get("message", "CDP error")))
            return message.get("result", {})


async def shoot(index_path: str, width: int, height: int, port: int) -> bytes:
    profile = tempfile.mkdtemp(prefix="cr-sheet-")
    chrome = (os.environ.get("CR_CHROME") or shutil.which("google-chrome")
              or shutil.which("chromium") or "google-chrome")
    process = subprocess.Popen(
        [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         "--allow-file-access-from-files", "--force-prefers-reduced-motion",
         "--user-data-dir=" + profile, "--remote-debugging-port=%d" % port, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        socket = await connect(port)
        async with socket:
            state = {"id": 0}
            await call(socket, state, "Page.enable")
            await call(socket, state, "Emulation.setDeviceMetricsOverride",
                       {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
            await call(socket, state, "Page.navigate",
                       {"url": "file://" + urllib.parse.quote(index_path)})
            await asyncio.sleep(4.5)          # every iframe paints its canvases once
            result = await call(socket, state, "Page.captureScreenshot",
                                {"format": "png", "captureBeyondViewport": True})
            return base64.b64decode(result["data"])
    finally:
        process.terminate()
        try:
            process.wait(5)
        except Exception:
            process.kill()
        shutil.rmtree(profile, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="a built report HTML to re-theme")
    ap.add_argument("--output", default=os.path.join(ROOT, "docs", "themes.png"))
    ap.add_argument("--catalogue", default=os.path.join(ROOT, "references", "themes.json"))
    ap.add_argument("--columns", type=int, default=7)
    ap.add_argument("--port", type=int, default=9333)
    a = ap.parse_args()

    catalogue = json.load(open(a.catalogue, encoding="utf-8"))["themes"]
    work = tempfile.mkdtemp(prefix="cr-sheet-src-")
    try:
        rows = []
        for row in catalogue:
            copy = os.path.join(work, "%s.html" % row["id"])
            shutil.copyfile(a.report, copy)
            subprocess.run([sys.executable, os.path.join(HERE, "apply-theme.py"), copy, row["id"]],
                           check=True, capture_output=True, text=True)
            # A dark-native theme's :root is its dark drop; headless Chrome prefers
            # light, so without the reader's own toggle the sheet would show six
            # themes in a band they do not ship as their default.
            if row.get("native") == "dark":
                text = open(copy, encoding="utf-8").read()
                open(copy, "w", encoding="utf-8").write(text.replace("<html ", '<html data-theme="dark" ', 1))
            rows.append((row["id"], row.get("suits", "").split(",")[0], copy))
        markup = tiles(rows)
        columns = min(a.columns, len(rows))
        index = os.path.join(work, "index.html")
        open(index, "w", encoding="utf-8").write(PAGE % {
            "columns": columns, "tile_w": TILE_WIDTH, "tile_h": TILE_HEIGHT, "label": LABEL_HEIGHT,
            "frame_w": FRAME_WIDTH, "frame_h": FRAME_HEIGHT,
            "scale": round(TILE_WIDTH / FRAME_WIDTH, 5), "tiles": markup})
        height = -(-len(rows) // columns) * TILE_HEIGHT
        png = asyncio.run(shoot(index, columns * TILE_WIDTH, height, a.port))
        open(a.output, "wb").write(png)
        print("%s — %d themes, %dx%d" % (a.output, len(rows), columns * TILE_WIDTH, height))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
