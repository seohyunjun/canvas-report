# 08 · Bridge

**The waterfall is the protagonist and everything else is a footnote.** For when "why did the
total move by this much" is the only question. The second place canvas motion actually carries
information (the first is 03 Scrollytelling).

## Data requirement
An entity key plus two points in time. Opening → entering → leaving → continuing → closing must
**add up.** If it does not, that discrepancy *is* the report — do not force it shut; create a
residual item and show it.

**Verify before you build.**

```sql
SELECT COUNT(*) AS rows, COUNT(DISTINCT key) AS keys FROM …
```

A large gap means the key is masked or recycled.
**A bridge built on the wrong key tells a plausible lie.**

## Section rhythm

```
masthead      M2 — the large figure is the single net change (or the discrepancy)
bridge        one large waterfall inside `.card--bleed`, using the full page width
breakdown     the entering and leaving components split by dimension, two hbars
residual      if the totals do not reconcile, explain it here
distribution  the distribution of change size (divColumns) — what the mean hides
methodology   key definition · residual duplicate count · what each point in time means
```

## Canvas placement
- Waterfall 300–340px tall, four to seven steps. Past eight, fold to top 5 plus "other".
- Opening and closing labels are text at the top corners. Never draw them as bars — the scale
  collapses.
- The total bar uses `mid` (neutral). Giving it a direction colour makes it read as growth or decline.

## Motion
- Play the waterfall **once**. A looping animation is decoration.
- Put a "replay" button in the card's top-right (the shell demo has one).
- The finished state must contain all the information — confirm it in a headless capture.

## Do not
- **A stock and a flow in one waterfall.** A point-in-time balance and a period event count
  cannot be added.
- **Hiding the residual in "other".** The residual gets a name and an explanation in the methodology.
- **Letting motion carry the meaning.** The chart must read with the animation removed.
