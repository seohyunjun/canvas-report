# External tools — select a small, purposeful toolchain

This skill ships one HTML file with **zero network requests**. External tools are actively used in
one of two honest ways:

- **Portable pattern** — use the tool's chart vocabulary, scale math, state model, easing, or
  choreography pattern through the shipped runtime. This is the default report path.
- **Vendored runtime** — use a pinned local runtime, inline it during the build, record its version,
  SHA-256, and licence, then run the same zero-network and final-state gates. Use this only with a
  builder that explicitly supports the selected runtime.

Do not add a CDN, improvise a third integration mode, or list a tool that had no observable effect
on the plan or output. `creative_direction.external_tools` records every selection.

## Selection table — read this on every run

Choose one chart/state source and at most one primary motion source. Keep those roles explicit:
D3 and Plotly are visualization/state tools, not primary motion engines. For chart entry motion,
the supported engines are GSAP, Motion, and anime.js. Read only the chosen sections and their
linked lab docs.

| Need | Prefer | Use from it | Do not use when |
|---|---|---|---|
| chart-form discovery, scales, shapes | D3 gallery + D3 | form vocabulary, scale/array math | a shipped `VIZ` factory already answers the question directly |
| stable identity across a re-sort | D3 | keyed join/object constancy | rows appear or disappear under a filter |
| named analytical states | Plotly frame model | state names separated from transitions | the report has only one state |
| simple entry, transform, opacity | Motion | browser-native animation and compact API | native `R.motion` already expresses the same transition |
| multi-part scroll choreography | GSAP | one bounded timeline | transitions are independent or purely decorative |
| compact SVG sequence | anime.js | small timeline/keyframe surface | stagger merely delays reading |

Record `tool`, `role`, `integration`, and `reason`. Prefer `portable-pattern`. A
`vendored-runtime` selection requires a supported builder and the pinned files under
`lab/motion-engines/vendor/`. The deterministic builder supports three deliberately narrow vendored
paths for `entry` motion: GSAP 3.12.5, Motion 11.11.17, and anime.js 3.2.2. It verifies the pinned
SHA-256, inlines the chosen runtime, uses that engine to drive canvas progress, and records version,
hash, and licence in the build manifest. Select only one of them per report. D3 and Plotly are not
accepted as `motion.source_tool` for chart entry.

---

## A. Chart-form vocabularies

### Observable D3 gallery · [d3-gallery-javascript](https://takanori-fujiwara.github.io/d3-gallery-javascript/)

A catalogue of roughly two hundred worked chart forms. The second link is Takanori Fujiwara's
vanilla-JavaScript port of the same gallery — more useful here, because it is plain JS you can
read without an Observable notebook runtime around it.

**What it is good at:** being a *vocabulary*. Twelve categories — animation, interaction,
analysis, hierarchies, networks, bars, lines, areas, dots, radial, maps, annotation. When you do
not know what form a dataset wants, this is the place to look.

**What this skill takes:** the forms, reimplemented on canvas. D3's real contribution to a
project like this is not the DOM-binding machinery — it is the *shape catalogue* plus the
scale/shape/array maths, which is a few dozen lines when you only need the parts you use.

**What this skill refuses:** the dependency, and about half the gallery. See the coverage map below.

### [D3.js](https://d3js.org/) — the library, not the gallery
*(lab: [`06-d3.html`](../lab/motion-engines/06-d3.html) · [`docs/d3.md`](../lab/motion-engines/docs/d3.md))*

The entry above is about D3's *catalogue*. This one is about the runtime, which is a different
question with a different answer.

**What it is good at:** the **keyed data join**. D3 does not animate elements you hand it; it
animates the relationship between data and elements. Give `selection.data()` a key function and a
reorder becomes *movement* — each mark travels to its new position and the eye follows one series
through the change. Drop the key and the identical transition describes nothing. That property is
called object constancy, and `enter` / `exit` are the same idea extended to marks that must appear
and disappear. Nothing else in this file has an equivalent.

**What this skill takes:** the scale, shape and array maths, reimplemented — `ticks()`, the
linear mapping every factory does, the quartile arithmetic in `boxplot`. A few dozen lines once you
only need the parts you use.

**What this skill refuses:** the 280 KB, and DOM ownership. The shell repaints a canvas from
scratch every frame, so there is no element whose identity could be kept — which is fine, because
**a report has nothing to be constant through.** It is read once and archived; the data does not
change under the reader. The moment it does, that is an application, and § When to close this skill
applies.

### [Plotly.js animations](https://plotly.com/javascript/animations/)

**What it is good at:** a genuinely well-designed animation *model*. Named `frames` added with
`Plotly.addFrames`, played by `Plotly.animate`, with `transition {duration, easing}` separate from
`frame {duration, redraw, mode}`. The `mode` values — `immediate`, `next`, `afterall` — are a
queueing vocabulary most animation code never bothers to define, and `redraw:false` is the
standard escape hatch for animating many frames quickly.

**What this skill takes:** the separation of *transition* from *frame*, and the discipline of
naming states rather than imperatively tweening. `R.scrolly` + a pinned canvas is the same idea:
each step is a named state, and the transition between them is a separate concern.

**What this skill refuses:** Plotly itself. It is a large bundle and it owns the DOM. Also worth
knowing before you reach for it elsewhere: **only scatter traces transition smoothly**, other
trace types snap, and you can animate data *or* layout but not both at once.

---

## B. Motion engines

> **Worked examples live in [`../lab/motion-engines/`](../lab/motion-engines/).** Each engine has
> one runnable page and one doc, all animating the same dataset, with the runtimes vendored and
> pinned. Read this section for the verdict; go there when the verdict is "yes, close the skill".
>
> **[`motion-engines.md`](motion-engines.md) maps every feature these engines advertise onto what a
> report can use, and picks the easing and duration per chart factory.** Read it when a chart
> enables motion.
>
> **Before copying an API name off any of these sites, read
> [`docs/api-surface.md`](../lab/motion-engines/docs/api-surface.md).** Each site documents whatever
> version is current; this repo builds against pinned files, and the two have drifted. That file
> records what the pinned runtimes actually expose, read out of the bundles themselves.

All three are excellent, all three are a network request or a build step, and **all three solve a
problem this skill does not have.** They animate a document. This skill animates a canvas, where
`c.t` is one number that every factory already reads.

### [GSAP](https://gsap.com/) — now free for everyone
*(lab: [`01-gsap.html`](../lab/motion-engines/01-gsap.html) · [`docs/gsap.md`](../lab/motion-engines/docs/gsap.md))*

**Good at:** choreography. Timelines that nest, and a plugin ecosystem nothing else matches —
ScrollTrigger, MorphSVG, MotionPath, DrawSVG, SplitText, Draggable. If you need to sequence
thirty things against a scrollbar, GSAP is the answer and it is not close.

**Portable idea taken:** the easing catalogue. A named curve set is the part of GSAP you can
retype in twenty lines, and this skill now ships one (see below).

### [Motion](https://motion.dev/) — MIT, formerly Framer Motion
*(lab: [`02-motion.html`](../lab/motion-engines/02-motion.html) · [`docs/motion.md`](../lab/motion-engines/docs/motion.md))*

**Good at:** a hybrid engine that hands transforms, `backgroundColor` and SVG to hardware-accelerated
browser APIs, and **real spring physics** that react to input velocity rather than replaying a
fixed curve. Its API is markedly smaller than the GSAP equivalent. Layout transitions and exit
animations are its distinctive features.

**Portable idea taken:** springs as a *curve*, and the browser-native path. The shell's `motion()`
helper already drives the Web Animations API directly rather than tweening styles in JavaScript,
which is Motion's core insight, minus the library.

### [anime.js](https://animejs.com/) — pinned at 3.2.2, 17 KB
*(lab: [`03-anime.html`](../lab/motion-engines/03-anime.html) · [`docs/anime.md`](../lab/motion-engines/docs/anime.md))*

**Read the link with care:** animejs.com documents **v4**, whose API is `animate()`,
`createTimeline()`, `createDraggable()`, `createScope()`, `onScroll()` and the SVG factories. This
repo vendors **3.2.2**, and eleven of those fourteen names do not occur in that file at all — see
[`docs/api-surface.md`](../lab/motion-engines/docs/api-surface.md). A `vendored-runtime` selection
gets `anime({targets, duration, easing, update, complete})`, not the API on the site.

**Good at:** breadth per byte. Timeline, keyframes, an SVG toolset (morphing, line drawing, motion
path), and the most developed **stagger** utilities of the three — time-based, value-based and
grid-position. The Draggable and Scope APIs the site leads with are v4 only.

**Portable idea taken:** almost none, deliberately. Stagger is anime.js's signature and this skill
**bans it** ([`motion.md`](motion.md)): six cards rising in sequence delays reading six times.
What was taken is the modular instinct — the shell's motion surface is five small functions, not
an engine.

---

## The D3 gallery, mapped onto this skill

| Gallery category | Status here |
|---|---|
| **Bars** | covered — `columns` `divColumns` `hbars` `divHbars` `lollipop` |
| **Lines** | covered — `line` `slope` `spark` |
| **Areas** | covered — `stackedArea` (streamgraph and horizon deliberately skipped: a wiggling baseline makes every band unreadable) |
| **Dots** | covered — `bubbles`. Beeswarm skipped; `bubbles` plus jitter answers the same question |
| **Analysis** | covered — `divColumns` (histogram) and `boxplot`. Density/violin skipped: a kernel bandwidth is a choice readers cannot see |
| **Radial** | `donut` only, capped at five parts. Radial bars and sunbursts encode magnitude as angle, which people read badly |
| **Annotation** | covered by the shell — help chips, card notes, direct endpoint labels |
| **Animation** | see [`motion.md`](motion.md). The gallery's bar-chart race is the canonical example of motion **replacing** analysis: it is a ranking over time, and a slope chart or a small-multiple grid says the same thing in one static screen |
| **Interaction** | partly — hover, tabs, filters, sortable tables. Brush-and-zoom is out of scope for a document you scroll |
| **Hierarchies** | out of scope — treemaps and sunbursts compare areas, which readers estimate poorly. Use a ranked bar chart with an indent |
| **Networks** | out of scope — a force-directed graph is a beautiful way to answer no question in particular. If topology matters, that is a different document |
| **Maps** | out of scope — needs geographic data and a projection. A region ranking (`hbars`) usually answers the question a choropleth is asked to |

The exclusions are the point. This is a catalogue for **reports someone must reason from**, not a
gallery of everything drawable.

---

## What was actually adopted

**Two chart forms** the gallery exposed as real gaps:

- `VIZ.boxplot` — compare the *shape* of a distribution across many groups. A histogram shows one
  distribution well; this shows twenty, comparably. Takes raw values (quartiles computed for you)
  or precomputed statistics. Outliers are drawn, not removed.
- `VIZ.stackedArea` — composition over time when **the total is the subject**. It prints its own
  caveat on the canvas: only the bottom band and the total share a flat baseline, so a middle band
  cannot be compared by eye. If a middle band is the subject, use `panels`.

**One behaviour**, taken from D3's keyed join:

- **`cfg.key` on `VIZ.hbars` and `VIZ.lollipop`.** Give a row a stable identity and `chart.play()`
  after a re-sort makes each mark travel from the row it held to the row it now belongs in, rather
  than regrowing from zero. That is object constancy, and it is the one thing in this file the
  shell could not do at all: a canvas repainted from scratch has no element whose identity could be
  kept, so the identity has to live in the factory instead. The port is about twenty lines — a
  previous-position map, a lerp, and a fade for rows that were not there before. Without a key
  nothing changes. The bound is in [`motion.md`](motion.md) § The fourth place: a re-sort only,
  never a filter, because a mark that travels claims to be the same thing somewhere else.

**An easing vocabulary** — the portable half of GSAP, Motion and anime.js:

| Value-safe (legal on a bar or an area) | Overshoot (opacity and position only) |
|---|---|
| `linear` `outCubic` `inOutCubic` `outQuint` `outExpo` `outCirc` `inOutQuint` | `outBack` `spring` |

The split is enforced, not advised. An overshoot curve makes `c.t` exceed 1, so a bar would draw
**past its own axis** for a few frames — slop-test gate 3. `anim()` refuses an overshoot easing on
a chart, warns in the console, and falls back to `outCubic`. Use them with `R.motion()` (opacity
and small translations) or `R.countUp()` (a settling figure), where nothing is scaled to an axis.

```js
chart.play(700, 'outExpo');        // fine
chart.play(700, 'spring');         // refused, warns, falls back
R.countUp(el, 1024, 900, R.compact, 'spring');   // fine — a number is not a mark
R.motion(node, {opacity:1}, {duration:300, easing:'outBack'});   // fine
```

---

## When to close this skill

Be honest about the boundary. Reach for the real tools when:

- **the deliverable is an application, not a document** — state, routing, live data → D3 or Plotly
  inside your framework, GSAP or Motion for the choreography;
- **someone must brush, zoom and re-query interactively** — that is a tool, and
  [`04-workbench.md`](macrostructures/04-workbench.md) is only the document-shaped end of it;
- **the data is geographic, hierarchical or a network** — the exclusions above are real; a
  different document type is the answer, not a worse chart.

A single self-contained file is a constraint chosen for a reason. When the reason stops applying,
stop applying the constraint.

**When you do stop applying it**, [`../lab/motion-engines/`](../lab/motion-engines/) is the worked
version of this page: four runnable pages, one per selected tool, on the same data and layout so
only the engine differs; the runtimes vendored and SHA-pinned; one doc each covering the minimum
call, what only that engine can do, and what you must add yourself. The lab's own finding is worth
carrying back — **none of these engines guarantees a final state.** When rAF stops (background tab,
headless capture, low-power mode) they freeze mid-frame, and a late frame will overwrite a value you
painted afterwards. The shell handles both with a timer and a token inside `anim()`; there, it is
your job.
