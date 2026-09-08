# What the sites document, what the pins expose

Read this before you copy an API name out of a tool's documentation into a plan.

`references/external-tools.md` links six sites. Each documents whatever version is current on the
day you open it; this repo builds against fixed files under `vendor/`, and a report ships one
offline HTML with the chosen runtime inlined. Where those two disagree, the pinned file wins and
the site is wrong about this repo — silently, because none of these libraries validates the option
names you pass them the same way.

Everything below was read out of the pinned files themselves. `api-surface.json` is that reading;
`../probe-api.py` regenerates it offline and `--expect` fails on drift:

```
python3 lab/motion-engines/probe-api.py --expect lab/motion-engines/docs/api-surface.json
```

Site claims were captured **2026-09-07** from the links in `references/external-tools.md`.

| Tool | Pinned here | Site documents | Aligned |
|---|---|---|---|
| GSAP | 3.15.0 (core **and** `all.min.js`) | v3 (core, plus 24 plugin files) | yes — every plugin is pinned |
| Motion | 11.11.17 | 13.1.1 | mostly |
| anime.js | 3.2.2 | 4.0.0 | **no — different API** |
| D3 | 7.9.0 | 7.9.0 | yes |
| Plotly | not vendored | — | n/a |

---

## GSAP 3.15.0 — the eases are real, and now so are the plugins

The pinned core exposes 34 entries (`to` `from` `fromTo` `set` `timeline` `parseEase` `killTweensOf`
`quickTo` `matchMedia` `registerPlugin` `ticker` `utils` …) and 17 `gsap.utils` helpers.

**70 ease names resolve through `gsap.parseEase`.** The documented catalogue —
`none` `power0`–`power4` `back` `bounce` `circ` `elastic` `expo` `sine` `steps`, each with
`.in`/`.out`/`.inOut` — plus aliases the eases page does not list: `linear` `quad` `cubic` `quart`
`quint` `strong`. Parametric forms work: `back.out(1.7)`, `elastic.out(1,0.3)`, `steps(12)`.
The default ease is `power1.out`, confirmed by identity against `gsap.parseEase('power1.out')`.

**Every plugin is present, in the bundle.** Two GSAP files are pinned: `gsap-3.15.0.min.js`,
the core, which the probe reads as text only, and `gsap-all-3.15.0.min.js`, which the probe loads.
The core contains **6** of the 31 names asked of it and the bundle contains all **31**; on window
the split is 1 global against **27**. `gsap.plugins` holds six built-in property plugins in both
and reaches 18 only after `gsap.registerPlugin()` — loading a plugin file does not register it, and
`gsap.parseEase('rough')`, `'slow'` and `'expoScale(1,2)'` all fail until EasePack is registered.
[`gsap.md`](gsap.md) carries the full catalogue and the verdict for each plugin. Half the
reason to reach for GSAP lives in those plugins, and none of it is available to a report.

## Motion 11.11.17 — two versions behind, and it will not tell you

`animate` `animateMini` `scroll` `inView` `stagger` `spring` `inertia` `delay` `frame`
`motionValue` `transform` `interpolate` `cubicBezier` `steps` `mirrorEasing` and ten named easings
(`easeIn/Out/InOut`, `circIn/Out/InOut`, `backIn/Out/InOut`, `anticipate`) — 44 exports in all.
Both the numeric form (`animate(0, 1, {onUpdate})`) and the element form return the same controls:
`play` `pause` `stop` `cancel` `complete` `then` `time` `speed` `duration`. There is no `timeline`
export; sequences go through `animate([...])`.

**The trap: options are not validated.** `visualDuration` — a spring option motion.dev documents
today — does not occur anywhere in the pinned file, and passing it raises nothing. A bogus easing
string is accepted the same way. So a plan copied from the current docs runs, looks plausible, and
quietly ignores half of what you asked for. The only thing that catches this is
`assets/check-motion.py` observing that progress actually happened.

## anime.js 3.2.2 — the link no longer documents this library

animejs.com now documents **v4**, which is a different API: `animate()`, `createTimeline()`,
`createTimer()`, `createDraggable()`, `createScope()`, `createSpring()`, `onScroll()`, `morphTo()`,
`createDrawable()`, `createMotionPath()`, `splitText()`. **Eleven of those fourteen documented names
do not occur in the pinned 3.2.2 file at all**; only `stagger`, `timeline` and `remove` survive into
it, and they are reached differently.

What is actually here is the v3 surface: `anime()` itself as a callable, plus `stagger` `timeline`
`remove` `get` `set` `path` `setDashoffset` `random` `running` `speed` `penner` `easing`
`convertPx` `suspendWhenDocumentHidden` `version`. Calls look like
`anime({targets, duration, easing, update, complete})`. The v4 selling points in the selection
table — a Draggable API, the Scope API, ScrollObserver — are **not** in what this repo ships.

Unlike Motion, anime.js does reject an unknown easing name, loudly. That is the one place these
two engines' failure modes differ, and it is why the ease check below means something for anime and
nothing for Motion.

## D3 7.9.0 — the only entry where site and pin agree

37 ease names (`easeLinear`, `easeCubic*`, `easePoly*`, `easeQuad*`, `easeSin*`, `easeExp*`,
`easeCircle*`, `easeBack*`, `easeBounce*`, `easeElastic*`), the full transition API
(`duration` `delay` `ease` `easeVarying` `attr` `attrTween` `style` `styleTween` `text` `textTween`
`tween` `remove` `on` `end` `selection` `transition`), `selection.interrupt()`, and
`data`/`join`/`enter`/`exit`. Because the pin and the site are the same version, what d3js.org says
holds here: transitions default to **250 ms** and `easeCubicInOut`, and are scheduled per element —
which is what lets one selection carry different timing per datum.

## Plotly — a model, not a dependency

Nothing is vendored and nothing should be. What the animation page describes is worth taking as a
*model*: named frames (`Plotly.addFrames`) played by `Plotly.animate`, with `transition
{duration, easing}` kept separate from `frame {duration, redraw}`, and queueing named explicitly
(`immediate`, `next`, `afterall`). Its limits are equally instructive: only scatter traces
transition smoothly, and data or layout can animate — not both at once.

## The gallery's animation category

Worked examples, useful as a form catalogue when a dataset's shape is not obvious: animated
treemap, temporal force-directed graph, connected scatterplot, the wealth & health of nations,
scatterplot tour, bar chart race, stacked-to-grouped bars, streamgraph transitions, smooth zooming,
zoom to bounding box, orthographic to equirectangular, world tour, Walmart's growth, hierarchical
bar chart, zoomable treemap, zoomable circle packing, collapsible tree, zoomable icicle, zoomable
sunburst, sortable bar chart. Every one of them is a document that changes under the reader — see
`gsap.md` and `d3.md` for why a report is not.

---

## What a run may actually ask for

A plan's `motion.easing` is one of seven names, and `assets/build-report.py` maps each to the
selected engine. The probe re-reads that table out of the builder and resolves every value against
the pinned runtime:

| plan | GSAP 3.15.0 | Motion 11.11.17 | anime 3.2.2 |
|---|---|---|---|
| `linear` | `none` | `linear` | `linear` |
| `outCubic` | `power3.out` | `[.22,.61,.36,1]` | `easeOutCubic` |
| `inOutCubic` | `power3.inOut` | `[.65,0,.35,1]` | `easeInOutCubic` |
| `outQuint` | `power4.out` | `[.23,1,.32,1]` | `easeOutQuint` |
| `outExpo` | `expo.out` | `[.16,1,.3,1]` | `easeOutExpo` |
| `outCirc` | `circ.out` | `[0,.55,.45,1]` | `easeOutCirc` |
| `inOutQuint` | `power4.inOut` | `[.83,0,.17,1]` | `easeInOutQuint` |

All twenty-one resolve. The snapshot also records a `<control>` row holding a deliberately invalid
name: GSAP and anime.js reject it, Motion accepts it. Read the Motion column as "did not throw",
not as "was understood".

So, for a plan:

- **Do not name a plugin, a v4 factory, or a spring option in a reason or a contract.** If it is
  not in this file, it is not in the report.
- The engine choice changes the easing *implementation*, not the vocabulary. Seven names, three
  engines, one meaning each.
- Anything richer than `entry` on `on-view` — a timeline, scroll choreography, morphing, drawing,
  stagger — needs a runtime this repo does not vendor, and `references/motion.md` bans most of it
  in a report anyway.
