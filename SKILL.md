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
read:
  analysis-lenses  "Past 25 periods, default the view to the most recent 12–13"  -> 31-day series kept, deviation recorded in the methodology
  motion           "| redraw after a filter change | **0ms** |"                    -> tab switch repaints instead of playing
critique: P4 H5 E4 S5 R4 V5 D5
```

**The `read:` block is a quote block, not a checklist.** One line per reference file you opened
while building *this* report, and each line carries three things:

```
  <file>[ §<section>]  "<a verbatim fragment from it>"  -> <the decision that fragment made>
```

A file name alone does not count. The fragment must be **copied from the open file**, long enough
to be found in it with a plain string search, and it must be the passage that actually changed
what you did — not the first sentence of the document. The decision after the arrow must be
visible in the report.

This is the point: **a quote cannot be produced from memory of having read something.** Listing a
file you did not open now requires fabricating text that a `grep -F` against the repo will not
find, which is a different and much more obvious kind of wrong. Before you ship, run that check on
your own stamp.

A file you opened and took nothing from is not listed. If none of the always-read files produced a
decision worth quoting, that is the signal you skimmed rather than read — go back.

**Pick a fragment that survives an edit.** Quote the sentence, not its list number: a quote that
starts `13. Every chart has a table twin` breaks the moment a gate is inserted above it, and the
report then cites a line that no longer exists. Drop the ordinal and quote
`Every chart has a table twin` instead. Adding to a reference is safe; renumbering is not, so do
not put a number inside the quotation marks.

**A file this skill binds to more than one step needs one entry per section, named.** A single
quote proves you opened the file; it says nothing about *which part*. `external-tools.md` is the
case that exists today — its form map and "when to close" belong to step 0 and its adopted forms
and easing vocabulary to step 6, so it takes **two** entries:

```
  external-tools §gallery  "<fragment from the form map or when-to-close>"  -> <step 0 decision>
  external-tools §adopted  "<fragment from What was actually adopted>"      -> <step 6 decision>
```

Missing the second entry is the same failure as missing the file: you chose a form and a curve
without reading the page that lists what this skill added and which curves are legal on a mark.

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

### Reading order — five files, every report, and you write down that you read them

The reference map at the bottom of this file is an index, not a menu. **Five of those files are
read in full on every report**, at the step that needs them, before you write the code for that step:

| Read it | At | Because skipping it costs you |
|---|---|---|
| [`references/analysis-lenses.md`](references/analysis-lenses.md) | step 0–1 | you build a lens the shape cannot carry, or blow past its judgement rules (period count, cardinality, key checks) |
| [`references/uncertainty.md`](references/uncertainty.md) | step 1, with the insights | you write "X went up" where the data only supports "X is 13.2%" — a comparison shipped without a denominator, an interval and a reference |
| [`references/pitfalls.md`](references/pitfalls.md) | step 5, before the wiring | you re-step a mine the shell already fixed — canvas height, cached tokens, an unchecked key |
| [`references/motion.md`](references/motion.md) | step 6 | you animate somewhere motion does not belong, or pick an easing that draws past the axis |
| [`references/tooltip-help.md`](references/tooltip-help.md) | step 7 | help copy that names the chart type and forgets the formula |
| [`references/external-tools.md`](references/external-tools.md) | step 0, with the lens table | you draw a form this skill refuses, miss the two forms it adopted, or keep writing a report the data says should be a different document |

**external-tools.md is read whole, not skimmed for the library verdicts.** Its four working parts
each bind a different step: **§ The D3 gallery, mapped onto this skill** is the form vocabulary and
the refusal list (hierarchies, networks, maps, streamgraph, violin, beeswarm, radial bars) — step 0,
beside the lens table. **§ When to close this skill** says when the data means you should be writing
a different document — step 0, before you commit. **§ What was actually adopted** names the two
forms this skill added because the gallery exposed them as gaps (`boxplot`, `stackedArea`) and the
easing vocabulary — step 6, when you choose a form and a curve. Only **§§ A–C**, the library
assessments, stay conditional.

**Use what it adopted.** `VIZ.boxplot` exists because "what does the mean hide" is a question a
histogram cannot answer across groups; if your data has a measure and a grouping with enough values
per group, that question is usually worth one card. `chart.play()` takes nine named curves and
defaults to `outCubic` — reach past the default only for a reason you can name, and name it in a
comment.

[`references/anti-patterns.md`](references/anti-patterns.md) stays open the whole time.
The rest are conditional and the map says when.

**If you have not read a file, do not claim its gates.** Reporting a passing slop test on
references you never opened is the one failure this skill cannot detect for you — which is why
the stamp carries a `read:` line and the log entry carries a `"read"` list. Write each file into
it as you open it. Content you happen to remember from another task is not a read; if it is not
open in front of you for *this* build, it does not go on the line.

**The decision must not contradict the fragment.** The quote check only proves you copied the
text; it cannot see the arrow. A report shipped with

```
  motion   "Play once on entry"   -> only the lead chart plays; the column charts stay static
```

— verbatim quote, invented rule, two of three charts frozen. Before you write the arrow, read the
fragment once more and ask whether the decision is an application of it or an exception to it. An
exception is allowed, but it is stated as one, with the reason.

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

Read [`references/external-tools.md`](references/external-tools.md) alongside it. The lens table
says what you *can* build from this shape; **§ The D3 gallery, mapped onto this skill** says what
this skill has decided *not* to draw and why, **§ When to close this skill** says when the honest
answer is a different document rather than a worse chart, and **§ What was actually adopted** says
which two forms were added to close real gaps — check whether your shape wants one of them before
you settle on the safe pair of bars and lines.

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

**Read [`references/uncertainty.md`](references/uncertainty.md) here, while the sentences are still
being written.** Each insight is about to become a claim, and it decides which of them you have
earned. A magnitude ("직거래는 324건, 13.2%") is always safe. A comparison ("직거래가 늘었다") needs
a denominator, an interval and the reference it is measured from, or it gets rewritten as a
magnitude. The shell ships `R.wilson(k,n)` for shares; medians and ratios get a seeded bootstrap at
build time, never in the browser. And if the data is a census rather than a sample — a billing
export is — say so and draw no interval at all.

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
`spark` `donut` `heatmap` `slope` `lollipop` `boxplot` `stackedArea` `concentration` `interval`.
All take `(canvas, cfg)`,
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

**Read [`references/motion.md`](references/motion.md) now.** Motion is confined to the four places
it names — the waterfall's flow, scroll transitions, play-once-on-entry, and a keyed re-sort.
Confined, but **required**: play-once-on-entry is every chart's default, wired in one call
(`R.playAll(700)`), and a chart that stays still is declared `static:true` with the reason in the
methodology. Wiring the lead chart and leaving the rest flat is the single most common defect in
this skill's output. Delete everything outside the four places, and
take the easing from its value-safe column: an overshoot curve on a chart draws the mark past its
own axis. The same nine curves are catalogued in
[`references/external-tools.md`](references/external-tools.md) **§ What was actually adopted**
together with the two adopted forms — if a section is about a distribution across groups, that is
where `VIZ.boxplot` is supposed to come from.

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

Wiring order: `R.wireHelp() → R.wireToggles() → R.reveal() → R.paintAll() → R.playAll(700)`.
`R.playAll` last: it wires play-once-on-entry for every chart built above it.

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
- **This run says nothing about motion.** The flag omits the animation, and `--virtual-time-budget`
  freezes `requestAnimationFrame` besides, so progress reads one constant value however long you
  sample. Motion is checked separately, on a real clock:

  ```bash
  python3 assets/check-motion.py report.html
  ```

  It reports per chart whether anything plays it on entry and whether it lands on its final state,
  and exits non-zero if one never moves. Gates 46–48 are this command.
- Shoot 1240 / 768 / 500. For the dark drop, temporarily set `data-theme="dark"` on `<html>`
  (never `--force-dark-mode`, which recolours the page).
- Headless clamps the viewport to 500px minimum; anything narrower only crops the screenshot.
- Judge horizontal overflow by **measuring** `document.documentElement.scrollWidth` against
  `innerWidth`, not by looking.
- Watch for: colliding labels, marks outside the plot, clipped text, values off-axis, blank
  canvases, an `N rows omitted` note you did not expect, and **charts that are all black or grey**
  (a colour-parsing failure — check the tokens are hex).

### 10. Run the slop test and record the result

Pass the 48 gates in [`references/slop-test.md`](references/slop-test.md).
**Do not read that file while generating** — the gates are a post-hoc check; the in-flight
reference is [`references/anti-patterns.md`](references/anti-patterns.md).

If anything in group D (data honesty, 1–12) trips, the rest is meaningless. Fix and re-run.

On passing, score the seven axes (P H E S R V D), put them in the stamp, and prepend this report
to `.canvas-report/log.json`. Create the file if it does not exist.

**Fill the stamp's `read:` block, then verify it.** Each entry needs a verbatim fragment and the
decision it drove; copy the same entries into the log entry as `"read"`. Then check every quote
against its file before you ship:

```bash
grep -Fq '<the quoted fragment>' references/<file>.md || echo "FABRICATED: <file>"
```

Run it for every line, and check that every multi-step file has all of its sections present — for
`external-tools.md` that means both `§gallery` and `§adopted`. A quote that does not match is not a
typo to patch — it means you wrote down a file you did not read, and the fix is to go and read it. Never carry an entry over because
the file was read in an earlier session or an earlier task in the same session; the block records
this build and nothing else.

---

## Reference map

| File | When to read it |
|---|---|
| [`assets/report-shell.html`](assets/report-shell.html) | step 5. The runtime you copy; it runs a demo as-is |
| [`assets/themes.css`](assets/themes.css) | never directly — `apply-theme.py` reads it |
| [`assets/apply-theme.py`](assets/apply-theme.py) | step 5. Swapping the theme |
| [`references/analysis-lenses.md`](references/analysis-lenses.md) | **always**, steps 0–1. Data shape → lens → chart, and the judgement rules |
| [`references/uncertainty.md`](references/uncertainty.md) | **always**, step 1. Which comparisons you have earned; Wilson, bootstrap, MAD; `VIZ.interval` and `VIZ.concentration` |
| [`references/macrostructures.md`](references/macrostructures.md) | step 3. **Index only**, then one file |
| [`references/themes.md`](references/themes.md) | step 4. Catalogue and the rotation rule |
| [`references/components.md`](references/components.md) | steps 4 and 6. Masthead, section head, insight, card archetypes |
| [`references/motion.md`](references/motion.md) | **always**, step 6. Where movement belongs, and the easing vocabulary |
| [`references/external-tools.md`](references/external-tools.md) | **always**, step 0 (form map · when to close) and step 6 (the two adopted forms · the easing vocabulary). §§ A–C when tempted by D3, Plotly, GSAP, Motion, anime.js, Lottie or Rive |
| [`references/tooltip-help.md`](references/tooltip-help.md) | **always**, step 7. Help copy and accessibility |
| [`references/anti-patterns.md`](references/anti-patterns.md) | while generating. The named failures |
| [`references/pitfalls.md`](references/pitfalls.md) | **always**, step 5, before the wiring. Not just for factory authors — Layout · Runtime · Numbers · Data are about the wiring |
| [`references/slop-test.md`](references/slop-test.md) | step 10. **Only after it is built** |
| [`lab/motion-engines/`](lab/motion-engines/) | never during a report — it breaks the output contract on purpose. Worked examples of the five motion engines for when step 0 says to close this skill |

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
