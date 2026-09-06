# Changelog

Versions are the `version:` field in `SKILL.md`. Dates are the day the work landed on `main`.

## 2.1.2 — 2026-09-06

Two more found by building a report, both the same shape: a value handed to the shell that the
shell quietly dropped.

- **`VIZ.divColumns` ignored `cfg.color`.** It is the diverging histogram, so it always coloured
  bars by distance from the midpoint. Used the way `analysis-lenses.md` prescribes it — for the
  distribution of a *positive* quantity — it painted red-to-blue across bins that have no
  direction, which is slop-test gate 33. It now takes a plain `cfg.color` as a single hue,
  `cfg.colorOf` for per-bar control, and diverges only when given neither.
- **`.tiles` was pinned to two columns on every screen above 520px**, so the `auto-fit` rule
  above it was dead everywhere but a phone and four stat tiles stacked two-by-two down the page.
  It now stays responsive: two up at 520px, more as the row allows.
- **01 Briefing's motion section** told stat-tile sparklines to draw without animation but
  predated `static:true`, so it read as an instruction to satisfy gate 46 by omission. It now
  names the declaration.

## 2.1.1 — 2026-09-06

Three defects found by building a report with 2.1.0.

- **`onTheme` never ran the hook it registered.** It only pushed onto the list that a theme
  toggle walks, so a legend built inside the hook stayed empty until the reader switched theme —
  and most never do. A two-series chart shipped with blank swatches. It now runs the hook once at
  registration as well; register it after the markup exists.
- **The shell's header comment contained a literal `<title>` tag.** A `<title>.*?</title>`
  substitution against the file matched the comment first and deleted the document head —
  `<html lang>`, both `<meta>` tags and the real title — leaving the page to render without its
  layout CSS applying. The comment now names the element without angle brackets, the way the
  `id="report-data"` line already did. `pitfalls.md` records both.
- **10 Field notes contradicted gate 46.** Its motion section said "almost none, `.reveal` only",
  which the new play-once-on-entry default cannot satisfy by omission. It now says entry play
  only — no emphasis animation, no re-sort travel — and points at `static:true` for a chart that
  genuinely must hold still.

## 2.1.0 — 2026-09-06

Everything below accumulated after 2.0.0 was tagged in the manifest and never released under a
version of its own. The runtime API is additive — no factory removed, no `cfg` key renamed — but
**the procedure gained required steps**, so a report written against 2.0.0's checklist will not
pass 2.1.0's gates.

### Motion is now required, not merely permitted

- `R.playAll(dur)` wires play-once-on-entry for every registered chart and is called by the
  default wiring block. Motion is **opt-out**: a chart that must not move declares
  `{static:true}` and the methodology says why.
- An audit found 9 of 27 charts wired across six shipped reports; one stamp quoted motion.md's
  "Play once on entry" verbatim and recorded the opposite decision. All six reports were fixed —
  66 charts, all animating and landing on their final state.
- `chart.play()` records `__played`, so a verifier can ask what actually ran rather than
  inferring it from the source.
- A fourth sanctioned place for motion: **a keyed re-sort**. `cfg.key` on `VIZ.hbars` and
  `VIZ.lollipop` makes marks travel to their new row instead of regrowing from zero — D3's object
  constancy without the runtime. Strictly a re-sort; never a filter.

### Verification tools

- `assets/check-motion.py` drives Chrome over the DevTools protocol on a **real clock** and
  reports, per chart, whether anything played it on entry and whether it landed on `t=1`.
  Both existing browser checks are structurally blind to motion:
  `--force-prefers-reduced-motion` omits the animation by design, and `--virtual-time-budget`
  freezes `requestAnimationFrame` so progress reads one constant value however long you sample.
- `assets/check-quotes.py` verifies every quote in a report's `read:` stamp still appears
  verbatim in the reference it cites — catching both an invented quote and a reference edited
  after the fact.

### Analysis

- `VIZ.concentration` — a cumulative share curve against an equality diagonal, reporting top-k
  share. Gini is deliberately not computed.
- `VIZ.interval` — point and band per row against a reference line; a band covering the reference
  is drawn muted, and direction is never carried by colour alone.
- `references/uncertainty.md`: a comparison ships with a denominator, an interval and a
  reference, or it states the magnitude and stops. Wilson for shares, seeded bootstrap at build
  time, MAD for spread. P-values, significance stars, intervals on a census, and concluding from
  overlap are all banned.
- `VIZ.boxplot` and `VIZ.stackedArea` joined the factory list; `cfg.max` on `hbars` and
  `divHbars` allows a shared axis across two charts.

### Process

- Four references (`analysis-lenses`, `pitfalls`, `motion`, `tooltip-help`) moved from
  conditional to **always-read**, and the form-scope half of `external-tools.md` moved to step 0.
- The `read:` stamp became a **quote block**: a verbatim fragment per bound file plus the
  decision it drove, machine-checkable with `grep -F`. Multi-step files carry one entry per
  bound section. Quoting a gate by its ordinal is forbidden — renumbering broke three shipped
  stamps once already.
- The slop test went 42 → 48 gates. Gates 46–48 (motion is wired; hero figures count up and
  scrollytelling scrolls; no `cfg.key` without a control that uses it) were **appended** to
  group M so nothing renumbers.

### Fixes

- `VIZ.lollipop` measured labels with the wrong font, producing a hard clip with no ellipsis, and
  hard-coded the value column width so long values drew past the right edge.
- `anim()` clamped progress only at the top. When rAF's clock preceded `performance.now()` the
  first frame gave a large negative `t` — `outCubic(-8.3)` is `-806` — which was invisible while
  `t` only scaled a bar and became visible the moment `cfg.key` let it drive a position.

### Reference material

- `references/external-tools.md` gained a D3.js entry in §A and a "what was actually adopted"
  record for the keyed join.
- `lab/motion-engines/`: one page per engine (GSAP, Motion, anime.js, Lottie, Rive, D3) with
  usage notes, vendored runtimes pinned and SHA256-verified, and licences flagged. Every page
  carries an explicit final-state paint, because none of the engines guarantees one.
- `README.md` documents how to use the skill, not only how to install it.

## 2.0.0 — 2026-09-05

Initial commit. `canvas-report` merges two lineages: the analytical disciplines of
`canvas-data-report` (data shape to lens, table twins, help tooltips, a methodology section) and
the structural variety of `hallmark` (rotating macrostructure, theme and masthead).
