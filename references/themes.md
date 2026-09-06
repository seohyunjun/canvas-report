# Themes — ten of them, three axes, one rotation rule

The data decides what a report *says*. **The theme decides what it looks like.** Two reports
with the same data shape must not arrive wearing the same face. The rotation rule in this file
is the mechanism that prevents it.

Token values live in [`../assets/themes.css`](../assets/themes.css). Apply one with the script,
which cannot damage the `[T]` marks:

```bash
python3 assets/apply-theme.py <report.html> <theme>
python3 assets/apply-theme.py --list
```

## Catalogue

| Theme | Character | Paper band | Display class | Accent hue | Card | Data it suits |
|---|---|---|---|---|---|---|
| `almanac` | statistical yearbook; neutral and quiet | light 94 | humanist-sans | cool 252 indigo | raised · r12 | official statistics, metric collections |
| `specimen` | editorial workshop; the sentences lead | light 96 warm | high-contrast-serif | warm 38 orange | inset · r4 | narrative analysis, research notes |
| `newsprint` | press; serif body text | light 92 cream | roman-serif | warm 28 oxblood | none (rules) | event briefings, multi-column argument |
| `cobalt` | instrumentation, engineering | light 98.5 cool | techno-grotesk | cool 258 cobalt | raised · r10 | logs, performance, experiments |
| `grid` | swiss data sheet | light 99 | neo-grotesk | warm 28 signal red | none (hairline) | dense metric grids, many small multiples |
| `terminal` | operations console | **dark 11** | mono | green 138 phosphor | raised · r2 | monitoring, anomalies, many time series |
| `lumen` | late-night studio | **dark 13** | classical-serif | warm 50 brass | raised · r14 | executive summaries, presentation decks |
| `garden` | environment, fieldwork | light 95.5 oat | roman-serif | green 142 leaf | inset · r10 | environmental, agricultural, field surveys |
| `carnival` | consumer, culture | light 92 pink | display-heavy | warm 88 mustard | inset · r4 · hard shadow | consumer trends, culture and leisure |
| `riso` | risograph zine; sans display over serif body | light 91 pink | reverse-pair | cool 222 cyan | none · offset shadow | a small dataset making a loud claim |

`terminal` and `lumen` are **dark-native**. Their light drops exist for print and for a projector,
not as a default. The other eight are light-native. All ten ship both drops.

## Rotation and compatibility

Theme selection is a validated plan decision, not a stamp-reading exercise. First discard themes
incompatible with the profile, accessibility contract, macrostructure, or explicit requirements.
Then calculate distance from the previous compatible theme across paper band, display class, and
accent hue. The chosen theme must have **rotation distance at least 2**.

An explicit user requirement outranks rotation only after compatibility is proven. A user may
explicitly request a compatible nearer theme; record the override and its compatibility evidence
in `plan.json`. An incompatible request receives a structured Rule-ID diagnostic and an
alternative. Macrostructure and masthead also rotate where compatible alternatives exist.

Rotation history and the decision live in run artifacts, not authoritative HTML comments. Optional
report notes may describe the choice, but `references/rules.json`, `references/index.json`, and
validator results are the source of truth.

## Series colours are used by role, never by taste

The tokens already satisfy the colour rules (if the `dataviz` skill is available, it is the
higher authority). **Do not re-pick them. Use them by role.**

| Token | Role | Use for | Never use for |
|---|---|---|---|
| `s1 s2 s3` | identity (nominal categories) | comparing 2–3 series, legends | anything ordered, like size or rank |
| `pos` `neg` + `mid` | direction (diverging) | change, deviation, vs target | separating nominal categories |
| `mix(mid, s1, t)` | magnitude (sequential) | density, intensity gradients | anything with a direction |
| `accent` | emphasis fill | hero backgrounds, large areas | small text |
| `accent-ink` | emphasis text | section numbers, links, focus ring | large fills |

- Past three categories, **do not add a colour.** Fold to top 3 plus `muted`, or switch to small
  multiples. Inventing a fourth colour is where the rainbow starts.
- Pass **token names** to the canvas: `color:'s1'`. A hard-coded hex will not follow the toggle.
- Legend swatches built in HTML must be repainted from the `R.onTheme()` hook.

## The contrast contract

Every block in `themes.css` is generated to pass this. **Editing a value by hand breaks it.**

| Target | Contrast against paper |
|---|---|
| `text-primary` | ≥ 7:1 |
| `text-secondary` | ≥ 7:1 |
| `text-muted` | ≥ 4.5:1 |
| `accent-ink` | ≥ 4.5:1 |
| `s1 s2 s3 pos neg` | ≥ 3:1 (the non-text floor) |

Series are separated by at least 55° of hue **or** a greyscale luminance ratio of 1.18, so they
survive both colour-vision deficiency and monochrome printing. If you need a fourth series,
split the chart — do not add a colour.

## Type

Each theme carries exactly three type roles: `--font-display`, `--font-body`, `--font-label`.
There is no fourth font.

**No font files are fetched.** Each stack names Latin faces first and then falls through to
`system-ui` / `ui-serif` / `ui-monospace`, so the *class* (serif / grotesk / mono) survives even
when the named face is absent, and the operating system resolves any script the named faces do
not cover. External-font requests are not an exception to the offline output contract.

To pin a face for a specific script, insert it immediately before `system-ui` in that theme's
stack. Otherwise expect that **in a non-Latin report the theme's difference is carried by
spacing, scale, rules and colour, not by the display face.** Do not lean on typeface alone to
tell two reports apart — that is what the macrostructure is for.
