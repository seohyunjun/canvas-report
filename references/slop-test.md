# Slop test — run this after, not during

**Do not read this while generating.** What you want during generation is
[`anti-patterns.md`](anti-patterns.md). This file is the scorecard for a finished report.
Anything that trips, fix and run again.

42 gates in five groups. **If anything in group D trips, the rest of the score is meaningless.**

---

## D · Data honesty (1–12) — stop immediately on failure

1. There is not a single dual axis.
2. Every bar chart starts at zero. (Lines may not; if so it is stated in the help tooltip.)
3. No axis range was back-computed from ticks — no mark sits outside its plot.
4. Every cell of every small-multiple grid shares one axis.
5. No number on screen was invented. Estimates are labelled as estimates.
6. Sentinel and placeholder values do not leak into ranking tables or tooltips.
7. If any analysis uses an entity key, `COUNT(DISTINCT)` was actually checked and the result is
   in the methodology.
8. Nowhere is a stock added to a flow.
9. If the newest period has collection lag, it is annotated.
10. Compact notation does not render two different values identically.
11. Changes below 0.1% are not flattened to `0.0%`.
12. The methodology carries all three of **data basis · formulas · known limits**, and the limits
    are not empty.

## E · Explorability (13–21)

13. Every chart has a table twin.
14. Every chart card has at least one help chip (`R.helpDot`).
15. Every computed metric carries a definition tooltip (`help-term`).
16. No information lives only in a tooltip — the same content is in a `card-note` or the methodology.
17. Help opens by hover, keyboard focus and touch tap alike (`R.wireHelp()` is called).
18. Filters sit directly above the group they govern, never inside a chart card.
19. A filter combination returning zero rows produces an empty-state message and a way back.
20. Value labels are selective — endpoints, extremes and the key series only.
21. Direction is never encoded by colour alone; a sign or arrow accompanies it.

## S · Structural variety (22–27)

22. A macrostructure was chosen and is named in the stamp.
23. It differs from the previous report (last three entries of `.canvas-report/log.json`).
24. The theme differs from the previous one on at least one of the three axes.
25. The masthead archetype differs from the previous one.
26. The chosen macro's data requirement is genuinely met (it is not a three-step scrollytelling piece).
27. No section was built on a lens the data does not support — no empty charts, no forced ones.

## V · Visual discipline (28–35)

28. No hex is written directly onto the canvas; every colour is passed as a token name.
29. Fewer than four colours on nominal categories. Past that it is folded or split.
30. Identity colours (`s1 s2 s3`) and direction colours (`pos neg`) are never mixed in one chart.
31. No italic headings.
32. Three type roles or fewer (`display` · `body` · `label`).
33. No fake browser bar, phone frame or terminal window is drawn.
34. The dark drop is declared in both `@media (prefers-color-scheme)` and `[data-theme]`.
35. The dark drop was actually rendered and looked at — it is not an inversion.

## M · Motion and finish (36–42)

36. The animation always ends — the final state draws even if rAF stops.
37. The final state alone carries all the information.
38. Under `prefers-reduced-motion` the animation is omitted, not slowed.
39. No loops, staggered entrances, hover zoom or loading skeletons.
40. Zero network requests. (If you deliberately added a web font, it is stated in the methodology.)
41. Rendered and inspected at 1240 / 768 / 500px, and horizontal overflow was **measured** with
    `scrollWidth` against `innerWidth`.
42. The stamp is at the top of the file and this report is recorded in `.canvas-report/log.json`.

---

## Self-critique — record it in the stamp

Score seven axes 1–5. **Anything below 3 gets fixed and re-scored.**

| Axis | The question |
|---|---|
| **P** perspective | does this report make a claim, or only display data |
| **H** hierarchy | is what matters most visible within three seconds |
| **E** execution | does it draw correctly — no collisions, clipping or overflow |
| **S** specificity | does it fit *this* data, or could it be pasted onto anything |
| **R** restraint | is anything left that could be deleted |
| **V** variety | does it have a different face from the previous report |
| **D** honesty | did you say what it cannot do |

```
canvas-report · macro: 05 Broadsheet · theme: newsprint · masthead: M3 · lenses: trend,comparison,outliers
critique: P4 H5 E4 S5 R4 V5 D5
```

## Browser check

```bash
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --force-prefers-reduced-motion \
  --virtual-time-budget=9000 --window-size=1240,8000 \
  --screenshot=out.png "file:///absolute/path.html"
```

- `--force-prefers-reduced-motion` is **required**. Without it you capture a mid-animation frame
  and misdiagnose it as "the chart is cut off".
- Shoot all three widths (1240 / 768 / 500). For the dark drop, temporarily put
  `data-theme="dark"` on `<html>` — do **not** use `--force-dark-mode`, which forcibly recolours
  the page.
- Headless Chrome clamps the viewport to a 500px minimum. Anything narrower crops the screenshot;
  that is not a layout bug.
- Judge horizontal overflow by measuring, never by looking.
- Watch for: colliding labels, marks outside the plot, clipped text, values off-axis, blank
  canvases, and **charts that are entirely black or grey** — that is a colour-parsing failure;
  check the tokens are hex.
