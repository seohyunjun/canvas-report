---
name: canvas-report
description: Turns any dataset into a self-contained interactive HTML analysis report drawn on canvas. Rotates macrostructure, theme and masthead so each report has a different face; leads with the insight; and gives every chart a hover tooltip, a table twin and a help tooltip. Use for "make me a report", "dashboard", "visualise this analysis", "canvas html", "interactive report", "data visualisation page", "make it look different this time".
version: 2.0.0
---

# Canvas Report

Turn one dataset into **a single HTML file a reader can explore for themselves.**

This skill merges two lineages. From `canvas-data-report` come the **analytical disciplines** —
data shape to lens, table twins, help tooltips, a methodology section. From `hallmark` come the
**design disciplines** — pick the macrostructure first, rotate themes on three axes, use named
archetypes, run anti-slop gates.

They are merged for one reason: **an accurate report that always looks the same never gets read
twice.**

The skill carries no domain knowledge. It looks only at the *shape* of the data — is there a time
column, is there an entity key, how many measures — and picks the lenses that shape can support.
Metric names, industry, currency and language all come from the input.

## Output contract

- **One `.html` file.** Zero network requests: no external scripts, fonts or images. Data is
  embedded in a `<script type="application/json">` block.
- Every chart is drawn directly on `<canvas>` 2D. No charting library is fetched.
- Write to the path the user gave; otherwise ask. Name it `<subject>-<period>.html`.
- **A stamp at the top of the file.** The next report's rotation reads it.

```
canvas-report · macro: 05 Broadsheet · theme: newsprint · masthead: M3 · lenses: trend,comparison,outliers
critique: P4 H5 E4 S5 R4 V5 D5
```

## Absolute rules

1. **No dual axes.** Two metrics in different units never share a chart → separate charts, or `VIZ.panels`.
2. **The axis range comes from the data.** Back-computing it from the tick list puts bars outside the plot.
3. **Colour is used by role.** Identity = `s1 s2 s3`; magnitude = one hue; direction = `pos`/`neg`
   with a neutral `mid`. No rainbows, no value gradients on nominal categories, no hex on the canvas.
4. **Every chart owes a table twin.** A tooltip supplements; it is never the only route.
5. **Every chart card gets one help chip.** This is a requirement of the skill, not a nicety.
6. **Value labels are selective.** Endpoints, extremes and the key series only.
7. **The animation always ends.** Even if rAF stops, the final state must draw (the shell does this).
8. **Never hide a limitation.** The last section carries basis, units, formulas and limits.
9. **Never ship the previous report's face.** Rotate macrostructure, theme and masthead.
10. **Never invent a number.** A metric the user did not supply is `—` and "to confirm", or the
    lens is dropped.

---

## Procedure

### Reading order — four files are not optional

The reference map at the bottom of this file is an index, not a menu. **Four of those files are
read on every report**, at the step that needs them, before you write the code for that step:

| Read it | At | Because skipping it costs you |
|---|---|---|
| [`references/analysis-lenses.md`](references/analysis-lenses.md) | step 0–1 | you build a lens the shape cannot carry, or blow past its judgement rules (period count, cardinality, key checks) |
| [`references/pitfalls.md`](references/pitfalls.md) | step 5, before the wiring | you re-step a mine the shell already fixed — canvas height, cached tokens, an unchecked key |
| [`references/motion.md`](references/motion.md) | step 6 | you animate somewhere motion does not belong, or pick an easing that draws past the axis |
| [`references/tooltip-help.md`](references/tooltip-help.md) | step 7 | help copy that names the chart type and forgets the formula |

[`references/anti-patterns.md`](references/anti-patterns.md) stays open the whole time.
The rest are conditional and the map says when.

**If you have not read a file, do not claim its gates.** Reporting a passing slop test on
references you never opened is the one failure this skill cannot detect for you.

### 0. Profile the data — shape, not domain

Actually load or query it first and establish the following. **Do not guess; query.**

| Check | Why |
|---|---|
| columns, types, null rates | whether a date is a string or a DATE changes every filter |
| the time column and its grain (day/month/quarter) | whether the trend lens is available at all |
| candidate entity keys and their **distinct count** | a masked or recycled key makes cohort analysis quietly wrong |
| which fields are measures (continuous) and which are dimensions (categorical) | decides which charts are possible |
| cardinality per dimension | past 8, it is top-N plus other, or small multiples |
| placeholder and sentinel values | `unclassified`, `N/A`, `-1`, `9999` leave the aggregates but stay in the totals |
| whether two periods can be compared | whether the flow (bridge) and direction lenses are available |

**Read [`references/analysis-lenses.md`](references/analysis-lenses.md) now** — the whole file,
not only the mapping table. Take the profile to it and **build only the lenses the shape supports.**
A lens the data cannot carry is not included at all.

Its judgement rules bind as hard as the mapping table does: under 6 periods is not a trend, over 25
defaults to the most recent 12–13, cardinality over 8 folds, and **a bridge or a cohort gets its key
checked with `COUNT(DISTINCT)` against `COUNT(*)` before it is built** — with the residual written
into the methodology. Deviating from one of them is allowed; deviating silently is not.

### 1. Fix the insights before the charts

Write **four to six sentences** first. Each contains a number and each must be falsifiable.
These become the insight cards and they determine the section order.
Write "what is true", not "here is the data".

Look especially for **where two totals fail to reconcile.** A stock mixed with a flow, entities
entering and leaving, two aggregates with different definitions — that is where the report is.

### 2. Look up the previous report — skip this and you will always produce the same one

Read `.canvas-report/log.json` in the project root. Failing that, read the stamp comment at the
top of another report HTML in the same folder. If neither exists, this is the first one.

```json
[
  { "date": "2026-09-04", "macro": "05 Broadsheet", "theme": "newsprint", "masthead": "M3",
    "lenses": ["trend", "comparison", "outliers"], "subject": "quarterly intake" }
]
```

Take **macrostructure · theme · masthead** from the last three to five entries. That is the
exclusion list for the next two steps.

### 3. Pick the macrostructure first — before the charts, before the theme

Read only the **index** in [`references/macrostructures.md`](references/macrostructures.md), pick
one name, then read **only that one file** in `references/macrostructures/`. Never read them all.

The order: ① drop any macro whose data requirement you cannot meet → ② narrow by what the reader
came to do → ③ drop anything in the last three entries → ④ choose from what remains.

Even on a first report with no constraints, **do not default to 01 Briefing.** Any data can carry
it, which is why you land there without thinking. Choose it only when the data really is
briefing-shaped.

### 4. Pick the theme and the masthead

One from the catalogue in [`references/themes.md`](references/themes.md). **At least one of the
three axes** (paper band · display class · accent hue) must differ from the previous report.

The masthead is one of M1–M6 in [`references/components.md`](references/components.md), different
from last time.

**Declare it in one line before writing code.** On the page, not in your head.

> *"Macro: 05 Broadsheet. Theme: newsprint (light · roman-serif · warm). Masthead: M3.
> Differs from the last (01 Briefing · almanac · M2) on all three."*

If the brief is genuinely vague — no theme hint, no tone — do not fall back to a default. Offer
**three from categorically different groups**: one grid-led (06 Poster), one document-led
(05 Broadsheet), one tool-led (04 Workbench). Three concrete options, not seven abstract tones.

### 5. Copy the shell and swap the theme

```bash
cp assets/report-shell.html <dest>/<subject>-<period>.html
python3 assets/apply-theme.py <dest>/<subject>-<period>.html <theme>
```

The shell is a **finished runtime** that runs a demo if you just open it. There are five places
to change, marked in the header comment: `[T]` theme tokens · `[L]` UI strings · `[1]` masthead
and copy · `[2]` the data JSON · `[3]` REPORT WIRING.

**Do not touch** the `[S]` structure layer, the tooltip engine, the `VIZ` factories or the table
builder. The bugs in them are already fixed.

**Read [`references/pitfalls.md`](references/pitfalls.md) before you write a line of wiring.**
Not only when you add a factory — its *Layout*, *Runtime*, *Numbers* and *Data* sections are about
the code **you** are about to write. Three that catch wiring authors every time: a canvas height set
in CSS is ignored (the height comes from the `<canvas height="…">` **attribute**), a colour cached
from `R.tokens()` outside the paint function goes stale, and an unchecked entity key makes a bridge
lie in silence.

`VIZ` factories: `line` `columns` `divColumns` `hbars` `divHbars` `panels` `bubbles` `waterfall`
`spark` `donut` `heatmap` `slope` `lollipop` `boxplot` `stackedArea`. All take `(canvas, cfg)`,
and `cfg.rows()` is a **function** so a filter change is picked up. Pass colours as **token names**
(`'s1'`), never hex.

`chart.play(duration, easing)` takes any of nine named curves; overshoot curves are refused on
charts and allowed on `R.motion()` / `R.countUp()`. See [`references/motion.md`](references/motion.md).

Runtime helpers: `R.helpDot` `R.wireHelp` `R.buildTable` `R.wireToggles` `R.onView` `R.onTheme`
`R.reveal` `R.countUp` `R.scrolly` `R.shrinkMasthead` `R.reduced` `R.paintAll` `R.tokens`.

**Writing a report in another language?** Translate the `[L] CR_STRINGS` block, set
`<html lang="…">` so `Intl` formats numbers correctly, and write your own copy in the wiring.
Nothing else changes.

### 6. Wire the sections

**Follow the section rhythm in your macrostructure file.** The order below is only the default
when the macro does not specify one (and only for lenses the data supports).

```
summary       1 hero figure + 3-4 stat tiles + 4-6 insight cards
01 trend      change over time. One axis per metric.
02 flow       opening-to-closing bridge. Where canvas motion earns the most.
03 distribution  counts and magnitudes per bucket. What the mean hides.
04 comparison magnitude and direction by dimension. Separate charts for each.
05 relationship  two metrics as a scatter; size = magnitude, colour = direction.
06 outliers   top and bottom rankings, with tabs to change the basis.
07 basis and limits  definitions, units, formulas, what it cannot do.
```

Pick the part archetypes — section head S1–S5, insight I1–I5, chart card C1–C5, filter F1–F4,
methodology Ft1–Ft4 — from [`references/components.md`](references/components.md).
**Use one section-head and one insight archetype across the whole report**; changing them per
section destroys the table of contents.

A filter goes on **one line directly above the group it governs**, never inside a chart card.

**Read [`references/motion.md`](references/motion.md) now.** Motion is confined to the three places
it names — the waterfall's flow, scroll transitions, and play-once-on-entry. Delete the rest, and
take the easing from its value-safe column: an overshoot curve on a chart draws the mark past its
own axis.

### 7. Wire the help tooltips — a requirement of this skill

Reader-facing explanation is a **tooltip**, not a separate note. Same engine as the value
tooltip, different shape. **Read [`references/tooltip-help.md`](references/tooltip-help.md) now** —
it fixes the copy order, caps you at three sentences, bans naming the chart type, and requires the
word "estimate" inside the tooltip whenever the number is one.

```js
// the question chip beside a chart title
titleEl.appendChild(R.helpDot('Title', 'What am I looking at. How do I read it. What can I do.', 'caveat (optional)'));

// a dotted underline on a term or metric
<span class="help-term" data-help-title="Churn rate" data-help="The denominator is the opening entity count."
      data-help-note="Do not confuse with the similarly named gross rate">churn rate</span>

R.wireHelp();   // wires hover, keyboard focus and touch tap
```

- Every chart card gets **at least one** help chip.
- Every computed metric (a rate, an estimate, an index) gets a definition tooltip.
- No information exists only in a tooltip — the same content is in the methodology too.

Wiring order: `R.wireHelp() → R.wireToggles() → R.reveal() → R.paintAll()`.

### 8. Write the methodology

Three blocks, whichever archetype (Ft1–Ft4) you chose.

- **Data basis** — source table or file, row count, observation unit ("1 row = one what"),
  inclusion and exclusion rules.
- **Formulas** — every derived metric as a formula. Estimates say "estimate".
- **Known limits** — totals that do not reconcile, weaknesses in the key, collection lag,
  code-system changes, and **what this data cannot see.**

Limits do not cost you trust. They build it. Everything odd you found goes here.

### 9. Render it and look at it — do not skip this

A validator only sees colour. Layout is only caught in a screenshot.

```bash
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --force-prefers-reduced-motion \
  --virtual-time-budget=9000 --window-size=1240,8000 \
  --screenshot=out.png "file:///absolute/path.html"
```

- `--force-prefers-reduced-motion` is **required**. Without it you capture a mid-animation frame
  and misdiagnose it as a cut-off chart.
- Shoot 1240 / 768 / 500. For the dark drop, temporarily set `data-theme="dark"` on `<html>`
  (never `--force-dark-mode`, which recolours the page).
- Headless clamps the viewport to 500px minimum; anything narrower only crops the screenshot.
- Judge horizontal overflow by **measuring** `document.documentElement.scrollWidth` against
  `innerWidth`, not by looking.
- Watch for: colliding labels, marks outside the plot, clipped text, values off-axis, blank
  canvases, an `N rows omitted` note you did not expect, and **charts that are all black or grey**
  (a colour-parsing failure — check the tokens are hex).

### 10. Run the slop test and record the result

Pass the 42 gates in [`references/slop-test.md`](references/slop-test.md).
**Do not read that file while generating** — the gates are a post-hoc check; the in-flight
reference is [`references/anti-patterns.md`](references/anti-patterns.md).

If anything in group D (data honesty, 1–12) trips, the rest is meaningless. Fix and re-run.

On passing, score the seven axes (P H E S R V D), put them in the stamp, and prepend this report
to `.canvas-report/log.json`. Create the file if it does not exist.

---

## Reference map

| File | When to read it |
|---|---|
| [`assets/report-shell.html`](assets/report-shell.html) | step 5. The runtime you copy; it runs a demo as-is |
| [`assets/themes.css`](assets/themes.css) | never directly — `apply-theme.py` reads it |
| [`assets/apply-theme.py`](assets/apply-theme.py) | step 5. Swapping the theme |
| [`references/analysis-lenses.md`](references/analysis-lenses.md) | **always**, steps 0–1. Data shape → lens → chart, and the judgement rules |
| [`references/macrostructures.md`](references/macrostructures.md) | step 3. **Index only**, then one file |
| [`references/themes.md`](references/themes.md) | step 4. Catalogue and the rotation rule |
| [`references/components.md`](references/components.md) | steps 4 and 6. Masthead, section head, insight, card archetypes |
| [`references/motion.md`](references/motion.md) | **always**, step 6. Where movement belongs, and the easing vocabulary |
| [`references/external-tools.md`](references/external-tools.md) | when tempted by D3, Plotly, GSAP, Motion, anime.js, Lottie or Rive |
| [`references/tooltip-help.md`](references/tooltip-help.md) | **always**, step 7. Help copy and accessibility |
| [`references/anti-patterns.md`](references/anti-patterns.md) | while generating. The named failures |
| [`references/pitfalls.md`](references/pitfalls.md) | **always**, step 5, before the wiring. Not just for factory authors — Layout · Runtime · Numbers · Data are about the wiring |
| [`references/slop-test.md`](references/slop-test.md) | step 10. **Only after it is built** |

If the `dataviz` skill is available, it is the higher authority on colour. The palettes in
`themes.css` already pass its rules.

## When the request is not a report

- **Just one chart** → do not use the whole shell. Lift one `VIZ` factory and the token block.
  No macrostructure, no rotation, no stamp.
- **Edit an existing report** → read its stamp and keep the **same** macro and theme. Rotation
  applies to new reports only. Re-score the critique line.
- **Change only the theme** → one `apply-theme.py` run, then render both drops again and look.
- **Another language** → translate `[L] CR_STRINGS`, set `<html lang>`, write the copy in the
  wiring. The structure, the gates and the rotation are unchanged.
- **No data** → do not build it. Ask what data, in what form, would let you start. A report made
  from sample data is a mockup, and mockups are not what this skill does.
