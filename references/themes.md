# Themes — twenty-six of them, three axes, and a subject to fit before you rotate

The data decides what a report *says*. **The theme decides what it looks like**, and the first job
of a look is to belong to the subject: a payroll report and a wildfire report should not arrive
wearing the same face, and neither should two payroll reports in a row. Fit comes first, rotation
second.

Token values live in [`../assets/themes.css`](../assets/themes.css); the catalogue that selection
actually reads is [`themes.json`](themes.json). Apply a theme with the script, which cannot damage
the `[T]` marks:

```bash
python3 assets/apply-theme.py <report.html> <theme>
python3 assets/apply-theme.py --list
```

## Choosing: three passes, in this order

`assets/select-candidates.py` runs all three and writes the result into the candidate artifact. The
plan then records the decision in `theme_rationale`, and `assets/validate-plan.py` checks that
record against the artifact — a plan cannot claim a subject match the profile does not evidence.

**1. Compatibility.** Discard themes incompatible with the profile, the accessibility contract, the
macrostructure, or an explicit requirement. `requirements.native_mode` (`light`/`dark`) filters
here; nothing else in the catalogue is conditionally unavailable.

**2. Subject fit.** Score every remaining theme against what the dataset is *about*. The signals are
the profiled column names, the source file's name, and the stated requirements — lowercased and
split into word tokens. A theme's `subjects` keyword matches when a signal token equals it or begins
with it, so `enrol` catches `enrolment`. Five matches is as fitted as a theme gets:

```text
fit_score = max(baseline, min(1, matched_keywords / 5))
```

The `baseline` in `themes.json` is what a subject-neutral theme scores when the columns say nothing
about a domain — `almanac`, `grid`, `specimen` and `lumen` stay selectable for data that is simply
numbers. A theme with `baseline: 0` and no match is not forbidden; it is just last.

**3. Rotation.** Among the fitted survivors, the chosen theme must sit at **distance ≥ 2** from the
previous theme across paper band, display class, and accent hue. Ranking is
`compatible → not rotation-excluded → fit_score → rotation_distance`, so **fit outranks distance**:
a report about payroll should look like payroll first and differ from the last report second.

An explicit user requirement outranks rotation only after compatibility is proven, and a user may
request a compatible nearer theme; record the override and its evidence in `plan.json`. An
incompatible request receives a Rule-ID diagnostic and an alternative.

### What the plan records

```json
"theme_rationale": {
  "subject": "monthly support-desk intake and backlog",
  "signals": ["backlog", "handling", "intake", "resolved", "ticket"],
  "fit_score": 1.0,
  "rotation_distance": 3,
  "runner_up": "cobalt",
  "why_not_runner_up": "cobalt reads as service internals; the report is about queue health for a non-engineering reader."
}
```

`subject` and `signals` are the report's own words and the artifact's own tokens. `fit_score` and
`rotation_distance` are **copied** from the candidate artifact, not estimated — `THEME-FIT-003`
fires on a mismatch, `THEME-FIT-004` on a signal the artifact never produced, and `THEME-FIT-001`
warns when a theme matching nothing was chosen over a compatible theme that scored 0.4 or better.
The rule to cite in `rule_decisions` is `THEME-SELECTION-001`, and it is required.

## Catalogue

The ten original faces. They carry no domain of their own beyond what is listed, and four of them
hold a baseline so that subject-less data still has somewhere to land.

| Theme | Character | Paper band | Display class | Accent hue | Data it suits |
|---|---|---|---|---|---|
| `almanac` | statistical yearbook; neutral and quiet | light 94 | humanist-sans | cool | official statistics, metric collections |
| `specimen` | editorial workshop; the sentences lead | light 96 warm | high-contrast-serif | warm | narrative analysis, research notes |
| `newsprint` | press; serif body text | light 92 cream | roman-serif | warm | event briefings, multi-column argument |
| `cobalt` | instrumentation, engineering | light 98.5 cool | techno-grotesk | cool | logs, performance, experiments |
| `grid` | swiss data sheet | light 99 | neo-grotesk | warm | dense metric grids, many small multiples |
| `terminal` | operations console | **dark 11** | mono | green | monitoring, anomalies, many time series |
| `lumen` | late-night studio | **dark 13** | classical-serif | warm | executive summaries, presentation decks |
| `garden` | environment, fieldwork | light 95.5 oat | roman-serif | green | environmental, agricultural, field surveys |
| `carnival` | consumer, culture | light 92 pink | display-heavy | warm | consumer trends, culture and leisure |
| `riso` | risograph zine | light 91 pink | reverse-pair | cool | a small dataset making one loud claim |

The sixteen subject-fitted faces. Each exists because a common kind of dataset deserves a face that
belongs to it; each is generated, not hand-picked, by `assets/make-themes.py`.

| Theme | Character | Paper band | Display class | Accent hue | Data it suits |
|---|---|---|---|---|---|
| `abacus` | finance ledgerbook; mono figures, serif prose | light 96 bone | ledger-mono | teal | revenue, cost, billing, anything that has to foot |
| `clinic` | clinical record; cool white and unhurried | light 98 | clinical-sans | cyan | patient, trial, and care-pathway data |
| `atlas` | survey sheet; sand paper, engraved labels | light 95 sand | cartographic-serif | slate | place, route, and movement data |
| `voltage` | industrial telemetry | **dark 14** | industrial-sans | amber | energy, utility, plant-floor measurement |
| `campus` | academic press; ivory, long measure | light 97 ivory | academic-serif | violet | students, courses, assessment |
| `pitch` | scoreboard; condensed caps, hard shadow | light 93 cool | condensed-grotesk | lime | competition results, season standings |
| `bazaar` | storefront; rounded and warm | light 97 blush | rounded-sans | magenta | retail and e-commerce transactions |
| `blueprint` | drafting table; square corners, drawn rules | light 96 cool | drafting-mono | indigo | built environment, assets, capacity |
| `sentinel` | incident desk; near-black, crimson stripe | **dark 12** | stencil-grotesk | crimson | security, abuse, incident response |
| `assay` | laboratory notebook; precise and footnoted | light 98 | scientific-serif | violet | instrument readings, repeated measurement |
| `civic` | public record; slab headings on warm grey | light 94 | civic-slab | indigo | census, public services, budgets |
| `signal` | growth desk; geometric caps on cool black | **dark 14** | geometric-sans | magenta | acquisition, funnel, retention |
| `roster` | people file; soft humanist on oat | light 95 oat | soft-humanist | teal | workforce and personnel data |
| `desk` | service desk; cool sheet, rust stripe | light 96 cool | record-sans | rust | support queues, SLA reporting, case handling |
| `tide` | observation log; blue-grey, long serif measure | light 95 cool | transitional-serif | cyan | climate, weather, environmental series |
| `flux` | network operations; wide mono on teal-black | **dark 13** | wide-mono | lime | network, telecom, infrastructure throughput |

Six themes are **dark-native**: `terminal`, `lumen`, `voltage`, `sentinel`, `signal`, `flux`. Their
light drops exist for print and for a projector, not as a default. The other twenty are
light-native. All twenty-six ship both drops, and the reader's toggle is always available.

## Adding a theme

Four files move together, and the check refuses to let them drift apart:

1. a design row in `assets/make-themes.py`, then `python3 assets/make-themes.py --write`;
2. a catalogue row in `references/themes.json` — axes, `character`, `suits`, `subjects`, `baseline`;
3. a row in the table above;
4. `python3 assets/check-themes.py`, which proves the contrast contract for every drop and fails on
   a theme that exists in only one of the two machine-readable files
   (`THEME-CATALOGUE-001`/`-002`).

## The contrast contract

Every block in `themes.css` is generated to satisfy this, measured against that block's own `--bg`.
**Editing a value by hand breaks it.** `assets/check-themes.py` is what proves it, not the comment
at the top of the file.

| Target | Contrast against paper |
|---|---|
| `text-primary` | ≥ 7:1 |
| `text-secondary` | ≥ 7:1 |
| `text-muted` | ≥ 4.5:1 |
| `accent-ink` | ≥ 4.5:1 |
| `s1 s2 s3 pos neg` | ≥ 3:1 (the non-text floor) |

Series are separated by at least 55° of OKLCH hue **or** a greyscale luminance ratio of 1.18, so they
survive both colour-vision deficiency and monochrome printing; `pos` and `neg` are separated by hue
alone, because direction has to read on a diverging scale. The generator solves each token's
lightness against the darkest and lightest ground a card can present — `--bg`, `--surface-1` and
`--surface-2` — so text stays legible inside a card, not only on the page.

## Series colours are used by role, never by taste

The tokens already satisfy the colour rules (if the `dataviz` skill is available, it is the higher
authority). **Do not re-pick them. Use them by role.**

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

## Type

Each theme carries exactly three type roles: `--font-display`, `--font-body`, `--font-label`. There
is no fourth font.

**No font files are fetched.** Each stack names Latin faces first and then falls through to
`system-ui` / `ui-serif` / `ui-monospace`, so the *class* (serif / grotesk / mono) survives even when
the named face is absent, and the operating system resolves any script the named faces do not cover.
External-font requests are not an exception to the offline output contract.

To pin a face for a specific script, insert it immediately before `system-ui` in that theme's stack.
Otherwise expect that **in a non-Latin report the theme's difference is carried by spacing, scale,
rules and colour, not by the display face.** Do not lean on typeface alone to tell two reports
apart — that is what the macrostructure is for.

Rotation history and the decision live in run artifacts, not in authoritative HTML comments. Optional
report notes may describe the choice, but `references/rules.json`, `references/index.json`, and
validator results are the source of truth.
