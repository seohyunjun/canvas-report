# 09 · Comparison spread

**Left/right symmetry.** Two periods, two cohorts, treatment and control, set face to face.
When comparison is the whole report, make comparison the layout itself.

## Data requirement
Two sets with the same schema. The observation unit, the period length and the inclusion rules
must **genuinely** match. If they do not, say so **on the first screen**, not in the methodology.

## Section rhythm

```
masthead      M1 — put both set names and sizes in the subtitle: "A (n=3,412) vs B (n=2,980)"
difference    centred. One diverging hbars answering "what moved apart the most"
the spread    `.grid.grid-2` — the same chart on the same axis, left and right
overlay       for the metrics that can honestly share one axis, as columns
methodology   the definitional differences between the two sets, always
```

## Canvas placement
- **The two sides share an axis.** Two canvases on different scales turn a comparison into an
  illusion. Pass an explicit `cfg.max` computed from both datasets.
- Fix left and right to `s1` / `s2` and never change what those mean anywhere in the report.
- The difference chart uses `pos`/`neg`. **Do not mix identity colours and direction colours in
  one chart.**

## Motion
- Both sides play together. Staggering invents a meaning ("the left one first") that is not there.
- Once, on entry, 600ms.

## Do not
- **Compare two sets of very different size by rate alone.** Show the absolute counts too, and
  give the smaller side a confidence interval or a minimum-size filter.
- **Stack left over right and call it done.** Below 820px they stack — label them explicitly as
  sharing an axis.
- **Write "statistically significant"** unless you ran a test. If you did not, write "a
  difference was observed".
