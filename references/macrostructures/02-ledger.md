# 02 · Ledger

**The first screen is a metric index.** The reader came to find their own number, not to read
your conclusion. Clicking a row expands a chart in place. Depth comes from expansion, not scroll.

## Data requirement
8+ metrics, each with a value, a change and a mini trend. Five metrics is a set of tiles, not a
table — use 01 Briefing instead.

## Section rhythm

```
masthead      M4 (index) — metric count and as-of date beside the title
ledger        .ledger table · metric / value / change / sparkline / [expand]
expanded row  a .drill holding one chart + its table + help
below         one or two cross-cutting sections the ledger cannot hold
methodology
```

## Canvas placement
- A `VIZ.spark` per row (height 28). Past 40 rows, add sorting and search.
- **One** chart inside an expanded row. Two makes the table an accordion dashboard.
- Build lazily: create and paint the canvas the first time a row opens, then cache it.

## Motion
- No height animation on expand — the `.drill` appears and only its chart plays, 300ms.
- Row sparklines are static. Forty of them animating makes the table unreadable.

## Markup skeleton

```html
<table class="ledger">
  <thead><tr><th>Metric</th><th>Value</th><th>Change</th><th>Trend</th></tr></thead>
  <tbody>
    <tr aria-expanded="false" aria-controls="d-01" tabindex="0"> … </tr>
    <tr class="drill-row" hidden><td colspan="4"><div class="drill" id="d-01"> … </div></td></tr>
  </tbody>
</table>
```

Put `aria-expanded` on the row and make Enter/Space open it too.

## Do not
- **Start with every row expanded.** Then it is not an index, it is a long page. Default: all closed.
- **Encode change with colour alone.** Always print the sign as well.
- **Omit metric definitions.** Derived metrics get a `help-term` on the row name.
