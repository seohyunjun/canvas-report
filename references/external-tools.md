# External tools — what to borrow, what to refuse

This skill ships one HTML file with **zero network requests**. That is not a stylistic
preference: it is what makes a report survive being emailed, opened offline, archived, and
re-opened in five years. Every library on this page is therefore **unusable as a dependency here**.

That does not make them useless. Each one is a body of craft, and the craft is portable even when
the code is not. This page records what each tool is actually good at, what this skill took from
it, and — just as important — when you should close this skill and reach for the real thing.

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

All three are excellent, all three are a network request or a build step, and **all three solve a
problem this skill does not have.** They animate a document. This skill animates a canvas, where
`c.t` is one number that every factory already reads.

### [GSAP](https://gsap.com/) — now free for everyone

**Good at:** choreography. Timelines that nest, and a plugin ecosystem nothing else matches —
ScrollTrigger, MorphSVG, MotionPath, DrawSVG, SplitText, Draggable. If you need to sequence
thirty things against a scrollbar, GSAP is the answer and it is not close.

**Portable idea taken:** the easing catalogue. A named curve set is the part of GSAP you can
retype in twenty lines, and this skill now ships one (see below).

### [Motion](https://motion.dev/) — MIT, formerly Framer Motion

**Good at:** a hybrid engine that hands transforms, `backgroundColor` and SVG to hardware-accelerated
browser APIs, and **real spring physics** that react to input velocity rather than replaying a
fixed curve. Its API is markedly smaller than the GSAP equivalent. Layout transitions and exit
animations are its distinctive features.

**Portable idea taken:** springs as a *curve*, and the browser-native path. The shell's `motion()`
helper already drives the Web Animations API directly rather than tweening styles in JavaScript,
which is Motion's core insight, minus the library.

### [anime.js](https://animejs.com/) — 24.5 KB core, modular

**Good at:** breadth per byte. Timeline, keyframes, an SVG toolset (morphing, line drawing, motion
path), a Draggable API with spring physics, a Scope API for responsive animation, and the most
developed **stagger** utilities of the three — time-based, value-based and grid-position.

**Portable idea taken:** almost none, deliberately. Stagger is anime.js's signature and this skill
**bans it** ([`motion.md`](motion.md)): six cards rising in sequence delays reading six times.
What was taken is the modular instinct — the shell's motion surface is five small functions, not
an engine.

---

## C. Runtime-dependent animation formats

### [Lottie / LottieFiles](https://lottiefiles.com/) · [Rive](https://rive.app/)

**Lottie** is an After Effects animation exported to JSON by Bodymovin and replayed by a player
library — `lottie-web`, or the newer dotLottie player, which is a **Rust + WASM core** (ThorVG)
with software, WebGL2 and WebGPU backends.

**Rive** is a vector animation format with a **State Machine**, played by a GPU-accelerated runtime.
Its state machine is a genuinely good idea: designers author interactive states rather than handing
developers a linear clip.

**Verdict for this skill: no, and not "no, unless".** Both need a runtime download measured in
hundreds of kilobytes plus an asset file. Inlining a WASM runtime as base64 inside a data report
would be absurd, and the pay-off would be a decorative animation — the exact thing
[`anti-patterns.md`](anti-patterns.md) calls out. If a report needs a designed illustration,
draw it in the canvas or leave it out.

**Where they are the right answer:** a marketing page, an onboarding flow, an empty state, a
product tour. Not an analysis anyone has to reason about.

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
- **the artefact is a designed animation** — an illustration, a mascot, an onboarding sequence →
  Lottie or Rive, and neither belongs in an analysis;
- **the data is geographic, hierarchical or a network** — the exclusions above are real; a
  different document type is the answer, not a worse chart.

A single self-contained file is a constraint chosen for a reason. When the reason stops applying,
stop applying the constraint.
