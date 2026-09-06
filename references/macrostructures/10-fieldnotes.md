# 10 · Field notes

**Marginalia runs beside the body.** The shape of a research notebook, putting observation and
caveat side by side. The only macro that can honestly handle data that is not clean, where the
outliers and exceptions are part of the story.

## Data requirement
Data that **actually has** qualitative notes: outliers, gaps, definitional changes.
Without them the margin is just white space → use 01 Briefing.

## Section rhythm

```
masthead        M5 (vertical label) or M1
observation 01… `.layout-margin` — left: marginalia / right: body and chart
  marginalia    source · row count · suspicion · "what we cannot see here"
  body          the observation, its chart, its table
open questions  the ones you could not answer. In this macro it is a required section
methodology
```

## Canvas placement
- Charts fit the body column (about 620px). Never spill into the margin column.
- **Mark outliers; do not delete them.** Label the extreme points on a `bubbles` chart directly
  and write in the margin what that point is.
- Break the line across a gap. A line drawn through missing data is invented data.

## Motion

Use the Motion Decision framework with `attention-guidance` only for a deliberate one-time entry
aid. Static is the default; do not use `data-transition`, `spatial-reordering`, or
`narrative-transition` in this macro.
- **Entry play only.** `R.playAll()` as everywhere else — watching a chart draw makes the axis
  register, and that is reading, not decoration. Nothing beyond it: no emphasis animation, no
  re-sort travel, no scroll transitions. A research notebook is read, not performed.
- Emphasise an outlier with a label and colour, not with animation.
- If an observation genuinely needs a still chart — a chart whose growth would read as a trend it
  does not have — declare it `static:true` and put the reason in the margin, where the other
  caveats already live.

## Do not
- **Fill the margin with decoration.** An observation with nothing to note gets no marginalia.
  Empty space beats a fake annotation.
- **Skip "open questions".** That removes the reason you chose this macro.
- **Hide the margin below 1040px.** It moves above the body (the CSS handles it) — it is worth
  as much as the body text.
