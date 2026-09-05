# 01 · Briefing

**The conclusion is entirely on the first screen.** Scrolling is how a reader checks the evidence,
not how they find the answer. A shape that still does its job for someone who leaves after
thirty seconds.

## Data requirement
None. Any data can carry it — **which is exactly what makes it dangerous.** Without deliberate
choice you will always land here. If the previous report was a briefing, pick something else.

## Section rhythm

```
masthead      M2 (large figure) or M1
summary       1 hero figure + 3-4 stat tiles + 4-6 insight cards
01 ...        one evidence section per insight, in the same order as the insights
methodology   basis · formulas · known limits
```

**Insight cards pair 1:1 with evidence sections.** Anchor from the card to the section
(`<a href="#s3">see the evidence</a>`). Delete anything unpaired — it is either a conclusion
with no support or a chart with no conclusion.

## Canvas placement
- One sparkline (`VIZ.spark`) beside the hero figure. No large chart in the summary.
- One or two charts per evidence section. Card grids stop at `grid-2`; a third column turns a
  briefing into a dashboard.

## Motion
- Hero figure: `R.countUp(el, v, 900)`.
- `.reveal` on each section; charts play once via `R.onView`.
- Stat-tile sparklines draw immediately, no animation — many small things moving at once is noise.

## Markup skeleton

```html
<header class="masthead masthead--figure"> … </header>
<main class="wrap" id="main">
  <section class="reveal">
    <div class="hero"> … hero figure + sparkline … </div>
    <div class="tiles"> … </div>
    <div class="insights"> … one #anchor per card … </div>
  </section>
  <section class="reveal" id="s1"> … </section>
</main>
```

## Do not
- **More than six insight cards.** Past six it is a list, not a summary.
- **Filters in the summary.** The summary must be fixed fact. Filters belong in evidence sections.
- **Six or more stat tiles.** That is a wall of numbers. If it overflows, switch to 02 Ledger.
