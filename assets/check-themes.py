#!/usr/bin/env python3
"""Verify every theme block in themes.css against the contrast contract.

    python3 assets/check-themes.py [--themes assets/themes.css] [--theme grid]

references/themes.md states the contract; this script is what proves it. A hand
edit that lowers a value fails here rather than in a reader's browser. Output is
the usual diagnostic envelope, so it can be piped into a run's validation log.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Contrast floors, measured against the block's own --bg. references/themes.md.
TEXT_MIN = {"text-primary": 7.0, "text-secondary": 7.0, "text-muted": 4.5, "accent-ink": 4.5}
MARK_MIN = {"s1": 3.0, "s2": 3.0, "s3": 3.0, "pos": 3.0, "neg": 3.0}
SERIES_HUE_MIN = 55.0       # degrees of OKLCH hue between any two series
SERIES_GREY_MIN = 1.18      # or this greyscale luminance ratio, for monochrome print
REQUIRED = tuple(TEXT_MIN) + tuple(MARK_MIN) + ("bg", "surface-1", "surface-2",
                                                "line", "line-strong", "accent", "mid", "focus")
SERIES = ("s1", "s2", "s3")


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(value: str) -> float:
    r, g, b = (srgb_to_linear(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a) + 0.05, luminance(b) + 0.05
    return max(la, lb) / min(la, lb)


def hue(value: str) -> float:
    r, g, b = (srgb_to_linear(c) for c in hex_to_rgb(value))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return math.degrees(math.atan2(B, A)) % 360


def hue_gap(a: str, b: str) -> float:
    d = abs(hue(a) - hue(b)) % 360
    return min(d, 360 - d)


def grey_ratio(a: str, b: str) -> float:
    la, lb = luminance(a) + 0.05, luminance(b) + 0.05
    return max(la, lb) / min(la, lb)


def blocks(css: str) -> dict[str, list[tuple[str, dict[str, str]]]]:
    """themes.css -> {theme: [(drop label, {token: hex}), ...]}"""
    out: dict[str, list[tuple[str, dict[str, str]]]] = {}
    parts = re.split(r"(?m)^/\* ── THEME ([A-Z0-9]+) ", css)
    for i in range(1, len(parts), 2):
        name, body = parts[i].lower(), parts[i + 1]
        drops = []
        for selector, decls in re.findall(r"(?m)^(?:@media[^{]*\{\s*)?([^{}\n]*?)\s*\{\n((?:\s{2}[^{}]*\n)+)", body):
            tokens = dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", decls))
            if tokens.get("bg"):
                drops.append((selector.strip() or "?", tokens))
        out[name] = drops
    return out


def check(theme: str, label: str, tokens: dict[str, str], report: list[dict[str, str]]) -> None:
    where = f"themes.css.{theme}.{label}"

    def fail(rule: str, problem: str, fix: str) -> None:
        report.append({"severity": "error", "id": rule, "location": where,
                       "problem": problem, "suggested_fix": fix})

    missing = [name for name in REQUIRED if name not in tokens]
    if missing:
        fail("THEME-TOKEN-001", "Missing tokens: " + ", ".join(missing),
             "Every drop declares the full token set; a reader's toggle must not inherit.")
        return
    paper = tokens["bg"]
    for name, floor in {**TEXT_MIN, **MARK_MIN}.items():
        ratio = contrast(tokens[name], paper)
        if ratio + 5e-3 < floor:
            rule = "THEME-CONTRAST-001" if name in TEXT_MIN else "THEME-CONTRAST-002"
            fail(rule, f"--{name} {tokens[name]} is {ratio:.2f}:1 on {paper}, below {floor}:1.",
                 "Recompute the block; do not hand-edit a single value.")
    for i, a in enumerate(SERIES):
        for b in SERIES[i + 1:]:
            gap, grey = hue_gap(tokens[a], tokens[b]), grey_ratio(tokens[a], tokens[b])
            if gap + 1e-6 < SERIES_HUE_MIN and grey + 1e-6 < SERIES_GREY_MIN:
                fail("THEME-SERIES-001",
                     f"--{a} and --{b} differ by {gap:.0f}° and {grey:.2f}× greyscale.",
                     f"Separate them by {SERIES_HUE_MIN:.0f}° of hue or {SERIES_GREY_MIN}× luminance.")
    if hue_gap(tokens["pos"], tokens["neg"]) < SERIES_HUE_MIN:
        fail("THEME-SERIES-002", "--pos and --neg are not distinguishable by hue.",
             "Direction must survive a diverging scale; widen the hue gap.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--themes", default=os.path.join(HERE, "themes.css"))
    ap.add_argument("--theme", help="check one theme instead of all of them")
    ap.add_argument("--catalogue", default=os.path.join(HERE, os.pardir, "references", "themes.json"),
                    help="cross-check the CSS against this catalogue")
    ap.add_argument("--output", help="write the diagnostic envelope here as well")
    a = ap.parse_args()

    table = blocks(io.open(a.themes, encoding="utf-8").read())
    if a.theme:
        if a.theme.lower() not in table:
            sys.exit("no theme %r in %s" % (a.theme, a.themes))
        table = {a.theme.lower(): table[a.theme.lower()]}

    report: list[dict[str, str]] = []
    for theme in sorted(table):
        drops = table[theme]
        if len(drops) != 3:
            report.append({"severity": "error", "id": "THEME-DROP-001",
                           "location": f"themes.css.{theme}",
                           "problem": f"Found {len(drops)} token drops; a theme ships exactly 3.",
                           "suggested_fix": "Ship :root, the prefers-color-scheme drop, and the data-theme drop."})
        for label, tokens in drops:
            check(theme, label, tokens, report)

    if not a.theme and os.path.isfile(a.catalogue):
        listed = {row["id"] for row in json.load(io.open(a.catalogue, encoding="utf-8"))["themes"]}
        for name in sorted(listed - set(table)):
            report.append({"severity": "error", "id": "THEME-CATALOGUE-001",
                           "location": f"references/themes.json.{name}",
                           "problem": "Catalogued theme has no token block in themes.css.",
                           "suggested_fix": "Generate the block, or drop the catalogue row."})
        for name in sorted(set(table) - listed):
            report.append({"severity": "error", "id": "THEME-CATALOGUE-002",
                           "location": f"themes.css.{name}",
                           "problem": "Theme block is not in references/themes.json, so nothing can select it.",
                           "suggested_fix": "Add the catalogue row with its axes, subjects, and baseline."})

    envelope = {"schema_version": "1.0", "themes_checked": sorted(table), "diagnostics": report}
    encoded = json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if a.output:
        io.open(a.output, "w", encoding="utf-8").write(encoded)
    print("%d themes, %d diagnostics" % (len(table), len(report)))
    for item in report:
        print("  %-20s %s %s" % (item["id"], item["location"], item["problem"]))
    return 1 if report else 0


if __name__ == "__main__":
    sys.exit(main())
