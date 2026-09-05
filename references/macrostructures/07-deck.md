# 07 · Deck

**One claim per viewport.** Scrolling catches like turning a page.
For a report that replaces a presentation, or an analysis that only convinces in sequence.

## Data requirement
Five to eight claims, each provable by one chart. Three makes a short deck; twelve makes the
scroll a punishment.

## Section rhythm

```
masthead       M1 (spare) — in a deck the masthead is the first slide
.layout-deck
  section 1    the claim as an h2 + one chart + one line of evidence
  ...
  section n    "so what do we do" — prose only, no chart
methodology    outside the snap, as an ordinary section at the end
```

- Each section title is a **sentence**. Not "Distribution by region" but "Only the metro area grew".
- Put `n / total` in the top-right of each section. Snap scrolling takes away the sense of place.

## Canvas placement
- **One** chart per section. A second one makes it a dashboard again.
- `<canvas height="380">` or so. Fill the viewport and the sentence gets pushed out.

## Motion
- Play once on entry (600ms) via `R.onView`; never replay on re-entry.
- Under `prefers-reduced-motion` the CSS releases `scroll-snap-type` — snapping causes motion
  sickness.

## Do not
- **A scrolling table inside a snap section.** Move tables outside the deck.
- **Make it un-navigable by keyboard.** Give each section `tabindex="-1"` and prev/next links.
- **End on a chart.** A deck ends on a sentence.
