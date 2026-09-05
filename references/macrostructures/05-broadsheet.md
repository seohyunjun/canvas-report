# 05 · Broadsheet

**A newspaper front page.** One lead chart spans the columns and the body text flows around it.
Use it when the analysis has prose to carry — when interpretation, not arithmetic, is the subject.

## Data requirement
Analysis with real text: three to six sentences per section. Without that, the columns are just
empty space → use 06 Poster.

## Section rhythm

```
masthead              M3 (nameplate) — heavy rule above, centred title, publication line
lead                  a `.span-all` lead chart plus the lead paragraph
.layout-broadsheet    2-3 columns; each with a subhead, prose and a small chart
sidebar               one whole column as `.card--inset` — definitions, caveats, side statistics
methodology           `.span-all`
```

## Canvas placement
- **The lead chart spans the columns** (`.span-all`). Everything else must fit one column
  (about 300px), so only `VIZ.spark`, a small `hbars` or a small `divColumns` belong there.
- In-column charts get `<canvas height="160">` or thereabouts, with three or four axis labels.
- `break-inside:avoid` is already in the CSS, but shrink a card that still breaks across a column.

## Motion
- Only the lead chart plays on entry (700ms). The small in-column charts are static.
- You borrowed the shape of a newspaper; keep the movement scarce. `.reveal` on the lead only.

## Do not
- **Keep columns on mobile.** Below 900px it is one column (the CSS handles it). Verify by screenshot.
- **Mechanically put one chart in every column.** Some columns must be pure prose or it stops
  reading like a newspaper.
- **Invent publication furniture.** No fake issue numbers or bylines. The as-of date and the
  source, nothing else.
