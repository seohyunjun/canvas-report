# canvas-report

A skill that turns a dataset into **one self-contained HTML file a reader can explore** — every
chart drawn directly on `<canvas>`, no libraries fetched, no network requests at all.

It also refuses to make the same report twice.

![Ten themes, one runtime, identical data](docs/themes.png)

*The same demo data and the same runtime, under all ten themes.*

---

## Why

Most report generators are accurate and forgettable. They produce a hero figure, three cards, a
chart grid and a footer, forever, regardless of what the data is. The analysis may be sound, but
nobody reads the second one.

So this skill makes two decisions before it makes a chart:

1. **Pick the page shape from the data** — one of ten macrostructures, chosen because the data
   supports it, not because it was the default.
2. **Rotate the look** — theme and masthead must differ from the previous report on recorded axes.

The analytical discipline is not traded away for it. Every chart still owes the reader a table
twin, a help tooltip and a methodology section that says what the data cannot do.

## What you get

**A single `.html` file.** Data embedded as JSON, charts drawn on canvas, zero external requests.
It works offline, it survives being emailed, and it renders the same in five years.

- **15 chart factories** — `line` `columns` `divColumns` `hbars` `divHbars` `panels` `bubbles`
  `waterfall` `spark` `donut` `heatmap` `slope` `lollipop` `boxplot` `stackedArea`
- **10 themes** × day/night drops, generated to a contrast contract
- **10 macrostructures** — Briefing · Ledger · Scrollytelling · Workbench · Broadsheet ·
  Poster/Almanac · Deck · Bridge · Comparison spread · Field notes
- **Archetypes** for masthead, section head, insight, chart card, filter bar and methodology
- Hover tooltips, keyboard-and-touch help tooltips, sortable table twins, a light/dark toggle,
  and motion that always finishes

## Install

Copy the folder into your skills directory:

```bash
# personal, available in every project
git clone https://github.com/<you>/canvas-report ~/.claude/skills/canvas-report

# or per project
git clone https://github.com/<you>/canvas-report .claude/skills/canvas-report
```

Then just ask for a report. The skill triggers on phrasing like *"make me a report"*,
*"dashboard"*, *"visualise this analysis"*, *"interactive report"*, *"make it look different
this time"*.

## Try it without installing

`assets/report-shell.html` is a finished runtime, not a template. Open it and a demo runs.

```bash
# swap the theme and open it again
python3 assets/apply-theme.py assets/report-shell.html newsprint
python3 assets/apply-theme.py --list
```

## The rules it will not break

These are enforced, not suggested:

- **No dual axes.** Two metrics in different units never share a chart.
- **The axis range comes from the data**, never back-computed from the tick list.
- **Colour is used by role** — identity, magnitude, direction. No rainbows, no hex on the canvas.
- **Every chart owes a table twin.** A tooltip supplements; it is never the only route.
- **No invented numbers.** A metric you did not supply becomes `—`, or the section is dropped.
- **Nothing is dropped silently.** Rows that cannot be plotted are counted on the canvas.
- **The animation always ends**, even if the browser stops rendering. The final frame holds all
  the information.
- **The limits section is mandatory** — including what the data cannot see.

A finished report is scored against 42 gates in `references/slop-test.md` before it ships.
If anything in the data-honesty group trips, the rest of the score is void.

## Layout

```
SKILL.md                     the procedure: profile → insights → shape → theme → wire → verify
assets/
  report-shell.html          the runtime. Open it; a demo runs
  themes.css                 10 themes × day/night, hex-frozen from OKLCH
  apply-theme.py             swaps a theme without breaking the shell's marks
references/
  analysis-lenses.md         data shape → lens → chart
  macrostructures.md         index; read one file from macrostructures/
  themes.md                  catalogue, rotation rule, contrast contract
  components.md              masthead / section head / insight / card archetypes
  motion.md                  the three places movement is allowed
  tooltip-help.md            help copy and the accessibility contract
  anti-patterns.md           read while generating
  pitfalls.md                read before touching the runtime
  slop-test.md               read only when it is built
  external-tools.md          D3, Plotly, GSAP, Motion, anime.js, Lottie, Rive —
                             what to borrow from each and what to refuse
docs/themes.png              the contact sheet above
```

## Requirements

- A modern browser for the report itself (OKLCH is only used at authoring time; shipped tokens
  are hex, so the output is broadly compatible).
- Python 3 for `apply-theme.py` — standard library only.
- Headless Chrome if you want the verification step, which the skill treats as mandatory:

```bash
google-chrome --headless=new --force-prefers-reduced-motion \
  --window-size=1240,8000 --screenshot=out.png "file:///absolute/path.html"
```

`--force-prefers-reduced-motion` is required — without it you capture a mid-animation frame and
misdiagnose it as a broken chart.

## Localisation

The shell ships in English. Every string a reader sees lives in one `[L] CR_STRINGS` block —
translate that, not the code, and set `<html lang="…">` so `Intl` formats numbers and magnitudes
for the locale.

Theme font stacks name Latin faces and then fall through to `system-ui` / `ui-serif` /
`ui-monospace`, so any script the named faces do not cover is resolved by the operating system.
Note the consequence: in a non-Latin report the difference between themes is carried by spacing,
scale, rules and colour rather than by the typeface, which is exactly why the macrostructure
matters more than the theme.

## Attribution

Merged from two predecessors:

- **canvas-data-report** — the canvas runtime, the analysis lenses, table twins, help tooltips
  and the methodology discipline.
- **[Hallmark](https://www.usehallmark.com) (MIT)** — macrostructure-first selection, three-axis theme
  rotation, component archetypes and the anti-slop gates. The theme palettes here were derived
  from Hallmark's OKLCH token values and recomputed against a contrast contract.

Hallmark is MIT licensed; its copyright notice is reproduced in full in [`NOTICE`](NOTICE), which
must travel with any redistribution of this repository.

## Licence

MIT — see [`LICENSE`](LICENSE). Third-party notices are in [`NOTICE`](NOTICE).
