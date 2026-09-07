# Analysis lenses — from data shape to chart

The table that decides what you can honestly show, without knowing the domain.
**Build a lens only when the left column is true.**

## The mapping

| Lens | Data shape it needs | Question it answers | Shell factory |
|---|---|---|---|
| **Trend** | a time column + 1 measure, 6+ periods | is it rising or falling, is there seasonality | `VIZ.line` |
| **Composition over time** | time + 2–3 measures **in the same unit** | which of two forces is winning | `VIZ.columns` |
| **Composition of a total** | time + 2–4 parts summing to a meaningful total, non-negative | is the total growing, and which part carries it | `VIZ.stackedArea` |
| **Flow (bridge)** | an entity key + two points in time | where did the net change come from | `VIZ.waterfall` |
| **Distribution (one group)** | 1 measure, one row per entity | does the mean represent anything, where does it pile up | `VIZ.divColumns` |
| **Distribution (many groups)** | 1 measure + 1 dimension, ≥ 5 values per group | which groups are wide, skewed, or full of outliers | `VIZ.boxplot` |
| **Comparison (size)** | 1 dimension + 1 measure, cardinality ≤ 20 | who is big | `VIZ.hbars` |
| **Comparison (direction)** | the above + two periods | who grew and who shrank | `VIZ.divHbars` |
| **Comparison (multi-metric)** | 1 dimension + 2–3 measures in **different units** | is the biggest also the most numerous | `VIZ.panels` |
| **Relationship** | 2 measures per entity (+ size, + direction) | do the two move together | `VIZ.bubbles` |
| **Rank movement** | 1 measure at two points in time, ≤ 12 entities | who overtook whom | `VIZ.slope` |
| **Cross-tab intensity** | 2 dimensions + 1 non-negative measure, ≤ 100 cells | where is the grid hot | `VIZ.heatmap` |
| **Ranking (sparse)** | 1 dimension + 1 measure, ≤ 20 items | ranking where bars would be too heavy | `VIZ.lollipop` |
| **Parts of a whole** | 2–5 nominal parts, non-negative | is one part dominant | `VIZ.donut` |
| **Outliers** | an entity key + a sortable measure | who produced the result | `VIZ.hbars` + tabs |
| **Concentration** | 1 measure over 5+ entities, non-negative | how much of the total comes from how few | `VIZ.concentration` |
| **Uncertainty** | a point estimate + an interval per row | is this difference mine to claim | `VIZ.interval` |

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

**A row cap applies to the whole source, not to the chart.** The builder hands every source row to
every chart, so a five-slice `donut` means a five-row report. Aggregate before profiling, or choose
a form without a cap. Past a cap the runtime prints a message where the data should be, so the
validator refuses the plan first (`CHART-007`, `CHART-009`).

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
