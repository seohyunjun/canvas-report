# Motion engines — every advertised feature, and where it lands in a report

Read this with [`motion.md`](motion.md) whenever a chart enables motion or a plan names a
`vendored-runtime`. [`motion-features.md`](motion-features.md) is the fuller catalogue — it walks
both documentation sites feature by feature and routes easing and duration per chart factory; this
file is the engine-by-engine comparison. `motion.md` sets the contract; this file says what the engines actually offer,
what the pinned copies actually contain, and which of it a canvas report can use.

The engines' own sites document whatever version is current. This repo builds against fixed files,
and the surface read out of them is in
[`../lab/motion-engines/docs/api-surface.md`](../lab/motion-engines/docs/api-surface.md) with the
machine-readable inventory beside it. Where a site and a pin disagree, the pin wins.

| Engine | Pinned | Site documents | Loading here |
|---|---|---|---|
| Motion | 11.11.17 | 13.x | inlined from `lab/motion-engines/vendor/`, SHA-256 verified at build |
| anime.js | 3.2.2 | 4.x — **a different API** | same |
| GSAP | 3.15.0 | 3.x | same; the core is inlined, and all 24 plugins are pinned for the lab |

**Loading never follows the quick-starts.** They offer npm, an ESM CDN import, and a `<script src>`
from jsdelivr. A report makes zero network requests and has no build step, so the builder inlines
the pinned file it has already hashed. Never write an `import`, a CDN URL, or a `<script src>` into
a plan.

---

## What a report actually calls

One call per engine, once per chart, driving one number from 0 to 1. This is the whole integration
(`assets/build-report.py`):

```js
gsap.to(engine, {t:1, duration:duration/1000, ease:gsapEase(easing),
                 onUpdate:paintIfCurrent, onComplete:finish});

Motion.animate(0, 1, {duration:duration/1000, ease:motionEase(easing),
                      onUpdate:function(v){ engine.t = v; paint(); }, onComplete:finish});

anime({targets:engine, t:1, duration:duration, easing:animeEase(easing),
       update:paintIfCurrent, complete:finish});
```

`engine.t` is the only channel. The factories read it and repaint the canvas; nothing else about a
chart is animatable, because there is no DOM element per mark to animate.

The shell already owns the parts the engines also offer, and owns them better for this job:

| Job | The shell | Do not use the engine's version |
|---|---|---|
| Play when the chart is scrolled to | `R.onView`, once | `Motion.inView`, `ScrollTrigger` |
| Honour reduced motion | `R.reduced()` omits motion and paints the final state | engines have no equivalent |
| Guarantee the final frame | `setTimeout(finish, dur+260)` plus a token in `anim()` | all three freeze mid-frame when rAF stops |
| Cancel a superseded run | `engine.__token` | `kill()`, `stop()`, `anime.remove()` — the builder calls these too, but the token is what makes it safe |

---

## Motion 11.11.17

The quick-start's four examples map onto this build as follows.

| Feature the site shows | In the pin | In a report |
|---|---|---|
| `animate(el, {rotate: 360})` | yes | **the numeric form is what the builder uses**: `animate(0, 1, {onUpdate})`. The element form has nothing to target. |
| `{ease: "circInOut", duration: 1.2}` | yes — `duration` in **seconds** | used; the plan's easing name is translated to a cubic-bezier array, not passed through |
| `{type: "spring", stiffness: 300}` | spring exists; `visualDuration` does **not**, and is accepted without error | **no.** A spring has no bounded end and overshoot writes values past the axis. The plan's easing enum has no spring for this reason |
| `stagger(0.1)` as `delay` | yes — `stagger(duration, {startDelay, from, ease})` | **banned** by `motion.md`. One chart is one mark set with one progress value; there is nothing to cascade |
| `scroll(animation)` / ScrollTimeline | yes, with `{container, target, axis, offset}` | **no.** Scroll-linked motion is a scrollytelling state model the deterministic builder does not compile |
| `inView(el, cb, {root, margin, amount})` | yes | the shell's `R.onView` already does this and is what the gate measures |
| press · hover · drag · layout animation | gestures and layout are v12+/React-side | out of scope: a canvas has no per-mark elements to gesture on |
| mini (2.3 kb) vs hybrid build | the pin is the 63 KB UMD hybrid | irrelevant — the file is inlined, not fetched |

Two things about this build that the current docs will not tell you: **options are not validated**
(a misspelled option or an unknown easing string is accepted silently), and `Motion.animate`
returns controls — `play pause stop cancel complete then time speed duration` — of which the
builder uses `stop()`.

## anime.js 3.2.2

The vanilla-JS getting-started page shows **v4**: `import { animate, utils, createDraggable, spring }
from 'animejs'`. None of those names exists in the pinned file. Translate before you plan:

| v4, as documented | 3.2.2, as pinned |
|---|---|
| `animate(targets, {…})` | `anime({targets: …, …})` |
| `createTimeline()` | `anime.timeline()` |
| `stagger(…)` | `anime.stagger(…)` — **and its options differ**: v3 takes `direction:'reverse'` and `easing`, where v4 takes `reversed` and `ease` |
| `onUpdate` / `onComplete` / `onBegin` | `update` / `complete` / `begin` |
| `ease: 'outExpo'` | `easing: 'easeOutExpo'` |
| `createDraggable` · `createScope` · `createTimer` · `onScroll` · `morphTo` · `createDrawable` · `createMotionPath` · `splitText` | **absent** |

What the pin does contain: `anime()` itself plus `stagger` `timeline` `remove` `get` `set` `path`
`setDashoffset` `random` `running` `speed` `penner` `easing` `convertPx`
`suspendWhenDocumentHidden` `version`.

| Feature | In a report |
|---|---|
| `anime({targets, duration, easing, update, complete})` | **used** — `duration` in **milliseconds** here, unlike Motion |
| `anime.stagger` (time, value, grid) | **banned**. It is the engine's signature feature and the reason not to pick it for a report |
| `anime.timeline()` | not compiled: the builder has one chart, one progress value, no sequence |
| SVG toolset — `setDashoffset`, `path`, morphing | no SVG in a report; the charts are canvas |
| `anime.remove(targets)` | the builder calls it before painting the final state, because a late frame otherwise overwrites the value |

Unlike Motion, anime.js **throws on an unknown easing name**. That is the one place their failure
modes differ, and it is why a typo is caught here and swallowed there.

## GSAP 3.15.0

Two files are pinned. A report inlines **`gsap-3.15.0.min.js`**, the 72 KB core: seventy ease names
resolve, the default is `power1.out`, and the timeline — the reason to choose GSAP at all — has
nothing to sequence in a report that animates once per chart.

The 325 KB **`gsap-all-3.15.0.min.js`** carries the core plus all 24 plugin files, and it is the
lab's. No report inlines it: a document that runs one entry tween has no business shipping
ScrollSmoother. The plugins are all *reachable* now — Webflow's licence change of April 2025 freed
the bonus set, and cdnjs has carried every one since 3.13.0 — so each is refused or held on what a
report should do rather than on what the pin lacks.
[`lab/motion-engines/docs/gsap.md`](../lab/motion-engines/docs/gsap.md) is the catalogue: what each
plugin does, whether it is a property, behaviour or ease plugin, and the verdict here. The one
measured trap it opens with: loading a plugin file does not register it, and `gsap.plugins` is the
wrong place to look for the answer.

---

## Choosing: which engine, and whether any

Answer in this order.

1. **Does the chart need motion at all?** `motion.md` decides. Static needs a chart-specific reason,
   not a shrug.
2. **Does the report need a third-party runtime?** Almost never. The shell's `motion()` helper drives
   the Web Animations API directly, which is Motion's own core idea. `portable-pattern` keeps the
   file smaller and skips the SHA/licence machinery. Choose `vendored-runtime` only when the run is
   there to demonstrate the pinned engine, or when a downstream requirement names it.
3. **If a runtime is genuinely wanted**, they are interchangeable for this one call, so pick on
   cost, not capability:

| | Motion 11.11.17 | anime.js 3.2.2 | GSAP 3.15.0 |
|---|---|---|---|
| Inlined weight | 63 KB | **17 KB** | 72 KB |
| Licence | MIT | MIT | GreenSock standard, no-charge |
| Duration unit | seconds | milliseconds | seconds |
| Unknown easing | silently accepted | throws | `parseEase` returns falsy |
| Pick it when | the report is about browser-native animation | weight is the deciding factor | a later run may need timelines |

Whatever is chosen goes in `creative_direction.external_tools` with a role and an integration mode,
and every enabled chart repeats it in `motion.source_tool`. One motion source per report.

---

## Choosing the easing and the duration, per chart

`c.t` does not mean the same thing in every factory. The shipped code:

| Factory | What `c.t` scales | Consequence while the animation runs |
|---|---|---|
| `line`, `concentration` | `n = round(rows.length · t)` — how many points are drawn | a **reveal**: nothing on screen is wrong, there is just less of it. Quantised to 1/N, so 24 rows means 24 steps |
| `columns`, `divColumns` | bar height from the zero baseline | the bar **shows a value smaller than the datum** until it lands |
| `hbars`, `lollipop` | bar length or lollipop value | same |
| `bubbles` | the **radius** | area grows with `t²`, so the mark looks far smaller than its value for most of the run |

Two rules follow, and they are the whole of "use the right one in the right place":

- **Reveal charts can afford a steady curve; value-scaled charts cannot.** A bar that spends 400 ms
  reading 60 % of its number is a bar that is briefly lying. Prefer a curve that arrives early —
  `outQuint`, `outExpo` — and a shorter duration.
- **A reveal's easing is its reading pace.** On `line` and `concentration`, `outExpo` lands almost
  immediately and wastes the sweep; `outCubic` or `linear` keep the left-to-right order legible.

| Chart | Easing | Duration | Why |
|---|---|---|---|
| `line` | `outCubic`, or `linear` when the time order *is* the point | 600–800 ms | the sweep is the reading order; 24 points at 700 ms is about one point every 30 ms |
| `concentration` | `outCubic` | 600–800 ms | same reveal mechanic |
| `columns`, `divColumns` | `outQuint` or `outExpo` | 400–600 ms | the baseline registers, then the heights arrive before the eye starts comparing |
| `hbars`, `lollipop` | `outQuint` | 400–600 ms | as above; labels are already in place, so only the length is in motion |
| `bubbles` | `outExpo` | 700–900 ms | radius is the square root of area — the curve compensates for the slow visual start |
| any chart carrying the report's caveat | — | — | static, with that as the reason |

`inOutCubic` and `inOutQuint` exist for the rare chart whose entry should feel deliberate rather
than quick; they spend time at both ends and suit no evidence chart in a Briefing. `outCirc` starts
fast and eases late, which reads well on a single hero figure and poorly on a set of bars.

Bounds are enforced, not advisory, but the two integration paths do not enforce the same one. The
plan schema and the motion gate take **180–1200 ms**; the vendored path clamps to exactly that; the
portable path does not, because the shell's own `anim()` caps at **900 ms**
(`Math.min(900, Math.max(0, dur))`). Nothing reports the difference — the gate reads the declared
attribute, not the elapsed time — so a `portable-pattern` chart declaring 1,000 ms passes every
check and runs for 900. **On the portable path, do not declare more than 900 ms.** Every duration
recommended above is inside that ceiling, and `bubbles` sits exactly on it.

Overshoot curves — `outBack`, `spring` — are in the shell for opacity and position only, and
`anim()` refuses them on a value-scaled mark, falling back to `outCubic` with a console warning.
