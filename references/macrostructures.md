# Macrostructures — the index

**Pick the report's shape first.** Before the charts, before the theme.
One macrostructure fixes the section rhythm, the canvas placement, the scroll grammar and the
reading order all at once. It is faster than choosing six axes separately, and it is what stops
every report coming out the same.

**Pick one name from this index, then read that one file.** Never read them all.

| # | Name | One line | Data it requires | File |
|---|---|---|---|---|
| 01 | **Briefing** | conclusion first: hero figure + insight cards, then the evidence | anything | [01-briefing.md](macrostructures/01-briefing.md) |
| 02 | **Ledger** | a metric index table is the first screen; rows expand in place | 8+ metrics | [02-ledger.md](macrostructures/02-ledger.md) |
| 03 | **Scrollytelling** | one canvas is pinned; scrolling changes the picture | one subject changing in stages | [03-scrolly.md](macrostructures/03-scrolly.md) |
| 04 | **Workbench** | filter rail left, work surface right. A tool, not a read | 3+ dimensions | [04-workbench.md](macrostructures/04-workbench.md) |
| 05 | **Broadsheet** | a newspaper front page: columns, one large lead chart | analysis with real prose | [05-broadsheet.md](macrostructures/05-broadsheet.md) |
| 06 | **Poster / Almanac** | everything on one sheet: big figure + dense small-multiple grid | 12+ series of the same shape | [06-poster.md](macrostructures/06-poster.md) |
| 07 | **Deck** | one claim per viewport, snap scrolling | 5–8 claims | [07-deck.md](macrostructures/07-deck.md) |
| 08 | **Bridge** | the waterfall is the protagonist; everything else is a footnote | entity key + two points in time | [08-bridge.md](macrostructures/08-bridge.md) |
| 09 | **Comparison spread** | left/right symmetry: two periods or two groups face each other | two comparable sets | [09-spread.md](macrostructures/09-spread.md) |
| 10 | **Field notes** | marginalia beside the body: observations and caveats side by side | data with outliers and qualitative notes | [10-fieldnotes.md](macrostructures/10-fieldnotes.md) |

## How to choose

1. **Filter on the data requirement first.** Drop any macro whose requirement you cannot meet.
   Picking 08 without bridge data means building a fake waterfall.
2. **Ask what the reader came to do.**
   - only needs the conclusion → 01 · 07
   - is looking for their own number → 02 · 04
   - has to be persuaded → 03 · 05 · 08
   - needs to scan the whole → 06 · 09
   - does not know the answer yet → 04 · 10
3. **Apply rotation.** Never the same macro as the previous report. If it is in the last three
   entries of `.canvas-report/log.json`, drop it.
4. **Declare it in one line**, before writing code.

> *"Macro: 05 Broadsheet. Theme: newsprint. Masthead: M3. Differs from the last (01 Briefing · almanac · M2) on all three."*

## Deviating

A macrostructure is a starting point, not a cage. But **when you deviate, write the reason in one
sentence.** "The data demands this shape" is a reason. "A card grid was easier" is not.
Drifting back to 01 Briefing without a reason is the default failure this skill exists to prevent.

## Never

- **Two macros on one page.** A workbench rail plus deck snapping breaks both.
- **Imitating a shape you lack the data for.** Three steps is not a scrollytelling piece; it is
  an empty scroll.
- **Starting without choosing.** If you do not choose, you will always produce 01 Briefing.
