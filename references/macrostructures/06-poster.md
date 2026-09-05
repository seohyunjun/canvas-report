# 06 · Poster / Almanac

**Everything on one sheet.** A large figure on top, a dense small-multiple grid below.
The point is not to read individual values — it is to make **the pattern legible at a glance.**

## Data requirement
12+ series of the same shape (17 regions, 24 sectors, 36 months …).
With eight or fewer the grid is sparse → use 09 Comparison spread.

## Section rhythm

```
masthead        M2 (large figure) or M3
whole           hero figure + a one-sentence summary. This much is "the poster's title"
.layout-poster  the small-multiple grid — name + mini chart + one value per cell
sort control    one row above the grid: by value / by change / alphabetical
how to read     three lines. This macro does not work without them
methodology
```

## Canvas placement
- One canvas per cell. **Height comes from the `<canvas height="104">` attribute** — the shell's
  `fit()` reads the attribute, not CSS. A height set in CSS is ignored. Use `VIZ.spark` or a very
  plain `columns`.
- **Every cell shares one y range.** Per-cell auto-scaling turns the grid into a lie. If the
  metrics cannot share an axis, this macro is the wrong choice.
- One value label per cell (the latest). One axis explanation for the whole grid, in place of a legend.
- Past 40 cells, use `VIZ.spark` only and attach hover at cell level.

## Motion
- **The grid is static.** Twenty-four things drawing at once is noise.
- Re-sorting rearranges immediately, no FLIP. Announce the new order with one `aria-live` line.

## Do not
- **A different axis per cell.** That removes the reason this macro exists.
- **Tooltips instead of a table.** A table covering the whole grid must sit below it.
- **Default to alphabetical.** Sort by value first so the pattern is visible before the labels are.
