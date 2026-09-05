# 04 · Workbench

**A tool to use, not a report to read.** A filter rail is pinned on the left and the right is a
work surface. It refuses to hand over a conclusion and says "recompute it on your own terms".

## Data requirement
Three or more dimensions (say period, region, category) and a measure whose meaning changes with
the combination. With one dimension the rail is empty — use 01 Briefing or 06 Poster.

## Section rhythm

```
masthead        M6 (sticky, shrinking) — the current condition must stay visible while scrolling
condition line  the current filter state as a sentence: "2024-2025 · metro · all sectors · 3,412 rows"
.layout-rail    left: .rail filters / right: 3-5 charts
methodology
```

## Canvas placement
- The work surface is `grid-2`. One filter governs **every** chart, so no filter lives inside a
  chart card.
- Every `cfg.rows()` is a function reading current filter state. On change: `R.paintAll()`.
- Some combination **will** return zero rows. **Design the empty state**: one line —
  "No rows match. The closest condition is …" — and a reset button.

## Motion
- On filter change, **redraw with no animation.** A control must respond instantly.
- Play once on entry. Never replay on a filter change.

## Markup skeleton

```html
<div class="layout-rail">
  <aside class="rail" aria-label="Filters">
    <div class="grp"><label for="f-period">Period</label><select id="f-period"> … </select></div>
    <div class="grp"><label>Minimum size</label><input type="range" id="f-min"></div>
    <button class="btn" id="f-reset">Reset</button>
  </aside>
  <div class="grid grid-2"> … chart cards … </div>
</div>
```

- Give the condition line `aria-live="polite"` so a screen reader hears the result of a change.
- Below 1000px the rail folds to the top (the CSS handles it). Do not make it sticky there.

## Do not
- **Leave unsaid what the filter does *not* change.** If a total tile ignores the filter, say so on it.
- **Require sharing without URL state.** Reflect filters in `location.hash` and a link carries the view.
- **Seven or more filters.** The cost of operating exceeds the insight. Keep the top three, fold the rest.
