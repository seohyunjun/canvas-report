# Analysis lenses — from data shape to chart

The table that decides what you can honestly show, without knowing the domain.
**Build a lens only when its data shape is true.**

## The mapping

| Lens | Data shape it needs | Question it answers | Shell factory | Gate |
|---|---|---|---|---|
| **Trend** | a time column + 1 measure, 6+ periods | is it rising or falling, is there seasonality | `VIZ.line` | `trend` |
| **Composition over time** | time + 2–3 measures **in the same unit** | which of two forces is winning | `VIZ.columns` | `trend` |
| **Composition of a total** | time + 2–4 parts summing to a meaningful total, non-negative | is the total growing, and which part carries it | `VIZ.stackedArea` | `trend` |
| **Flow (bridge)** | an entity key + two points in time | where did the net change come from | `VIZ.waterfall` | `cohort` |
| **Distribution (one group)** | 1 measure, one row per entity | does the mean represent anything, where does it pile up | `VIZ.divColumns` | `distribution` |
| **Distribution (many groups)** | 1 measure + 1 dimension, ≥ 5 values per group | which groups are wide, skewed, or full of outliers | `VIZ.boxplot` | `distribution` + `comparison` |
| **Comparison (size)** | 1 dimension + 1 measure, cardinality ≤ 20 | who is big | `VIZ.hbars` | `comparison` |
| **Comparison (direction)** | the above + two periods | who grew and who shrank | `VIZ.divHbars` | `comparison` |
| **Comparison (multi-metric)** | 1 dimension + 2–3 measures in **different units** | is the biggest also the most numerous | `VIZ.panels` | `comparison` + `relationship` |
| **Relationship** | 2 measures per entity (+ size, + direction) | do the two move together | `VIZ.bubbles` | `relationship` |
| **Rank movement** | 1 measure at two points in time, ≤ 12 entities | who overtook whom | `VIZ.slope` | `relationship` |
| **Cross-tab intensity** | 2 dimensions + 1 non-negative measure, ≤ 100 cells | where is the grid hot | `VIZ.heatmap` | `comparison` |
| **Ranking (sparse)** | 1 dimension + 1 measure, ≤ 20 items | ranking where bars would be too heavy | `VIZ.lollipop` | `comparison` |
| **Parts of a whole** | 2–5 nominal parts, non-negative | is one part dominant | `VIZ.donut` | `comparison` |
| **Outliers** | an entity key + a sortable measure | who produced the result | `VIZ.hbars` + tabs | `comparison` |
| **Concentration** | 1 measure over 5+ entities, non-negative | how much of the total comes from how few | `VIZ.concentration` | `comparison` |
| **Uncertainty** | a point estimate + an interval per row | is this difference mine to claim | `VIZ.interval` | `relationship` |

## Eligibility, in two steps

`assets/select-candidates.py` runs before the plan is written and emits a `lenses` block: five
gates, each with an `eligible` flag and, when it fails, the reason. Those five are coarse; the
seventeen above are the actual choices. The **Gate** column is the join between the two — a lens is
arguable only once its gate is eligible.

What each gate tests, and nothing more:

| Gate | Eligible when the profile shows |
|---|---|
| `trend` | a `date`/`datetime` column with `distinct_count ≥ 6`, plus one numeric column |
| `comparison` | one `string`/`boolean` column, plus one numeric column |
| `distribution` | one numeric column |
| `relationship` | two numeric columns |
| `cohort` | a name in `candidate_keys`, plus a `date`/`datetime` column |

The three time lenses share the `trend` gate and inherit its six-period test, which is the right
answer rather than a strict one: below six periods the shape is a comparison, not a trend, and the
Judgement rules say to demote it.

Nothing in that table counts rows per group, checks that two measures share a unit, tests whether
parts sum to a total, or reads a single cell — the profile never sees cell values. **An eligible
gate is permission to consider a lens, never evidence for it.** The middle column of the mapping is
what you still have to establish, and these are the profile fields that establish it:

| To establish | Read |
|---|---|
| how many marks any chart will draw | `row_count` — one number, for every chart in the report |
| whether a measure goes negative | `columns[].min` |
| the cardinality of a dimension | `columns[].distinct_count` |
| how many periods there are, and how they are spaced | `columns[].distinct_count` on the date column, and `time_grains[<column>]` |
| whether two periods exist to compare at all | `comparable_periods` |
| whether an entity key is trustworthy | `candidate_keys` |
| whether a measure is really a measure | `columns[].type` — `integer` or `number`; `mixed` is not numeric, and `CHART-010` will say so |
| whether the aggregate is polluted | `columns[].null_rate`, `columns[].sentinel_candidates` |

`candidate_keys` is worth naming twice. It is `COUNT(DISTINCT key) = COUNT(*)` already computed —
the profiler lists a column only when it is fully distinct and never null. A key **absent** from
that list is exactly the masked or recycled case, so a bridge or a cohort built on it is the silent
lie the Judgement rules warn about, and the profile told you before the plan was written.

## Asking for one

Every factory in that table compiles from a plan. A chart names its `type` and maps each **role**
the factory reads to one profiled column; the roles below are the whole vocabulary, and
`assets/validate-plan.py` rejects a role a type does not read (`CHART-008`) as firmly as a missing
one (`CHART-005`).

| `type` | Required roles | Optional | Rows the factory accepts | Measures it will not take negative |
|---|---|---|---|---|
| `line` | `x` `value` | — | any | — |
| `columns` | `x` `value` | `value2` `value3` | any | — |
| `divColumns` | `label` `value` | — | any | — |
| `hbars` | `label` `value` | — | any | — |
| `lollipop` | `label` `value` | — | ≤ 20 | — |
| `divHbars` | `label` `value` | — | any | — |
| `waterfall` | `label` `value` | — | any | — |
| `panels` | `label` `value` `value2` | `value3` | any | — |
| `slope` | `label` `before` `after` | — | ≤ 12 | — |
| `boxplot` | `label` `lo` `q1` `med` `q3` `hi` | — | any | — |
| `interval` | `label` `value` `lo` `hi` | — | any | — |
| `bubbles` | `label` `x` `y` `size` | — | any | `x` `y` `size` |
| `heatmap` | `x` `y` `value` | — | ≤ 100 cells | `value` |
| `stackedArea` | `x` `value` `value2` | `value3` | ≥ 2 | every series |
| `donut` | `label` `value` | — | 2–5 | `value` |
| `concentration` | `label` `value` | — | ≥ 2 | `value` |

Four things this table is quietly telling you.

**Roles are typed, per chart.** `value`, `before`, `after`, `lo`, `hi`, `q1`, `med`, `q3` and
`size` must land on a profiled measure. `x` and `y` are measures on `bubbles` and categories on
`heatmap`, which is why the check is per type (`CHART-010`). A category in a measure role does not
fail loudly: the mark is drawn at length NaN, which is no mark at all.

**A row cap applies to the whole source, not to the chart — and the caps intersect.** The builder
hands one `rows` array to every chart, and the validator measures every chart against the profile's
single `row_count`. A cap is therefore not local to the chart that carries it: one five-slice
`donut` makes the whole report a five-row report, and every other chart on the page — and every
table twin — then has at most five rows to draw. The tightest cap among the selected types governs
all of them.

| A plan containing | constrains `row_count` to |
|---|---|
| `donut` | 2–5 |
| `slope` | ≤ 12 |
| `lollipop` | ≤ 20 |
| `heatmap` | ≤ 100 |
| `stackedArea` or `concentration` | ≥ 2 |

So `donut` alongside `lollipop` is a five-row report, not a twenty-row one, and `donut` alongside
`stackedArea` leaves a window of 2–5. Aggregate before profiling, or choose forms without a cap.
Past a cap the runtime prints a message where the data should be, so the validator refuses the plan
first (`CHART-007`, `CHART-009`).

**Three series is the ceiling.** `columns`, `stackedArea` and `panels` read `value`, `value2` and
`value3`, painted `s1`, `s2`, `s3`, and the builder emits the legend that names them — by column
name, so the key and the table twin cannot disagree. There is no `value4`, because
[`themes.md`](themes.md) will not invent a fourth colour. `donut` past three parts hits the same
wall from the other side: the factory cycles the same three, so parts four and five repeat parts
one and two. `CHART-013` warns about it.

**`waterfall` draws each step from the zero line**, not stacked onto the one before, so it reads as
an ordered set of signed deltas rather than a running balance. The bridge framing is carried by the
section's prose and the sequence, not by a cumulative bar. Use it where the *order* of the deltas is
the argument; use `divHbars` where only their direction and size are.

`stackedArea` and `line` also assume the `x` column is **ordered**. The profile cannot tell an
ordered category from an unordered one, so no validator will stop you drawing a stacked area across
five team names — and the continuity it implies would be a fiction. That one is yours to check.

## When two lenses both fit

The mapping is a set of entry conditions, and more than one is usually open. These are the
questions that close them — each one asks what the reader is being told, not which chart is nicer.

| Both fit | Take | Because |
|---|---|---|
| `hbars` / `lollipop` | `hbars` by default | Same roles, same ranking. `lollipop` is for a long sparse list where bar ink would swamp the page, and it drags a 20-row cap onto every other chart in the report. `hbars` has no cap. |
| `hbars` / `donut` | `hbars` unless the parts *are* the whole | On a donut, colour carries identity and runs out after three (`CHART-013`); on `hbars`, length carries it and never does. If the question is "which is biggest", it was never a donut. |
| `columns` / `stackedArea` | whichever names the subject | `columns` when the reader compares the series against each other; `stackedArea` when the **total** is the subject and the parts explain it. |
| `columns` / `panels` | by unit | `columns` requires one shared axis, so the series must share a unit. `panels` exists for the case where they do not. Two units on one axis is the dual-axis lie in a different costume. |
| `waterfall` / `divHbars` | by whether order is the argument | `waterfall` when the *sequence* of deltas is the finding; `divHbars` when only direction and size are. |
| `slope` / `divHbars` | by whether anything crosses | `slope` when *crossing* is the finding — who overtook whom. A slope chart with no crossing lines is a ranking drawn the hard way; use `divHbars` and show the change. |
| `bubbles` / `panels` | by whether both axes reach zero | The Relationship lens asserts that two measures move together, and `VIZ.bubbles` scales from the origin. Where the ranges do not approach zero, `panels` shows the same two measures without asserting a shape. |
| `boxplot` / `divColumns` | by how many distributions | `divColumns` shows one distribution's actual values; `boxplot` compares many distributions' summaries. Below about five values per group the box over-claims. |
| `heatmap` / `panels` | by whether values are read or scanned | `heatmap` when the grid *position* is the finding; `panels` when the reader needs to read a value off an axis. Intensity is not legible to three significant figures. |
| `concentration` / `hbars` | by the sentence | `hbars` ranks. `concentration` answers "how much of the total comes from how few", which is a different sentence — and usually the better one. |
| `interval` / `hbars` | `interval` the moment a difference is the claim | An interval is not decoration on a comparison; it is what separates a finding from a number. See [`uncertainty.md`](uncertainty.md). |

## What the lens costs downstream

Choosing the lens fixes more than the chart: the factory decides the motion band, because what a
chart's progress value scales differs per factory. `assets/validate-plan.py` warns outside the band
(`MOTION-FIT-001` on the curve, `MOTION-FIT-002` on the duration), so the lens decision is worth
making with the consequence in view.

- **Reveals** — `line`, `slope`, `concentration` — draw part of a finished mark set, and nothing
  on screen is ever wrong. Steady curve, 600–800 ms. `waterfall` is a sequenced reveal that has to
  divide the run among its steps: 600–900 ms.
- **Value-scaled marks** — `columns`, `divColumns`, `hbars`, `divHbars`, `lollipop`, `panels`,
  `stackedArea`, `donut`, `heatmap` — read a number smaller than the datum until they land, so they
  need a curve that arrives early: 400–600 ms.
- **Spread** — `boxplot`, `interval` — grows outward from a value already drawn in place, so every
  running frame shows a **narrower** interval than the data supports. That is an overclaim rather
  than a delay, and it takes the shortest run in the table: 300–500 ms.
- **`bubbles`** scales the radius, so area grows with the square of progress and the mark reads far
  smaller than its value for most of the run: 700–900 ms.

[`motion-features.md`](motion-features.md) is the authority and carries the easings per factory.
On the portable path nothing may declare past 900 ms — the shell's `anim()` clamps silently and
`MOTION-PORTABLE-CEILING-001` is an error, not a warning.

## Judgement rules

**Time granularity.** Fewer than 6 periods is not a trend — demote it to a bar comparison.
Past 25 periods, default the view to the most recent 12–13 and put the full range behind a filter.

**Entity keys.** Before building a cohort or a bridge, compare `COUNT(DISTINCT key)` with `COUNT(*)`.
A large gap means the key is masked, recycled, or needs to be a composite.
**A bridge built on the wrong key tells a plausible lie in silence.**

**Cardinality.**
- ≤ 8 → show everything
- 9–40 → top N plus a folded "other", or a size filter
- \> 40 → switch to a scatter (one point per entity) or a top/bottom ranking. Forty bars is a table.

**Scatters start at zero here.** `VIZ.bubbles` scales both axes from the origin — there is no
domain option — so the Relationship lens only reads when the two measures approach zero within the
data. Two series that live between, say, 1,000 and 2,600 land in one corner of an empty plot and
their marks overlap into a smear. Check the ranges against zero before selecting the lens; when
they do not reach it, the honest move is to drop the lens, say so in the plan, and let the two
measures share a table twin instead of a chart that asserts a shape it cannot draw.

**When the measure is a ratio.** Always state the denominator in the tooltip and the methodology.
A large ratio from a small denominator needs a minimum-size filter, switched **on** by default.
If the report goes on to *compare* two ratios, that is a claim, not arithmetic — give each one an
interval ([`uncertainty.md`](uncertainty.md)) or describe the magnitudes and stop.

**Concentration is a finding, not a footnote.** If the top few entities carry most of the total,
that is usually the most useful sentence in the report and it deserves the chart rather than a
parenthesis. `VIZ.concentration` draws it; the top-k share is the statistic. Do not compute Gini.

**A difference needs three things on the page:** the denominator, an interval, and the reference
it is measured from. Missing any one of them, state the magnitude and stop.
See [`uncertainty.md`](uncertainty.md) — it is read at step 1, with this file.

**Stock vs flow.** A balance at a point in time and a count of events during a period cannot be
added or subtracted. If you have both, make the discrepancy its own section — that is usually
where the report actually is.

**Parts of a whole.** Only when the parts genuinely sum to the whole, there are 2–5 of them, and
none is negative. Otherwise it is a ranking, not a composition.

**Stacked bands.** In a stacked area only the bottom band and the total sit on a flat baseline;
every band above rides on the ones below, so its *shape* is readable but its *size* is not
comparable by eye. Use it when the total is the subject. If a middle part is the subject, give it
its own axis with `VIZ.panels`.

**Box plots vs histograms.** A histogram answers "what does this one distribution look like".
A box plot answers "how do these twenty distributions differ". Below about five values per group
a box plot is over-claiming — show the points instead.

## When nothing fits

A data shape with no honest lens is a result, not a failure. It has four exits, in this order —
the same ladder [`SKILL.md`](../SKILL.md) applies to a failed gate, taken before the build rather
than after it.

1. **Aggregate first.** Most cap and cardinality problems are really grain problems. Aggregate the
   source, then profile the aggregate — the profile describes the file it was handed, so this has
   to happen upstream of profiling, not inside the plan.
2. **Rewrite the claim down to the evidence.** A comparison with no denominator becomes a
   magnitude. A trend with four periods becomes a comparison. The section survives; the claim
   shrinks to what the data carries.
3. **Keep the table twin and drop the chart.** The numbers are still worth printing. What the data
   will not support is the shape a chart asserts about them.
4. **Drop the section and disclose it.** The limitation is content. A report that names what its
   data could not answer is worth more than one that quietly answers it anyway.

What none of these is: choosing the nearest chart and letting a caveat in the card note carry the
difference. A caveat does not undraw a mark.

## What one section contains

```
title           what you found — a claim, not a question
lede            2–3 sentences. why this lens
toolbar         (optional) one row of filters governing this group
card
  h3 + help chip
  card-note     basis, unit, caveat. Head off the misreading here
  legend        required once there are 2+ series
  canvas        the chart
  tablewrap     the table twin (may start collapsed)
```

## Writing an insight

- The title is a **claim**. "Results by region" ✗ / "The regions split in opposite directions" ✓
- Put a number in the first sentence and wrap it in `<span class="fig">`.
- Ask what would falsify it. If next period's data could not prove it wrong, it is a summary, not an insight.
- If a change is explained by seasonality, a policy change, or a collection change, **say that**.
  A spike with no cause is usually a data event, not a real one.
