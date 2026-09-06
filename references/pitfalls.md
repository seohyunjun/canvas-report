# Mines already stepped on

Everything below is already fixed in the shell. **Read this list before adding a chart factory
or touching the runtime** — these are easy to reintroduce.

## Canvas

**Back-computing the axis range from the ticks.**
If `ticks(-mx*1.15, mx*1.15, 4)` returns `[-100000, 0, 100000]` and the data reaches `152,905`,
then setting `lo = min(ticks)` puts the bar outside the plot, drawn over the category labels.
→ **Fix the axis range from the data first, then find ticks inside that range.**

**A mid-animation frame becomes the final state.**
If progress lives in `c.t`, then whenever rAF stops — a background tab, a headless capture —
the half-drawn chart is what remains.
→ A `setTimeout(finish, dur+260)` safety timer plus a token to prevent double runs.

**Axis labels collide.**
An `i % step === 0` rule plus "always show the last one" puts the final two labels on top of
each other. → Filter by pixel gap (`minGap`) and drop the label that collides with the last.

**Small bars vanish.** Guarantee 2px minimum, and no more. The value label is the real information.

**A negative bar's value label leaves the plot.** Clamp the label's y to the plot bounds.

**A negative label overlaps the row name in diverging horizontal bars.**
Reserve label width (about 56px) out of the maximum bar length.

**Side-by-side panels: the left panel's max label touches the right panel's title.**
Widen the gutter and right-align the max label to its own panel.

**`measureText` measures with a different font than the one you draw with.**
The symptom is not an ellipsis — it is a **hard clip with no ellipsis**. `ell()` measures with a
narrower font, decides the label fits, and `txt()` then draws it wider, off the left edge.
Set `ctx.font` immediately before `ell()` measures, on every row.
This was live in `divHbars`, `panels`, `hbars` and `lollipop`; all four are fixed.
`lollipop` was missed in the first sweep and surfaced again in a real report, where SKU names
ran off the left edge of the plot with no ellipsis. Any new factory that draws a row label
inherits this trap.
`divHbars`'s label width was also a hard 64px cap that non-Latin and long labels overflowed;
it is now `cfg.labelW` (default 96) and `cfg.labelRatio` (default .28).

**Overlapping marks separated by a stroke.** A stroke is ink, not data.
→ A 2px ring in the surface colour, and 2px of space between adjacent fills.

**A missing value silently deletes a mark.** `null`, `NaN` or a string reaching a coordinate
produces no error at all — the mark just is not there, and nobody notices.
→ Every factory filters at the door with `usable(rows, [getters])`, and prints
`N rows omitted` on the canvas. Never drop rows quietly.

**A factory that cannot take negatives gets them anyway.** `columns`, `divColumns` and `bubbles`
assume non-negative magnitudes; a negative inverts the axis and produces nonsense.
→ They now draw an explicit message naming the factory to use instead.

**One data point cannot make a line.** `(v.length - 1)` divides by zero.
→ `spark` duplicates the single point; `line` never advances past `rows.length`.

**A re-sort key that is not stable.** `cfg.key` on `hbars` / `lollipop` decides which mark is
"the same thing" across a sort. Hand it an array index, or a string that reformats when the value
changes, and marks swap identities mid-flight — the animation then asserts that A became B.
→ Key on the entity, never on position or on anything derived from the value. If no stable
identity exists, omit `cfg.key`: growing from zero is the honest default.

**Animating a filter as if it were a sort.** With `cfg.key` set, `play()` after rows have been
added or removed slides the survivors into place, which implies a continuity the data does not
have. → `R.paintAll()` on a filter change (0ms, `motion.md`), `play()` only on a re-sort.

**Canvas height set in CSS.** The shell's `fit()` reads the `<canvas height="...">` **attribute**
and overwrites `style.height` itself. A height given in CSS is silently ignored.
→ Height always comes from the attribute. CSS owns width only (`width:100%`).

## Numbers

**Compact rounding collides.**
If `174,866` and `165,104` both render as "0.2M" the table is lying.
→ `Intl.NumberFormat(lang, {notation:'compact', maximumFractionDigits:1})`, which also handles
locale-specific magnitude words.

**Sub-0.1% changes flatten to zero.** `-0.035%` shown as `0.0%` turns a decline into a plateau.
→ Two decimals below an absolute value of 0.1.

**`tabular-nums` everywhere.** Hero figures and stat tiles want proportional digits; only table
columns want tabular.

## Data

**Sentinel values leak to the screen.** Placeholders like `unclassified`, `N/A`, `-1`, `9999`
get excluded from aggregates and then reappear in ranking tables and tooltips, which show
individual rows. → Filter the label once more, immediately before display.

**Trusting an identifier without checking.** Public datasets often mask or recycle identifiers,
so they are not unique. → Always count `COUNT(DISTINCT key)` against `COUNT(*)`, build a
composite key if needed, and **write the residual duplicate count into the methodology.**

**Code systems change underneath you.** Region and industry codes get merged, split and retired.
If a code appears in only one of two periods, suspect a reorganisation, and say so if you merged
anything. Series across a code change cannot simply be concatenated.

**Reading collection lag as a trend.** The newest period's "new registrations" are always low
because of reporting delay, and get revised up next release. That is not a decline. Annotate it,
or exclude the period and say that you did.

## Layout

**A grid child overflows on narrow screens.** Put a table with `min-width:520px` inside a grid
item and the item's `min-width:auto` pushes the whole grid wide. → `.grid > * { min-width: 0 }`.

**Misdiagnosing a headless screenshot as a layout bug.**
Headless Chrome clamps the viewport to a minimum of 500px. Passing `--window-size=390` crops a
500px layout into a 390px image. → Judge horizontal overflow by **measuring**
`document.documentElement.scrollWidth` against `innerWidth`, not by looking at a picture.

**Handling dark mode by inverting.** Never flip light values. Declare the values again in both
`@media (prefers-color-scheme: dark)` and `[data-theme]`, exactly as the themes do.

**Hard-coding a chart colour as hex.** The canvas will not follow a theme change.
→ Pass token names (`color:'s1'`) and resolve at draw time. Legends built in HTML get repainted
from the `onTheme()` hook.

**`VIZ.panels` was the one factory that ignored colour tokens.** It assigned
`cfg.panels[].color` straight to `fillStyle`, so `'s1'` was ignored and the canvas kept the
previous colour. Fixed — every factory now routes colour through `colorOf()`. Keep it that way.

## Runtime

**Deleting the `[T]` marks.** Pasting a theme by hand over `/* [T] */` or `/* [/T] */` means
`apply-theme.py` can never swap the theme again. → Keep the marks; replace only between them.
Better, use the script: `python3 assets/apply-theme.py <report.html> <theme>`.

**Writing tokens in `oklch()` and getting black charts.** The canvas is not a CSS colour parser.
`rgbOf()` reads most notations back through a 1×1 canvas, but shipped theme tokens stay hex.
A parse failure logs a warning — **if every chart is black or grey, suspect colour parsing first.**

**Editing theme token values by hand.** The values in `themes.css` are generated to satisfy the
contrast contract (body 7:1, muted text 4.5:1, chart marks 3:1) and series separation
(≥55° of hue or ≥1.18 greyscale ratio). Recompute; do not eyeball.

**Replacing the token object on theme change.** `readTokens()` used to assign a new `T`, so any
wiring holding a reference from `R.tokens()` kept painting the old colours after a toggle.
It now refreshes the same object in place. Still safest to call `R.tokens()` inside your paint
function rather than caching it.

**A cache keyed by arbitrary strings.** `_pcache[v]` on a plain object returns
`Object.prototype.constructor` for the colour name `"constructor"`. → `Object.create(null)`.

**Expecting a display font to cover every script.** Theme stacks name Latin faces, then fall
through to `system-ui` / `ui-serif` / `ui-monospace`, which the OS resolves for any script.
So in non-Latin reports the theme difference is carried by spacing, scale, rules and colour —
not by the display face. Do not rely on typeface alone to differentiate a theme; that is what
the macrostructure is for.

**Scrollytelling with a per-step axis.** If each step rescales, the pinned canvas is pointless.
→ Compute the axis range across **all** steps up front and fix it.

**A large canvas inside `.layout-broadsheet`.** A canvas in a newspaper column has about 300px.
The lead chart spans the columns with `.span-all`; the rest must fit one column.

**A scrolling table inside a snap section.** Nested scrolling fights the snap.
→ Move tables out of `.layout-deck` sections.

**`position:sticky` left on at narrow widths.** A pinned element eats half a phone screen.
→ The shell enables sticky for `.stick` and `.rail` only above 940px and 1000px. Match that.

**Calling `R.reveal()` before the DOM exists.** It must run after you build the sections.
→ The order is `wireHelp → wireToggles → reveal → paintAll`.

**A literal `<script ...>` tag inside a comment.** A regex like
`<script id="report-data".*?</script>` will match the comment first and eat the document head.
The shell's header comment therefore refers to `id="report-data"` without the angle brackets.
Keep it that way if you script edits to the file.
