#!/usr/bin/env python3
"""Inventory what the pinned motion runtimes actually expose.

The engine sites document whatever version is current; this repo vendors fixed ones. Run this to
read the surface out of the pinned files themselves, offline, so `docs/api-surface.md` cites the
bundle rather than the marketing page.

  python3 lab/motion-engines/probe-api.py --output docs/api-surface.json
  python3 lab/motion-engines/probe-api.py --expect lab/motion-engines/docs/api-surface.json
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERSION = "1.0"
# Loaded into the probe page. The GSAP entry is the all-in-one bundle, which contains the
# core: loading the core as well would put a second gsap on window and the inventory would
# read whichever won.
RUNTIMES = ("gsap-all-3.15.0.min.js", "motion-11.11.17.js", "anime-3.2.2.min.js",
            "d3-7.9.0.min.js")
# Hashed and read as text, never loaded. The core is here so the catalogue can show which
# names live only in the bundle — the answer is all of them.
SCAN_ONLY = ("gsap-3.15.0.min.js",)
GSAP_PLUGINS = ("ScrollTrigger", "ScrollSmoother", "ScrollToPlugin", "SplitText",
                "ScrambleTextPlugin", "TextPlugin", "DrawSVGPlugin", "MorphSVGPlugin",
                "MotionPathPlugin", "MotionPathHelper", "Flip", "Draggable", "InertiaPlugin",
                "Observer", "Physics2DPlugin", "PhysicsPropsPlugin", "GSDevTools",
                "EaselPlugin", "PixiPlugin", "CustomEase", "CustomWiggle", "CustomBounce",
                "CSSRulePlugin", "EasePack", "RoughEase", "SlowMo", "ExpoScaleEase")

# Names each tool's own site documents today. A false here is the interesting case: the site
# describes it, the pinned build does not contain the identifier at all.
DOCUMENTED = {
    # Every plugin name, asked of both GSAP files. The core answers false to all of them and
    # the bundle answers true to all of them, which is the whole distinction between the two.
    "gsap-3.15.0.min.js": GSAP_PLUGINS + ("timeScale", "killTweensOf", "quickTo", "matchMedia"),
    "gsap-all-3.15.0.min.js": GSAP_PLUGINS + ("timeScale", "killTweensOf", "quickTo", "matchMedia"),
    "motion-11.11.17.js": ("visualDuration", "restSpeed", "restDelta", "stiffness", "damping",
                           "bounce", "repeatType", "animateMini", "inView", "scroll", "stagger"),
    "anime-3.2.2.min.js": ("animate", "createTimeline", "createTimer", "createDraggable",
                           "createScope", "createSpring", "onScroll", "morphTo", "createDrawable",
                           "createMotionPath", "splitText", "stagger", "timeline", "remove"),
    "d3-7.9.0.min.js": ("easeVarying", "textTween", "interrupt", "attrTween", "styleTween"),
}

INVENTORY = r"""
function sorted(o){ try { return Object.keys(o).sort(); } catch (e) { return null; } }
function has(o, names){ var r = {}; names.forEach(function (n) { r[n] = !!(o && typeof o[n] !== 'undefined'); }); return r; }
var out = {};

if (window.gsap) {
  var eases = [];
  ['none','linear','power0','power1','power2','power3','power4','quad','cubic','quart','quint',
   'strong','back','bounce','circ','elastic','expo','sine','steps','slow','rough','expoScale'
  ].forEach(function (n) {
    ['', '.in', '.out', '.inOut'].forEach(function (s) {
      try { if (gsap.parseEase(n + s)) eases.push(n + s); } catch (e) {}
    });
  });
  var parametric = {};
  ['back.out(1.7)', 'elastic.out(1,0.3)', 'steps(12)'].forEach(function (n) {
    try { parametric[n] = !!gsap.parseEase(n); } catch (e) { parametric[n] = false; }
  });
  // Loading a plugin file is not registering it. Read the surface either side of the call,
  // because gsap.plugins never names most of them and the eases only resolve afterwards.
  var PLUGIN_NAMES = ['ScrollTrigger', 'ScrollSmoother', 'ScrollToPlugin', 'SplitText', 'ScrambleTextPlugin', 'TextPlugin', 'DrawSVGPlugin', 'MorphSVGPlugin', 'MotionPathPlugin', 'MotionPathHelper', 'Flip', 'Draggable', 'InertiaPlugin', 'Observer', 'Physics2DPlugin', 'PhysicsPropsPlugin', 'GSDevTools', 'EaselPlugin', 'PixiPlugin', 'CustomEase', 'CustomWiggle', 'CustomBounce', 'CSSRulePlugin', 'EasePack', 'RoughEase', 'SlowMo', 'ExpoScaleEase'];
  function easeReport() {
    var r = {};
    ['none','linear','power1','power2','power3','power4','back','bounce','circ','elastic','expo',
     'sine','steps(12)','rough','slow','expoScale(1,2)'].forEach(function (n) {
      try { r[n] = typeof gsap.parseEase(n) === 'function'; } catch (e) { r[n] = false; }
    });
    return r;
  }
  var onWindow = PLUGIN_NAMES.filter(function (n) { return typeof window[n] !== 'undefined'; });
  var before = {plugins: sorted(gsap.plugins), globals: Object.keys(gsap.core.globals()).length,
                eases: easeReport()};
  onWindow.forEach(function (n) { try { gsap.registerPlugin(window[n]); } catch (e) {} });
  var after = {plugins: sorted(gsap.plugins), globals: Object.keys(gsap.core.globals()).length,
               eases: easeReport()};
  out.gsap_plugins = {
    on_window: onWindow,
    absent_from_window: PLUGIN_NAMES.filter(function (n) { return typeof window[n] === 'undefined'; }),
    before_register: before,
    after_register: after
  };

  out.gsap = {
    version: gsap.version,
    api: sorted(gsap),
    utils: sorted(gsap.utils),
    eases: eases,
    parametric_eases: parametric,
    default_ease: (function () {
      try { return gsap.defaults().ease === gsap.parseEase('power1.out') ? 'power1.out' : 'other'; }
      catch (e) { return 'unreadable'; }
    })(),
    plugins_present: onWindow.slice().sort()
  };
}

if (window.Motion) {
  var CONTROLS = ['play', 'pause', 'stop', 'cancel', 'complete', 'then', 'time', 'speed', 'duration'];
  function controls(subject, keyframes, options) {
    try {
      var a = keyframes === null ? Motion.animate(subject, 1, options)
                                 : Motion.animate(subject, keyframes, options);
      var names = CONTROLS.filter(function (k) { return typeof a[k] !== 'undefined'; });
      a.stop();
      return names;
    } catch (e) { return ['<error: ' + e.message + '>']; }
  }
  var probeElement = document.createElement('div');
  document.body.appendChild(probeElement);
  out.motion = {
    api: sorted(Motion),
    animate_controls_number: controls(0, null, { duration: 0.01 }),
    animate_controls_element: controls(probeElement, { opacity: [0, 1] }, { duration: 0.01 }),
    named_easings: sorted(Motion).filter(function (k) {
      return /^(linear|anticipate|ease(In|Out|InOut)|circ(In|Out|InOut)|back(In|Out|InOut))$/.test(k);
    })
  };
}

if (window.anime) {
  out.anime = {
    version: anime.version,
    api: sorted(anime),
    easing_names: sorted(anime.easing || {}),
    penner_easings: (typeof anime.penner === 'object' && anime.penner) ? sorted(anime.penner) : null,
    v4_names_present: ['animate','createTimeline','createTimer','createDraggable','createScope',
                       'createSpring','onScroll','morphTo','createDrawable','createMotionPath','utils'
    ].filter(function (k) { return typeof anime[k] !== 'undefined'; })
  };
}

if (window.BUILDER_EASE) {
  var resolved = {};
  Object.keys(BUILDER_EASE).forEach(function (tool) {
    var names = Object.assign({ '<control>': tool === 'motion' ? 'nonsense-ease' : 'nonsenseEase' },
                              BUILDER_EASE[tool]);
    resolved[tool] = {};
    Object.keys(names).forEach(function (planName) {
      var value = names[planName];
      try {
        if (tool === 'gsap') { resolved[tool][planName] = typeof gsap.parseEase(value) === 'function'; }
        else if (tool === 'motion') {
          var a = Motion.animate(0, 1, { duration: 0.01, ease: value }); a.stop();
          resolved[tool][planName] = true;
        } else {
          var target = { t: 0 };
          anime({ targets: target, t: 1, duration: 10, easing: value, autoplay: false });
          anime.remove(target);
          resolved[tool][planName] = true;
        }
      } catch (e) { resolved[tool][planName] = false; }
    });
  });
  out.builder_easings_resolve = resolved;
}

if (window.d3) {
  var t = d3.select(document.body).transition();
  out.d3 = {
    version: d3.version,
    eases: sorted(d3).filter(function (k) { return /^ease/.test(k); }),
    transition_api: ['duration','delay','ease','easeVarying','attr','attrTween','style','styleTween',
                     'text','textTween','tween','remove','on','end','selection','transition'
    ].filter(function (k) { return typeof t[k] === 'function'; }),
    selection_interrupt: typeof d3.select(document.body).interrupt === 'function',
    join_api: has(d3.select(document.body).selectAll('nothing'), ['data', 'join', 'enter', 'exit'])
  };
  t.duration(0);
}

document.getElementById('out').textContent = JSON.stringify(out);
"""


EASE_MAP = re.compile(r"function (gsap|motion|anime)Ease\(name\)\{return (\{.*?\})\[name\]")


def builder_ease_maps(builder: Path) -> dict[str, str]:
    """The plan-easing → engine-easing tables, read from the builder so there is one source."""
    if not builder.is_file():
        return {}
    text = builder.read_text(encoding="utf-8")
    return {tool: literal for tool, literal in EASE_MAP.findall(text)}


def build_page(vendor: Path, files: list[str], ease_maps: dict[str, str]) -> str:
    scripts = "\n".join(
        '<script src="file://%s"></script>' % (vendor / name) for name in files
    )
    declared = ""
    if ease_maps:
        declared = "<script>var BUILDER_EASE = {%s};</script>\n" % ",".join(
            "%s:%s" % (tool, literal) for tool, literal in sorted(ease_maps.items()))
    return ("<!doctype html><meta charset=utf-8><body><pre id=out></pre>\n"
            + scripts + "\n" + declared + "<script>\n" + INVENTORY + "\n</script></body>\n")


def probe(vendor: Path, builder: Path) -> dict:
    files = [name for name in RUNTIMES if (vendor / name).is_file()]
    if not files:
        raise SystemExit("no pinned runtime found under %s" % vendor)
    chrome = (os.environ.get("CR_CHROME") or shutil.which("google-chrome")
              or shutil.which("chromium") or "google-chrome")
    workspace = Path(tempfile.mkdtemp(prefix="cr-probe-"))
    page = workspace / "probe.html"
    page.write_text(build_page(vendor, files, builder_ease_maps(builder)), encoding="utf-8")
    try:
        dom = subprocess.run(
            [chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--user-data-dir=" + str(workspace / "profile"),
             "--allow-file-access-from-files", "--virtual-time-budget=5000",
             "--dump-dom", "file://" + str(page)],
            capture_output=True, text=True, timeout=120).stdout
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    found = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    if not found:
        raise SystemExit("Chrome returned no inventory; is %s runnable?" % chrome)
    payload = json.loads(html.unescape(found.group(1)) or "{}")
    if not payload:
        raise SystemExit("the pinned runtimes loaded but exposed no global")
    scanned = files + [name for name in SCAN_ONLY if (vendor / name).is_file()]
    return {"schema_version": VERSION, "runtimes": files, "scanned_only": list(SCAN_ONLY),
            "surface": payload, "documented_names_in_bundle": scan(vendor, scanned)}


def scan(vendor: Path, files: list[str]) -> dict[str, dict[str, bool]]:
    """Does the pinned file even contain the identifier its site documents today?"""
    found = {}
    for name in files:
        text = (vendor / name).read_text(encoding="utf-8", errors="replace")
        found[name] = {word: word in text for word in DOCUMENTED.get(name, ())}
    return found


def differences(observed: dict, expected: dict, trail: str = "") -> list[str]:
    if isinstance(observed, dict) and isinstance(expected, dict):
        report = []
        for key in sorted(set(observed) | set(expected)):
            report.extend(differences(observed.get(key), expected.get(key),
                                      trail + "." + key if trail else key))
        return report
    if observed != expected:
        return ["%s: pinned runtime says %r, snapshot says %r" % (trail, observed, expected)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Read the API surface out of the pinned runtimes.")
    parser.add_argument("--vendor", default=str(Path(__file__).parent / "vendor"))
    parser.add_argument("--builder", default=str(Path(__file__).parents[2] / "assets" / "build-report.py"),
                        help="source of the plan-easing → engine-easing tables")
    parser.add_argument("--output")
    parser.add_argument("--expect", help="compare against a saved snapshot and fail on drift")
    args = parser.parse_args()
    observed = probe(Path(args.vendor).resolve(), Path(args.builder).resolve())
    text = json.dumps(observed, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    if args.expect:
        expected = json.loads(Path(args.expect).read_text(encoding="utf-8"))
        drift = differences(observed, expected)
        if drift:
            print("\n".join(drift), file=sys.stderr)
            return 1
        print("pinned runtimes match %s" % args.expect)
        return 0
    if not args.output:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
