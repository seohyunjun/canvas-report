# Archetypes — the parts of a report

The macrostructure fixes the page shape; the archetypes fix the voice of the parts inside it.
Every class already exists in the shell's `[S]` structure layer. **Choose one and add the class.**

**The masthead is not optional.** Everything else can stay default, but two reports with the same
masthead have the same first impression — which is why it is one of the three things that rotate.

## Masthead M1-M6

| Code | Class | Shape | Suits macro | Watch out |
|---|---|---|---|---|
| **M1** label stack | (default) | eyebrow → title → subtitle → meta line | 03 · 07 · 09 · 10 | safe but colourless. Never twice in a row |
| **M2** large figure | `masthead--figure` + `.mast-fig` | left: title / right: the one number the report is about | 01 · 06 · 08 | there must be exactly **one** number. Two means M1 |
| **M3** nameplate | `masthead--broadsheet` | heavy rule above, centred title, double rule below | 05 · 06 | no invented publication furniture |
| **M4** index | `masthead--index` + `.mast-index` | left: title / right: section anchors with headline values | 02 · 04 | the anchors must actually work |
| **M5** vertical label | `masthead--rail` + `.mast-rail` | rotated label (period, source) beside the title | 03 · 10 | hidden below 640px — its content must exist elsewhere too |
| **M6** sticky shrink | `masthead--sticky` + `R.shrinkMasthead()` | collapses to a thin bar on scroll | 02 · 04 | the current condition must survive the collapse |

`masthead--rule` adds a heavy top rule to any of them (suits the press and brutal themes).

```js
R.shrinkMasthead(document.querySelector('.masthead'), 140);   // M6
```

## Section head S1-S5

| Code | Class | Shape |
|---|---|---|
| **S1** numbered stack | (default `.sec-head`) | number, title, lede, stacked |
| **S2** hanging number | `sec-head--hang` | number in the left margin, title and lede to the right |
| **S3** rule and label | `sec-head--rule` | heavy top rule, the number flows into the title |
| **S4** pinned | `sec-head--pinned` | the title sticks to the top through a long section |
| **S5** question | `sec-head--ask` | a large question as the title, the lede answers it |

Use **one** across the whole report. A different head per section destroys the table of contents.

## Insight I1-I5

| Code | Class | When |
|---|---|---|
| **I1** left-rule card | (default `.insight`) | 4–6 independent insights |
| **I2** ledger | `insights--ledger` on the container | more than six, or a label:sentence structure |
| **I3** quote | `insight--quote` | only two or three insights, each with long prose |
| **I4** figure first | `insight--stat` + `.fig-big` | the number *is* the claim |
| **I5** margin note | `insight--margin` | inside 10 Field notes' marginalia |

**Common rules.** The title is a claim ("Results by region" ✗ / "The regions split" ✓).
Put a number in the first sentence, wrapped in `<span class="fig">`.
If next period's data could not prove it wrong, it is a summary, not an insight.

## Chart card C1-C5

| Code | Class | Shape | When |
|---|---|---|---|
| **C1** framed | (default `.card`) | background + border + radius | default |
| **C2** full bleed | `card--bleed` | spans the page width | lead charts, waterfalls |
| **C3** hairline | `card--hairline` | no background, one heavy top rule | grid · newsprint · riso themes |
| **C4** inset | `card--inset` | a surface that sinks below the paper | side information, sidebars |
| **C5** split | `card--split` | left: chart / right: table | when the table must stay open beside the chart |

One chart per card. If you want two, use two cards.

A card with two or three series carries a legend between the note and the canvas, and the builder
emits it — a `.legend` of `.key.sq` swatches named by the column each series reads, repainted from
`R.onTheme()` so the swatch follows the theme toggle. `panels` is the exception: it prints each
metric's name above its own panel, so a second key would only repeat it. Do not hand-write a legend
into a plan; there is nowhere to put one, and the builder's is bound to the encodings.

## Filter bar F1-F4

| Code | Shape | Where |
|---|---|---|
| **F1** one-line toolbar | `.toolbar` | directly **above** the group it governs. Never inside a chart card |
| **F2** rail | `.rail` (04 Workbench) | pinned left |
| **F3** tabs | `.tabs` | switching the basis of one chart (top/bottom, absolute/rate) |
| **F4** segmented | `.segmented` | two or three mutually exclusive views |

Put a filter **beside what it changes**. Put what it does *not* change in the help tooltip.

## Methodology / footer Ft1-Ft4

| Code | Shape |
|---|---|
| **Ft1** three columns | `.method` — data basis / formulas / known limits (default, recommended) |
| **Ft2** ledger | definitions as a table. For more than ten derived metrics |
| **Ft3** letter | three or four paragraphs. Suits 05 Broadsheet and 10 Field notes |
| **Ft4** colophon | sections, sources, revision history. Suits 02 Ledger |

**Whichever you pick, three things are always present:** the data basis (source, row count,
observation unit — "1 row = one what", inclusion and exclusion), the formulas (every derived
metric, with estimates labelled as estimates), and the known limits (totals that do not
reconcile, weaknesses in the key, collection lag, code-system changes, and **what this data
cannot see**).

Limits do not cost you trust. They build it.
