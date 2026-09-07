#!/usr/bin/env python3
"""Generate the expanded theme blocks appended to assets/themes.css.

    python3 assets/make-themes.py            # print the generated region
    python3 assets/make-themes.py --write    # replace the region in themes.css

The ten original themes were designed and frozen by hand and this script does not
touch them; it owns everything after the GENERATED marker. Each colour is solved
rather than picked: a hue and chroma are chosen for the role, then lightness is
searched until the token clears the contrast floor in references/themes.md on its
own paper. Verify the result with assets/check-themes.py, which is the gate.
"""
from __future__ import annotations

import argparse
import io
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER = "/* ══ GENERATED THEMES — assets/make-themes.py owns everything below ══"

# Contrast targets. The floors are in references/themes.md; these aim above them so
# that rounding to hex, and the surface-2 card ground, cannot push a token under.
AIM = {"light": {"text-primary": 15.0, "text-secondary": 7.6, "text-muted": 4.7,
                 "accent-ink": 5.6, "series": 4.6},
       "dark":  {"text-primary": 15.5, "text-secondary": 7.7, "text-muted": 4.7,
                 "accent-ink": 6.2, "series": 5.6}}

# Signed lightness offsets from --bg for the non-ink furniture, per band. A light
# theme lifts the card off the page and sinks its rules; a dark theme does both by
# getting lighter, because there is nothing below black to sink into.
STACK = {"light": {"surface-1": +.022, "surface-2": -.048, "line": -.085,
                   "line-strong": -.200, "mid": -.035},
         "dark":  {"surface-1": +.030, "surface-2": +.058, "line": +.055,
                   "line-strong": +.140, "mid": +.020}}


# ── colour space ────────────────────────────────────────────────────────────
def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def oklch_to_linear(L: float, C: float, H: float) -> tuple[float, float, float]:
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l, m, s = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, \
              (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, \
              (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def oklch(L: float, C: float, H: float) -> str:
    """OKLCH -> hex, reducing chroma until the colour is inside sRGB."""
    def inside(chroma: float) -> bool:
        return all(-0.0005 <= v <= 1.0005 for v in oklch_to_linear(L, chroma, H))
    if not inside(C):
        lo, hi = 0.0, C
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(mid) else (lo, mid)
        C = lo
    rgb = oklch_to_linear(L, C, H)
    return "#" + "".join("%02x" % max(0, min(255, round(linear_to_srgb(max(0.0, min(1.0, v))) * 255)))
                         for v in rgb)


def luminance(value: str) -> float:
    r, g, b = (srgb_to_linear(int(value[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a) + 0.05, luminance(b) + 0.05
    return max(la, lb) / min(la, lb)


def solve(papers: list[str], H: float, C: float, target: float, darker: bool) -> str:
    """Search lightness until the ink clears `target` on every paper it may sit on.

    Contrast is monotonic in L on either side of the paper, so a bisection is exact
    to the hex step. `darker` picks the side: dark ink on light paper, or the reverse.
    """
    def ratio(L: float) -> float:
        ink = oklch(L, C, H)
        return min(contrast(ink, paper) for paper in papers)
    lo, hi = (0.0, 1.0) if darker else (1.0, 0.0)      # lo = most contrast
    if ratio(lo) < target:                              # unreachable: take the extreme
        return oklch(lo, C, H)
    for _ in range(48):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ratio(mid) >= target else (lo, mid)
    return oklch(lo, C, H)


# ── theme design table ──────────────────────────────────────────────────────
# paper: (L, C, H) of --bg in the theme's native band. ink: hue/chroma of body text.
# The inverse drop is derived from `flip`, the paper of the other band.
MONO = '"IBM Plex Mono","JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace'
SPECS = (
  dict(id="abacus", native="light", title="ABACUS", line="finance ledgerbook · warm bone paper + teal rule · light-native",
       paper=(.955, .008, 92), flip=(.155, .010, 92), ink=(.030, 100), accent=195, series=(195, 55, 305),
       pos=170, neg=25, radius=4, rule=1, track="-.014em", caps="uppercase", shadow="none",
       display='"IBM Plex Mono","Roboto Mono",ui-monospace,SFMono-Regular,Menlo,monospace',
       body='"IBM Plex Serif","Source Serif 4",ui-serif,Georgia,serif', label=MONO),
  dict(id="clinic", native="light", title="CLINIC", line="clinical record · cool white + cyan · light-native",
       paper=(.982, .004, 215), flip=(.175, .012, 225), ink=(.026, 235), accent=225, series=(225, 145, 25),
       pos=225, neg=25, radius=8, rule=1, track="-.016em", caps="uppercase", shadow="lift",
       display='"IBM Plex Sans","Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif',
       body='"IBM Plex Sans","Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="atlas", native="light", title="ATLAS", line="survey sheet · sand paper + slate ink · light-native",
       paper=(.945, .014, 78), flip=(.150, .012, 250), ink=(.032, 250), accent=250, series=(250, 150, 40),
       pos=250, neg=28, radius=6, rule=1, track="-.020em", caps="uppercase", shadow="none",
       display='"Spectral","Cormorant Garamond",ui-serif,Georgia,serif',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="voltage", native="dark", title="VOLTAGE", line="industrial telemetry · graphite + amber · DARK-native",
       paper=(.140, .012, 70), flip=(.955, .010, 80), ink=(.028, 75), accent=70, series=(70, 200, 320),
       pos=155, neg=25, radius=3, rule=1, track="-.010em", caps="uppercase", shadow="none",
       display='"Archivo","Roboto Condensed",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="campus", native="light", title="CAMPUS", line="academic press · ivory paper + violet · light-native",
       paper=(.965, .012, 95), flip=(.160, .014, 300), ink=(.030, 300), accent=300, series=(300, 190, 60),
       pos=190, neg=25, radius=6, rule=1, track="-.024em", caps="none", shadow="soft",
       display='"Libre Baskerville","EB Garamond",ui-serif,Georgia,serif',
       body='"EB Garamond","Libre Baskerville",ui-serif,Georgia,serif', label=MONO),
  dict(id="pitch", native="light", title="PITCH", line="scoreboard · cool grey + lime · light-native",
       paper=(.930, .006, 250), flip=(.135, .010, 250), ink=(.028, 250), accent=135, series=(135, 250, 30),
       pos=135, neg=25, radius=2, rule=2, track="-.030em", caps="uppercase", shadow="hard",
       display='"Oswald","Archivo Narrow","Roboto Condensed",system-ui,ui-sans-serif,sans-serif',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="bazaar", native="light", title="BAZAAR", line="storefront · warm blush + magenta · light-native",
       paper=(.968, .012, 40), flip=(.160, .014, 350), ink=(.032, 350), accent=350, series=(350, 200, 110),
       pos=200, neg=20, radius=16, rule=1, track="-.022em", caps="none", shadow="soft",
       display='"Nunito","Quicksand",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif',
       body='"Nunito Sans","Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="blueprint", native="light", title="BLUEPRINT", line="drafting table · cool paper + indigo · light-native",
       paper=(.958, .008, 235), flip=(.150, .016, 265), ink=(.030, 265), accent=265, series=(265, 165, 45),
       pos=265, neg=25, radius=0, rule=1, track="-.012em", caps="uppercase", shadow="none",
       display='"Space Mono","IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace',
       body='"Space Grotesk","Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="sentinel", native="dark", title="SENTINEL", line="incident desk · near-black + crimson · DARK-native",
       paper=(.120, .010, 20), flip=(.945, .006, 20), ink=(.026, 20), accent=20, series=(20, 215, 130),
       pos=150, neg=20, radius=3, rule=1, track="-.026em", caps="uppercase", shadow="ring",
       display='"Saira Condensed","Archivo","Roboto Condensed",system-ui,ui-sans-serif,sans-serif',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="assay", native="light", title="ASSAY", line="laboratory notebook · neutral paper + violet · light-native",
       paper=(.975, .003, 260), flip=(.170, .010, 285), ink=(.024, 285), accent=285, series=(285, 180, 55),
       pos=180, neg=25, radius=5, rule=1, track="-.018em", caps="uppercase", shadow="none",
       display='"Source Serif 4","Charter","Charis SIL",ui-serif,Georgia,serif',
       body='"Source Serif 4","Charter",ui-serif,Georgia,serif', label=MONO),
  dict(id="civic", native="light", title="CIVIC", line="public record · warm grey + indigo slab · light-native",
       paper=(.940, .006, 85), flip=(.145, .012, 270), ink=(.030, 270), accent=270, series=(270, 160, 35),
       pos=270, neg=25, radius=4, rule=2, track="-.020em", caps="uppercase", shadow="none",
       display='"Zilla Slab","Roboto Slab",ui-serif,Georgia,serif',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="signal", native="dark", title="SIGNAL", line="growth desk · cool black + magenta · DARK-native",
       paper=(.135, .014, 285), flip=(.965, .008, 300), ink=(.026, 300), accent=340, series=(340, 210, 120),
       pos=210, neg=15, radius=10, rule=1, track="-.028em", caps="uppercase", shadow="ring",
       display='"Poppins","Century Gothic","Futura",system-ui,ui-sans-serif,sans-serif',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="roster", native="light", title="ROSTER", line="people file · oat paper + teal · light-native",
       paper=(.952, .016, 88), flip=(.155, .012, 175), ink=(.028, 175), accent=185, series=(185, 60, 310),
       pos=185, neg=28, radius=12, rule=1, track="-.016em", caps="none", shadow="lift",
       display='"Source Sans 3","Lato",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif',
       body='"Source Sans 3","Lato",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="tide", native="light", title="TIDE", line="observation log · blue-grey paper + cyan · light-native",
       paper=(.948, .010, 220), flip=(.148, .012, 220), ink=(.028, 220), accent=210, series=(210, 130, 25),
       pos=210, neg=25, radius=8, rule=1, track="-.024em", caps="none", shadow="none",
       display='"Crimson Pro","Crimson Text",ui-serif,Georgia,serif',
       body='"Crimson Pro","Crimson Text",ui-serif,Georgia,serif', label=MONO),
  dict(id="desk", native="light", title="DESK", line="service desk · cool grey sheet + rust · light-native",
       paper=(.955, .005, 250), flip=(.150, .008, 250), ink=(.026, 250), accent=40, series=(40, 215, 145),
       pos=215, neg=15, radius=6, rule=1, track="-.018em", caps="uppercase", shadow="ring",
       display='"Barlow","IBM Plex Sans",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif',
       body='"Barlow","Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
  dict(id="flux", native="dark", title="FLUX", line="network operations · deep teal-black + lime · DARK-native",
       paper=(.128, .016, 190), flip=(.950, .008, 190), ink=(.024, 190), accent=125, series=(125, 230, 350),
       pos=125, neg=20, radius=2, rule=1, track="0", caps="uppercase", shadow="ring",
       display='"Martian Mono","Roboto Mono","IBM Plex Mono",ui-monospace,SFMono-Regular,monospace',
       body='"Inter",system-ui,-apple-system,"Segoe UI",ui-sans-serif,sans-serif', label=MONO),
)

SHADOWS = {
    "none": ("none", "none"),
    "soft": ("0 1px 2px rgba(20,18,14,.05), 0 10px 28px -20px rgba(20,18,14,.30)",
             "0 1px 2px rgba(0,0,0,.40), 0 10px 28px -18px rgba(0,0,0,.75)"),
    "lift": ("0 1px 0 rgba(16,20,30,.04), 0 6px 18px -14px rgba(16,20,30,.35)",
             "0 1px 0 rgba(255,255,255,.04), 0 6px 18px -12px rgba(0,0,0,.85)"),
    "ring": ("0 0 0 1px rgba(16,20,30,.05), 0 12px 30px -24px rgba(16,20,30,.45)",
             "0 0 0 1px rgba(255,255,255,.03), 0 18px 44px -26px rgba(0,0,0,.90)"),
    "hard": ("4px 4px 0 var(--line-strong)", "4px 4px 0 var(--line-strong)"),
}


def drop(spec: dict, band: str) -> dict[str, str]:
    """Build one full token set for `band`, solved against its own paper."""
    light = band == "light"
    aim, stack = AIM[band], STACK[band]
    L, C, H = spec["paper"] if band == spec["native"] else spec["flip"]
    bg = oklch(L, C, H)

    def shifted(delta: float, chroma: float = C) -> str:
        return oklch(max(0.0, min(1.0, L + delta)), chroma, H)

    tokens = {"bg": bg}
    for name, delta in stack.items():
        tokens[name] = shifted(delta, C * (0.9 if name == "mid" else 1.0))
    # Ink must clear its floor on the worst ground a card can present, not only on
    # --bg: a light theme's --surface-2 is darker than the page, a dark theme's is
    # lighter, and text sits on all three.
    grounds = [tokens["bg"], tokens["surface-1"], tokens["surface-2"]]
    ink_c, ink_h = spec["ink"]
    tokens["text-primary"] = solve(grounds, ink_h, ink_c, aim["text-primary"], light)
    tokens["text-secondary"] = solve(grounds, ink_h, ink_c * 1.3, aim["text-secondary"], light)
    tokens["text-muted"] = solve(grounds, ink_h, ink_c * 1.3, aim["text-muted"], light)
    accent = solve(grounds, spec["accent"], .16, aim["accent-ink"], light)
    tokens["accent"] = tokens["accent-ink"] = tokens["focus"] = accent
    for name, hue in zip(("s1", "s2", "s3"), spec["series"]):
        tokens[name] = solve(grounds, hue, .17, aim["series"], light)
    tokens["pos"] = solve(grounds, spec["pos"], .16, aim["series"], light)
    tokens["neg"] = solve(grounds, spec["neg"], .18, aim["series"], light)
    return tokens


ORDER = (("bg", "surface-1", "surface-2"), ("text-primary", "text-secondary", "text-muted"),
         ("line", "line-strong"), ("accent", "accent-ink"), ("s1", "s2", "s3"),
         ("pos", "neg", "mid"), ("focus",))


def render(spec: dict) -> str:
    native, inverse = spec["native"], "dark" if spec["native"] == "light" else "light"
    shadow_light, shadow_dark = SHADOWS[spec["shadow"]]
    shadow = {"light": shadow_light, "dark": shadow_dark}
    rule = "─" * 57
    out = [f'/* ── THEME {spec["title"]} {rule}\n   {spec["title"]} — {spec["line"]}\n'
           f'   {"─" * 73} */\n']

    def body(band: str, fonts: bool) -> str:
        tokens = drop(spec, band)
        lines = [f"  color-scheme: {band};"]
        for group in ORDER:
            lines.append("  " + " ".join(f"--{name}:{tokens[name]};" for name in group))
        if fonts:
            lines += [f'  --font-display:{spec["display"]};',
                      f'  --font-body:{spec["body"]};',
                      f'  --font-label:{spec["label"]};',
                      f'  --radius:{spec["radius"]}px; --rule:{spec["rule"]}px; '
                      f'--track-display:{spec["track"]}; --label-caps:{spec["caps"]};']
        lines.append(f'  --shadow:{shadow[band]};')
        return "\n".join(lines)

    out.append(":root{\n" + body(native, True) + "\n}\n")
    out.append(f'@media (prefers-color-scheme: {inverse}){{ :root:not([data-theme="{native}"]){{\n'
               + body(inverse, False) + "\n}}\n")
    out.append(f'[data-theme="{inverse}"]{{\n' + body(inverse, False) + "\n}\n")
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="rewrite the generated region of themes.css")
    ap.add_argument("--themes", default=os.path.join(HERE, "themes.css"))
    a = ap.parse_args()

    region = (MARKER + "\n"
              "   Sixteen subject-fitted themes, solved rather than picked. Re-run the script\n"
              "   after changing a design row; never hand-edit a value here. The contract is\n"
              "   proved by assets/check-themes.py, not by this comment.\n"
              "   ═══════════════════════════════════════════════════════════════════════ */\n\n"
              + "\n".join(render(spec) for spec in SPECS))
    if not a.write:
        sys.stdout.write(region)
        return 0
    css = io.open(a.themes, encoding="utf-8").read()
    cut = css.find(MARKER)
    io.open(a.themes, "w", encoding="utf-8").write(
        (css[:cut] if cut >= 0 else css.rstrip() + "\n\n") + region)
    print("wrote %d generated themes into %s" % (len(SPECS), a.themes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
