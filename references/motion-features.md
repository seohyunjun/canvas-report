# Motion and anime.js — every advertised feature, and the one place each belongs

[`motion.md`](motion.md) sets the contract and [`motion-engines.md`](motion-engines.md) compares the
three pinned engines. This file is the catalogue: it walks the two documentation pages a plan is
most likely to be written from — [Motion's quick-start](https://motion.dev/docs/quick-start) and
[anime.js's *Using with vanilla JS*](https://animejs.com/documentation/getting-started/using-with-vanilla-js)
— summarises what each advertised feature does, shows the call as the **pinned** file would take
it, and says where that feature lands in a canvas report.

Read it before writing a `motion` block. The point is not that most of this is unused; it is that
every one of these capabilities is already accounted for, so a plan never has to guess whether a
feature is missing, forbidden, or simply supplied by something else.

## The two pages document versions this repo does not ship

| | Site documents | Pinned here | Consequence |
|---|---|---|---|
| Motion | the 13.x line | **11.11.17** | most names match; springs gained options the pin lacks and silently ignores |
| anime.js | **4.0.0** | **3.2.2** | a different API. Every `create*` name on that page is absent from the pin |

The read-out of what the pinned files actually export is
[`../lab/motion-engines/docs/api-surface.md`](../lab/motion-engines/docs/api-surface.md), with the
machine-readable inventory beside it. **Where a site and a pin disagree, the pin wins.**

Neither page's loading instructions apply. Both offer npm, an ESM CDN `import`, and a `<script src>`;
a report makes zero network requests and has no build step, so `assets/build-report.py` inlines the
pinned file it has already SHA-256 verified. Never write an `import`, a CDN URL, or a `<script src>`
into a plan.

## How to read the verdict

| Verdict | Meaning |
|---|---|
| **used** | the builder calls it, on every chart that enables motion |
| **shell** | the report has this capability; `assets/report-shell.html` supplies it, and its version is what the gates measure |
| **held** | present in the pin and legal in principle, but the deterministic builder compiles no plan field that reaches it |
| **absent** | the page shows it; the pinned file does not contain it |
| **refused** | the pin has it and the report contract forbids the effect, for a stated reason |

---

## Motion 11.11.17, against its quick-start

### Getting something on screen

| Feature | What it does | In the pin | Verdict |
|---|---|---|---|
| `animate(el, {rotate: 360})` | animates a DOM element or CSS selector | yes | **held.** A canvas has one element and no per-mark nodes; there is nothing to select |
| `animate(0, 1, {onUpdate})` | animates a bare number and hands you each value | yes | **used.** This is the whole integration — see below |
| `animate(obj, {x: 100})` | animates an object's properties in place | yes | **held.** The number form is more explicit for one progress value |
| CSS selector targets, multiple elements at once | one call drives many nodes | yes | **held**, for the same reason |
| Independent transforms (`x`, `y`, `rotateY`, `scale`) | transform components animate separately, off the main thread | yes | **held.** Nothing in a report is transformed; the canvas is repainted |
| Colours, filters, SVG attributes and paths | typed value interpolation | yes | **held.** Chart colour comes from the theme tokens and never animates |
| `animateMini` (the 2.3 kb HTML/SVG build) | a smaller WAAPI-only `animate` | present in the pin | **held.** The pin is the 63 KB hybrid UMD, and it is inlined, not fetched — bundle size is not the axis that matters here |

The one call the builder makes:

```js
Motion.animate(0, 1, {duration: duration/1000, ease: motionEase(easing),
                      onUpdate: function(v){ engine.t = v; paint(); },
                      onComplete: finish});
```

`engine.t` is the only channel. The chart factories read it and repaint; nothing else about a chart
is animatable, because there is no DOM element per mark.

### Options

| Option | What it does | In the pin | Verdict |
|---|---|---|---|
| `duration` | length of the animation, **in seconds** | yes | **used.** The plan declares milliseconds; the builder divides by 1000 |
| `delay` | wait before starting | yes | **refused.** A delayed evidence chart is a chart the reader waits for. Entry motion starts when the chart is in view, not later |
| `repeat`, `repeatType` (`loop`/`reverse`/`mirror`) | replay the animation | both present | **refused.** `motion.md`: a report animates once. A looping chart re-asserts a value that has already been read |
| `ease` — named strings | `easeIn/Out/InOut`, `circIn/Out/InOut`, `backIn/Out/InOut`, `anticipate` | the pin exports exactly those ten, plus `"linear"` | **used, but translated.** The plan's easing enum is mapped to a cubic-bezier array; the name is never passed through |
| `ease` — cubic-bezier array | `[.22,.61,.36,1]` | yes (`cubicBezier`) | **used.** This is what `motionEase()` produces |
| `ease` — `steps()` | quantised playback | yes | **held.** A quantised reveal is what the `line` factory already does by rounding `n = round(rows.length · t)` |
| `ease` — custom function | your own `(t) => t` | yes | **refused.** An arbitrary curve cannot be shown to stay inside `[0,1]`, and a value-scaled mark drawn past its axis is a false reading |
| `times` | keyframe offsets | yes (`keyframes`) | **held.** One value from 0 to 1 has no intermediate stops |
| `type: "spring"` with `stiffness`, `damping`, `mass`, `bounce`, `restSpeed`, `restDelta` | real spring physics that responds to velocity | present, **except `visualDuration`**, which the pin accepts and ignores | **refused.** A spring has no bounded end and overshoots. The plan's easing enum contains no spring for exactly this reason |
| `inertia` | momentum-based settling | present | **refused**, same reason |

### Orchestration, controls and gestures

| Feature | What it does | In the pin | Verdict |
|---|---|---|---|
| `stagger(0.1, {startDelay, from, ease})` | spreads delay across a set of targets | yes | **refused.** One chart is one mark set with one progress value; there is nothing to cascade, and a cascade costs the reader one delay per mark |
| Controls: `play pause stop cancel complete then time speed duration` | drive a running animation | all present on both the element and number forms | **`stop()` is used**, when a superseded run has to be cancelled. The rest are held |
| `scroll(animation, {container, target, axis, offset})`, `scrollInfo` | ties progress to scroll position | yes | **held.** Scroll-linked motion is a scrollytelling state model the deterministic builder does not compile. Do not declare it and hope the shell infers it |
| `inView(el, cb, {root, margin, amount})` | fires when an element enters the viewport | yes | **shell.** `R.onView` already does this, plays once, and is what `assets/check-motion.py` measures |
| `hover()`, `press()`, drag, layout animation | gesture and layout APIs the quick-start advertises | **absent from 11.11.17** — they are v12+/React-side | **absent.** Chart hover is the shell's own hit-testing and tooltip, which works under reduced motion |
| Utilities: `mix`, `interpolate`, `transform`, `wrap`, `clamp`, `progress`, `distance` | value plumbing | all present | **held.** The factories already own their scales; a second mapping layer would put two sources of truth on one axis |

Two properties of this build the current docs will not tell you: **options are not validated** — a
misspelled option name or an unknown easing string is accepted in silence — and `animate()` returns
controls whether you asked for them or not.

---

## anime.js 3.2.2, against its *Using with vanilla JS* page

That page documents **4.0.0** and opens with an ESM import:

```js
import { animate, utils, createDraggable, spring } from 'animejs';
```

**None of those four names exists in the pinned file.** Translate before you plan:

| v4, as the page writes it | 3.2.2, as pinned |
|---|---|
| `animate(targets, {…})` | `anime({targets: …, …})` |
| `createTimeline()` | `anime.timeline()` |
| `createTimer()`, `createAnimatable()`, `createScope()`, `createDraggable()` | absent |
| `onScroll()` | absent |
| `stagger(…)` | `anime.stagger(…)` — **and the options differ**: v3 takes `direction:'reverse'` and `easing`, v4 takes `reversed` and `ease` |
| `spring({bounce: .7})` | absent as a factory; v3 has the string form `'spring(mass, stiffness, damping, velocity)'` |
| `ease: 'inOut(3)'`, `'out(4)'` | `easing: 'easeInOutCubic'`, `'easeOutQuart'` — the parameterised shorthand is v4 only |
| `onUpdate` / `onComplete` / `onBegin` | `update` / `complete` / `begin` |
| `utils.$`, `utils.set`, `utils.get`, `utils.remove`, `utils.random` | `anime.set`, `anime.get`, `anime.remove`, `anime.random`; there is no `$` |
| `svg.morphTo`, `svg.createDrawable`, `svg.createMotionPath` | `anime.path`, `anime.setDashoffset` only |
| `text.split()`, `waapi.animate()`, `engine` | absent |

What the pin does contain, in full: `anime()` itself plus `stagger` `timeline` `remove` `get` `set`
`path` `setDashoffset` `random` `running` `speed` `penner` `easing` `convertPx`
`suspendWhenDocumentHidden` `version`.

### Feature by feature

| Feature | What it does | In the pin | Verdict |
|---|---|---|---|
| `anime({targets, duration, easing, update, complete})` | the core call | yes | **used.** `duration` is in **milliseconds** here, unlike Motion |
| Keyframe arrays — `scale: [{to: 1.25, …}, {to: 1, …}]` | per-step values, easings and durations | v3 uses `[{value, duration, easing}]` | **held.** One progress value has no steps |
| `loop`, `loopDelay` | the page's example loops forever | both present in v3 | **refused.** Same rule as Motion's `repeat` |
| `easing` — the 41 penner names | `easeOutCubic`, `easeInOutQuint`, … | all present | **used, translated.** `animeEase()` maps the plan's enum onto them |
| `easing` — `'spring(...)'`, `easeOutElastic`, `easeOutBounce`, `easeOutBack` | overshooting curves | present | **refused.** They pass 1 on the way and would draw a mark beyond its own axis |
| `anime.stagger(value, {grid, from, axis})` | distributes delay by time, value, or grid position | yes — the most developed stagger of the three | **refused**, and it is the engine's signature feature. Five bars 90 ms apart costs the fifth value 360 ms; on a Poster's thirty-one cells it is 2.7 seconds |
| `anime.timeline()` | sequences animations | yes | **held.** One chart, one progress value, no sequence to build |
| `createDraggable` (the page's second example) | pointer dragging with spring release | absent | **absent.** Chart interaction is the shell's hit-testing, which is keyboard-reachable |
| `anime.path`, `anime.setDashoffset` | SVG path following and line drawing | yes | **held.** Reports draw to canvas; there is no SVG geometry to trace |
| `anime.set` / `anime.get` | read and write target properties directly | yes | **held.** The factories own their own state |
| `anime.remove(targets)` | cancels animations on a target | yes | **used.** The builder calls it before painting the final state — a late frame otherwise overwrites the value |
| `anime.running`, `anime.speed`, `anime.suspendWhenDocumentHidden` | global playback state | yes | **held** |

Unlike Motion, **anime.js throws on an unknown easing name.** That is the one place the two engines'
failure modes differ, and it is why a typo surfaces here and disappears there.

---

## Every capability the report needs, and who supplies it

Nothing on the "refused" and "held" lists leaves a gap. The shell owns these jobs, and owns them
better for this one, because it can guarantee the final frame.

| Job | The shell's API | The engine feature it replaces |
|---|---|---|
| play when the chart is scrolled to | `R.onView(node, fn)` — fires once | `Motion.inView`, `ScrollTrigger` |
| honour reduced motion | `R.reduced()`; `anim()` paints the final state instead of animating | no engine has an equivalent |
| guarantee the last frame | `setTimeout(finish, dur + 260)` plus a token in `anim()` | all three freeze mid-frame when rAF stops |
| cancel a superseded run | `engine.__token` | `kill()` / `stop()` / `anime.remove()` — the builder calls these too, but the token is what makes it safe |
| step through a story | `R.scrolly()` | `scroll()`, `onScroll()`, timelines |
| one-shot emphasis on a DOM node | `R.motion(node, keyframes, options)` — drives the Web Animations API, and refuses transforms beyond ±24 px | `animate(el, …)` |
| count a headline figure up | `R.countUp()` | `animate(0, n, {onUpdate})` on a DOM node |
| reveal a block as it arrives | `R.reveal()` and the `.reveal` class | `animate(el, {opacity, y})` |

`R.motion()`, `R.countUp()` and `R.reveal()` are the **only** places an overshoot curve is legal, because
they move opacity and position, not a number a reader is about to compare.

---

## Putting the right one in the right place

### Step 1 — does this chart need motion at all?

`motion.md` decides, per chart. Static needs a chart-specific clarity reason, not a shrug; motion
needs a reader benefit, not a preference for movement.

### Step 2 — does the report need a third-party runtime?

Almost never. The shell's `anim()` drives the same idea Motion's core is built on, and
`portable-pattern` skips the SHA/licence machinery and keeps the file smaller. Choose
`vendored-runtime` only when the run exists to demonstrate the pinned engine, or a downstream
requirement names it. For that one call the three are interchangeable, so pick on cost:

| | Motion 11.11.17 | anime.js 3.2.2 | GSAP 3.12.5 |
|---|---|---|---|
| Inlined weight | 63 KB | **17 KB** | 72 KB |
| Duration unit | seconds | milliseconds | seconds |
| Unknown easing | silently accepted | throws | `parseEase` returns falsy |

### Step 3 — the easing and duration follow the factory, not the theme

`c.t` does not mean the same thing in every factory, and this is where "the right feature in the
right place" actually bites:

| Factory | What `c.t` scales | What the reader sees while it runs |
|---|---|---|
| `line`, `concentration` | `n = round(rows.length · t)` — how many points are drawn | a **reveal**. Nothing on screen is wrong, there is just less of it |
| `slope` | how far along each line the endpoint has travelled | a reveal too: the point moves *along* the true line, so no frame is off it |
| `waterfall` | `clamp(t · steps − i)` per step — a **sequenced** reveal | steps land one after another, so `t` is divided among them |
| `columns`, `divColumns` | bar height from the zero baseline | the bar **reads a value smaller than the datum** until it lands |
| `hbars`, `lollipop`, `divHbars`, `panels` | bar length | the same |
| `stackedArea` | each band's height above the one below | the same, and the total is short too |
| `donut` | the sweep angle of each arc | every share reads smaller than it is until the ring closes |
| `heatmap` | cell intensity | every cell is paler than its value, so the field looks flatter than it is |
| `boxplot`, `interval` | the spread, growing **outward from a point drawn at its true position** | the opposite failure: a running frame shows a **narrower** interval than the data supports |
| `bubbles` | the **radius** | area grows with `t²`, so the mark looks far smaller than its value for most of the run |

Three rules follow:

- **A reveal can afford a steady curve; a value-scaled mark cannot.** A bar that spends 400 ms
  reading 60 % of its number is briefly lying. Use a curve that arrives early.
- **A reveal's easing is its reading pace.** On `line`, `outExpo` lands almost immediately and wastes
  the sweep; `outCubic` or `linear` keep the left-to-right order legible.
- **A chart that draws spread gets the shortest run of all.** `boxplot` and `interval` grow the
  range outward from a value already in place, so every intermediate frame is an *overclaim* of
  precision. Understating a bar for 400 ms is a delay; understating an interval is a different
  statement about the evidence.

| Chart | Easing | Duration | Why |
|---|---|---|---|
| `line` | `outCubic`, or `linear` when the time order *is* the point | 600–800 ms | the sweep is the reading order; 24 points at 700 ms is one point every 30 ms |
| `concentration` | `outCubic` or `linear` | 600–800 ms | the same reveal mechanic |
| `slope` | `outCubic` or `linear` | 600–800 ms | the line is read left to right, so it should be drawn that way |
| `waterfall` | `outCubic` or `linear` | 600–900 ms | the run is shared among the steps; five steps at 700 ms is 140 ms each |
| `columns`, `divColumns`, `divHbars` | `outQuint` or `outExpo` | 400–600 ms | the baseline registers, then the heights arrive before the eye starts comparing |
| `hbars`, `lollipop`, `panels` | `outQuint` or `outExpo` | 400–600 ms | labels are already in place, so only the length is in motion |
| `stackedArea` | `outQuint` or `outExpo` | 400–600 ms | the total is the subject and it has to be right early |
| `donut` | `outQuint` or `outExpo` | 400–600 ms | a part-way arc is a wrong share, and shares are what the chart is for |
| `heatmap` | `outQuint` or `outExpo` | 400–600 ms | intensity is the value; a pale grid is a quiet understatement of it |
| `boxplot`, `interval` | `outQuint` or `outExpo` | 300–500 ms | see the third rule: a narrow band claims more than the data does |
| `bubbles` | `outExpo` | 700–900 ms | radius is the square root of area, and the curve compensates for the slow visual start |
| any chart carrying the report's caveat | — | static | that is the reason |

`assets/validate-plan.py` reports a **warning** — `MOTION-FIT-001` for the curve, `MOTION-FIT-002`
for the duration — when a chart leaves its band. A warning does not block: record why this chart's
reading pace differs and ship it, or take the recommendation.

`inOutCubic` and `inOutQuint` spend time at both ends and suit a chart whose entry should feel
deliberate rather than quick; they suit no evidence chart in a Briefing. `outCirc` starts fast and
eases late, which reads well on a single hero figure and poorly on a set of bars.

### Step 4 — mind the ceiling the two paths do not share

The plan schema and the motion gate take **180–1200 ms**, and the vendored path clamps to exactly
that. The portable path does not, because the shell's `anim()` caps at **900 ms**
(`Math.min(900, Math.max(0, dur))`). The gate reads the declared attribute rather than the elapsed
time, so a `portable-pattern` chart declaring 1,000 ms would pass every check and run for 900.
`MOTION-PORTABLE-CEILING-001` is an **error** for exactly that case. Every duration recommended
above is inside the ceiling, and `bubbles` sits on it.

---

## Worked contracts

A reveal chart on the portable path:

```json
{
  "motion": {
    "enabled": true,
    "reason": "The series is drawn in time order so the reader acquires the trend's direction before its level.",
    "kind": "entry", "trigger": "on-view",
    "duration_ms": 700, "easing": "outCubic", "source_tool": "motion"
  }
}
```

A value-scaled chart, with the engine vendored because the run demonstrates it:

```json
{
  "motion": {
    "enabled": true,
    "reason": "The zero baseline registers first, so the size comparison resolves in reading order.",
    "kind": "entry", "trigger": "on-view",
    "duration_ms": 480, "easing": "outQuint", "source_tool": "anime"
  }
}
```

Static, for a chart-specific reason:

```json
{
  "motion": {
    "enabled": false,
    "reason": "Thirty-one dense labels are faster to scan without mark growth."
  }
}
```

Whatever engine is chosen goes in `creative_direction.external_tools` with a role and an integration
mode, and every enabled chart repeats it in `motion.source_tool`. **One motion source per report.**
