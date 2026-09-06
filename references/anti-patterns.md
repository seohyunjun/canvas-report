# Anti-patterns — the named failures

Two lineages. The first half is **how a data report lies**; the second is **how a screen gives
away that it was generated rather than made.** This skill exists to prevent both.

Consult this file *while generating*. The scorecard is [`slop-test.md`](slop-test.md), which you
read only when the report is finished.

---

## A. How a data report lies

**Dual axes.** Two metrics in different units overlaid on one chart. Nudge either scale and you
can manufacture whatever correlation you wanted. → Separate charts, or `VIZ.panels` small multiples.

**An axis range back-computed from the ticks.** Using the min/max of `ticks()` as the axis range
puts data outside the plot. → Fix the range from the data, then find ticks inside it.

**A bar chart not starting at zero.** A line may do this; a bar may not, because its length *is*
the value. A truncated bar makes a 2× difference look like 10×. → Bars always start at zero;
use a different chart when that scale is not useful.

**Small multiples with a per-cell axis.** The grid exists to compare; if each cell scales itself,
the comparison is an illusion. → A shared axis. If they cannot share one, do not build a grid.

**Invented numbers.** Plausibly filling in a metric the user never gave you. Writing
"+47% year on year" or "2.3× the industry average" without data invalidates the whole report.
→ A `—` and a "to confirm" label, or drop that lens.

**Sentinel leakage.** Placeholders — `unclassified`, `N/A`, `-1`, `9999` — excluded from the
aggregate reappear in ranking tables and tooltips. → Filter once more at display time.

**An identifier trusted without checking.** Cohorts and bridges built on masked or recycled keys
fail silently. → Count `COUNT(DISTINCT key)` against `COUNT(*)` and put the residual duplicate
count in the methodology.

**Collection lag read as a trend.** The newest period is always low because of reporting delay
and gets revised up. That is not a decline. → Annotate the last period, or exclude it and say so.

**Adding a stock to a flow.** A balance at a point in time and a count of events over a period
cannot be added or subtracted. → If you have both, make the discrepancy a section. It is usually
the most interesting thing in the data.

**Compact rounding collisions.** If `174,866` and `165,104` both render as "0.2M" the table lies.
→ `Intl.NumberFormat(lang,{notation:'compact',maximumFractionDigits:1})`.

**Flattening sub-0.1% change.** `-0.035%` shown as `0.0%` turns a decline into a plateau.
→ Two decimals below an absolute value of 0.1.

**A large rate from a small denominator.** Ranking "66.7% growth" from n=3 at the top.
→ Provide a minimum-size filter and switch it on by default.

**Information that exists only in a tooltip.** A tooltip supplements; it is not the only route.
Print, screenshots and keyboard users lose it. → Every chart owes a table twin. Definitions also
go in the methodology.

**A report with no limits section.** No dataset is perfect. A missing limits section means you
either hid what you found or never looked.

**Dropping rows silently.** A `null` or `NaN` reaching a coordinate deletes a mark with no error.
→ The shell's factories filter at the door and print `N rows omitted`. Never suppress that.

**Hand-editing a generated report.** A plausible HTML patch can disagree with the profile, plan,
or validator result and has no reproducible source. → The Agent writes only `plan.json`; change
the plan/spec and rebuild builder-owned HTML.

**Treating a quotation as validation.** A copied reference fragment can be irrelevant, stale, or
misapplied. → Rule IDs from `references/rules.json` and `references/index.json` in
profile/spec/results are authoritative. Quotations
are optional explanatory notes, never gate evidence.

**A fixed insight quota.** Padding a report to four cards promotes weak observations to claims.
→ Use an evidence-driven set, typically 2–6 falsifiable insights; drop unsupported ones.

---

## B. How a screen gives away that it was generated

**Always the same shape.** Hero → three cards → chart grid → footer. If the rhythm does not change
when the data does, the reader sees a template. → Choose the macrostructure first, and differently
from last time.

**A rainbow palette.** Six or more colours on nominal categories.
→ Top three plus `muted`, or small multiples.

**A value gradient on nominal categories.** Shading region names blue-to-dark invents an order
that does not exist. → Identity is `s1 s2 s3`; magnitude is one hue; direction is diverging.

**An improvised colour outside the tokens.** Writing `#3b82f6` straight onto the canvas. It will
not follow a theme change and it sits outside the contrast contract. → Pass token names. If the
colour you need does not exist, add it to the token block and then use it.

**Italic headings.** An `<em>` emphasis word in a title, or an italic display face. It is the most
reliable AI tell there is. → Carry emphasis with weight, colour or a drawn rule. Italic survives
only inside running body text.

**Re-drawn chrome.** Fake browser bars (URL pill plus traffic-light dots), fake phone frames,
fake terminal windows. → A real screenshot, or nothing.

**A number on every point.** Value labels belong on endpoints, extremes and the key series only.
Label them all and you have built a table, not a chart.

**Decorative animation.** Loops, staggered entrances, hover zoom, loading skeletons.
→ Delete it. Plan one report-level reading sequence, then declare only chart motion that improves
   acquisition, comparison, continuity, or a deliberate one-time reading aid.

**Tool soup.** D3, Plotly, GSAP, Motion, and anime.js are all named or bundled to
make the report sound sophisticated. → Select one chart/state source and at most one primary
motion source; every selection needs a reader benefit and an integration boundary.

**An unpinned runtime.** A CDN script or copied minified file enters the report without a version,
hash, or licence record. → Use a portable pattern through the shipped runtime, or a pinned local
vendor asset with attribution and a builder that inlines and validates it.

**An inflated title.** "Deep-Dive Insights Dashboard", "Our Future, Seen Through Data".
→ The title says what it is about; the subtitle says the as-of date and the scope. That is all.

**Auto-inverted dark mode.** Flipping light values destroys saturation and breaks contrast.
→ Use both drops from `themes.css`, declared in `@media` and `[data-theme]` alike.

**A grid child overflowing.** A table with `min-width:520px` inside a grid item pushes the whole
grid wide via `min-width:auto`. → `.grid > * { min-width:0 }` (already in the shell).

**A click target that wraps to two lines.** Buttons, anchors and tabs wrapping on mobile are hard
to hit and look careless. → Shorten the label or widen the container.

**A near-repeat theme without an explicit compatible override.** Choosing a theme fewer than two
axes away from the previous theme makes reports read as the same template. → Filter for
compatibility, then require rotation distance at least 2. A compatible explicit user override is
recorded in `plan.json`.

**Leaning on the display font to differentiate.** In scripts the named Latin faces do not cover,
every theme resolves to the same system font. → Difference must also come from spacing, scale,
rules, colour and the macrostructure.
