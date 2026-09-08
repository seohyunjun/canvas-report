# Changelog

## 3.6.0 — 2026-09-08

- Repin GSAP from 3.12.5 to **3.15.0**, and vendor the whole plugin set. Two files now sit in
  `lab/motion-engines/vendor/`: `gsap-3.15.0.min.js`, the 72 KB core a report inlines when a plan
  names `gsap` as a `vendored-runtime` motion engine, and `gsap-all-3.15.0.min.js`, 325 KB of core
  plus **all 24 plugin files**, which is the lab's. A document that runs one entry tween has no
  business shipping ScrollSmoother, so no report inlines the bundle.
- Rewrite `lab/motion-engines/docs/gsap.md` as the full catalogue from
  <https://gsap.com/docs/v3/Plugins>: every plugin, what it does, whether it is a **property**,
  **behaviour** or **ease** plugin — measured, not read off the site — and the verdict for this
  skill in the vocabulary `references/motion-features.md` uses. Nothing on that list is *absent*
  any more, which is the point: each plugin is now refused or held on what a report should do,
  where at 3.12.5 half the catalogue was simply not there to refuse.
- The pin had to move for that to be true. At 3.12.5 cdnjs carried **12** plugin files; the bonus
  set — SplitText, MorphSVG, DrawSVG, ScrollSmoother, Inertia, ScrambleText, Physics2D,
  PhysicsProps, GSDevTools, MotionPathHelper, CustomWiggle, CustomBounce — was Club GSAP and not
  publicly distributable. From **3.13.0** all 24 are on the CDN, alongside `all.min.js`.
- Record the licence change. Webflow's Standard "No Charge" GSAP License of 30 April 2025 made the
  library free for commercial use and freed the bonus plugins with it, and the 3.15.0 banner no
  longer mentions Club membership. `vendor/LICENSES.md` now carries the pinned file's own banner,
  says GSAP is still not MIT, and names the one restriction that survives — you may not put GSAP
  inside a no-code visual animation builder, nor reverse-engineer it to compete.
- **Loading a plugin file does not register it**, and `gsap.plugins` is the wrong place to look.
  `lab/motion-engines/probe-api.py` now measures the surface either side of
  `gsap.registerPlugin()`: 27 plugin globals arrive with the bundle, `gsap.plugins` holds 6 built-in
  property plugins before and 18 after, `gsap.core.globals()` goes 29 → 48, and
  `gsap.parseEase('rough')`, `'slow'` and `'expoScale(1,2)'` all fail until EasePack is registered.
  The core is scanned as text without being loaded, so the catalogue can show which names live only
  in the bundle: all of them.
- `lab/motion-engines/01-gsap.html` loads the bundle, mints its bar curve with `CustomEase` so a
  plugin genuinely drives something, and prints that before/after measurement on the page. The
  numbers in the doc and the numbers on the lab page come from the same call.

## 3.5.0 — 2026-09-08

- Grow the compiled chart vocabulary from sixteen types to **twenty-one**. `scatter`, `dumbbell`,
  `histogram` and `bullet` are new factories in `assets/report-shell.html`; `spark` was already
  there and is now compilable. Each one exists because a lens in
  `references/analysis-lenses.md` had no honest chart, not to raise the count.
- **`scatter` is the one that was costing the most.** `VIZ.bubbles` requires a `size` role and
  anchors both axes at the origin, so a dataset with exactly two measures had to invent a third
  column — the invented-number anti-pattern — and two measures that never approach zero smeared
  into one corner. The published pipeline example rejected the relationship lens on precisely that
  ground, in its own `LENS-ELIGIBILITY-001` decision and in its section prose. `VIZ.scatter` takes
  `label`/`x`/`y`, pads a data-derived domain, and accepts negatives: a dot is a position, not a
  length, so the zero-baseline rule that binds every bar does not bind it.
- `dumbbell` keeps both levels and the gap between them, where `slope` is about crossing and caps
  at 12 and `divHbars` throws the levels away. `histogram` bins a raw measure and **prints the bin
  count and width**, where `divColumns` draws a distribution someone already binned upstream where
  the reader cannot see it. `bullet` puts a value against the reference it was measured on, which
  the Judgement rules have always required on the page and no factory previously placed there.
- Open the factory options a plan could never reach. A chart may now carry `options`, validated per
  type: `interval`'s `reference` and `reference_label` — the line that decides which differences are
  claimable, and the whole point of that lens — plus axis names and an identity line on `scatter`
  and `bubbles`, the diverging mode on `divColumns`, a bin override on `histogram`, called-out marks
  on `concentration`, opening and closing labels on `waterfall`, a centre label on `donut`, end
  labels on `slope` and `dumbbell`, and `zero_based` on `line`, `boxplot` and `scatter`.
  `CHART-014` rejects an option the type does not read, `CHART-015` a value outside what the factory
  draws, and the builder owns the snake_case-to-camelCase translation.
- Refuse motion a factory cannot perform. `VIZ.spark` draws from a value list and never reads the
  progress value, so a `spark` declaring entry motion would sit still while the gate looked for
  movement. `CHART-016` is an error, not a warning.
- Fix the histogram count axis. `ticks()` spaces a small range in fractions and rounding those for
  display printed "1 1 1 0 0 0" up the axis — six gridlines claiming three values. Bin counts are
  whole numbers of rows, so the axis steps in integers and rounds its top up to one.
- Apply the masthead archetype the plan declares. `assets/report-shell.html` has always shipped CSS
  for M1–M6, and the builder never added the class: every report rendered as the M1 label stack
  whatever it recorded, so the published example declared `M3` and was not a nameplate. The builder
  now applies M1, M2, M3 and M6, and M2 gets the one number it is for through a new
  `masthead_figure` field. M4 wants per-section anchors with headline values and M5 a rail label —
  content the plan has no field for — so `MASTHEAD-002` refuses them rather than letting them fall
  back to something else. `MASTHEAD-001` rejects an unknown archetype, `MASTHEAD-003` an M2 with no
  figure, and `MASTHEAD-004` a figure on an archetype that does not render one.
- Publish a second report from the same support-intake CSV: **The backlog was never measured**,
  a fresh run from `INIT` with rotation and subject fit applied — `Briefing · desk · M2` against the
  first report's `Broadsheet · newsprint · M3`, with `desk` at a saturated 1.00 subject fit and
  rotation distance 2. It carries five charts where the first has three, using the two-series
  `columns`, `scatter` and `histogram`, and it is the first `M2` masthead this repository has built.
- Rebuild the published pipeline example against the new vocabulary. It gains the two scatters it
  could not draw: handling hours against tickets resolved, and opened against resolved under a
  `resolved = opened` identity line, below which 18 of the 24 months sit. That line is the report's
  first claim, drawn rather than counted, and the `LENS-ELIGIBILITY-001` decision now records a lens
  restored on evidence rather than one turned down on build capability.

## 3.4.0 — 2026-09-08

- Turn `references/analysis-lenses.md` from a lookup table into a selection procedure. The file
  named seventeen lenses and the shape each one needs, but not how a lens is chosen when several
  shapes are true at once, nor how its seventeen names relate to the five gates
  `assets/select-candidates.py` actually emits. Both joins are now written down.
- Add the **Gate** column and an *Eligibility, in two steps* section. Each lens now names the
  candidate gate — `trend`, `comparison`, `distribution`, `relationship`, `cohort` — that must be
  eligible before it is arguable, and the section states exactly what each gate tests: column
  types, column counts, and a six-period test on the date column. Nothing more. The gates never
  count rows per group, never check that two measures share a unit, and never read a cell, so an
  eligible gate is permission to consider a lens and not evidence for it. A table maps the rest of
  the mapping's conditions to the `profile.json` fields that settle them — `row_count`,
  `columns[].min`, `columns[].distinct_count`, `time_grains`, `comparable_periods`,
  `candidate_keys`, `null_rate`, `sentinel_candidates`.
- Say that the row caps **intersect**. The builder hands one `rows` array to every chart and the
  validator measures each one against the profile's single `row_count`, so a cap is not local to
  the chart that carries it: a five-slice `donut` makes the whole report a five-row report, and
  every other chart and table twin on the page then draws at most five rows. `donut` alongside
  `lollipop` is a five-row report, not a twenty-row one. The file previously said the cap applied
  to the source rather than the chart, which is half of it.
- Add *When two lenses both fit*: eleven pairs the mapping leaves open — `hbars`/`lollipop`,
  `hbars`/`donut`, `columns`/`stackedArea`, `columns`/`panels`, `waterfall`/`divHbars`,
  `slope`/`divHbars`, `bubbles`/`panels`, `boxplot`/`divColumns`, `heatmap`/`panels`,
  `concentration`/`hbars`, `interval`/`hbars` — each with the question that closes it. A slope
  chart with no crossing lines is a ranking drawn the hard way; `lollipop` drags its 20-row cap
  onto every other chart; `panels` exists for the two-unit case `columns` cannot take.
- Add *What the lens costs downstream*: the motion band the factory fixes at the moment the lens is
  chosen — reveals at 600–800 ms, `waterfall` at 600–900, value-scaled marks at 400–600, spread at
  300–500, `bubbles` at 700–900 — so the consequence is visible during selection rather than at
  `MOTION-FIT-002`. `references/motion-features.md` remains the authority for the easings.
- Add *When nothing fits*: the four honest exits, in order — aggregate upstream of profiling,
  rewrite the claim down to the evidence, keep the table twin and drop the chart, drop the section
  and disclose it. A caveat in a card note does not undraw a mark.

## 3.3.0 — 2026-09-07

- Grow the compiled chart vocabulary from seven types to **sixteen**. `divHbars`, `donut`,
  `heatmap`, `slope`, `waterfall`, `boxplot`, `stackedArea`, `panels` and `interval` join the
  builder, and `columns` gains a second and third series. Nothing new was added to the runtime:
  every one of these factories already shipped in `assets/report-shell.html`, and
  `references/analysis-lenses.md` already listed them as the lens each data shape earns — the
  pipeline simply could not compile them from a plan, so the reference promised charts the builder
  refused. It no longer does.
- Give `analysis-lenses.md` the encodings contract: every type, the roles it requires, the roles it
  accepts, the row counts the factory will draw, and which measures it will not take negative.
- Check every encoding against the profile rather than only against the column list.
  `CHART-008` rejects a role the type does not read, `CHART-010` a category in a measure role — the
  check is per type, because `x` and `y` are measures on `bubbles` and categories on `heatmap` —
  `CHART-011` a negative value under a chart that reads magnitude as a share, an area, or an
  intensity, and `CHART-009` a row count below what the factory will draw. A category in a measure
  role used to draw a mark of length NaN, which is no mark at all and no error either.
- Emit a legend for a multi-series chart. `columns`, `stackedArea` and `panels` read `value`,
  `value2` and `value3`, painted `s1`, `s2`, `s3`; the builder writes the `.legend` and repaints it
  from `R.onTheme()`, naming each series by the column it reads so the key and the table twin cannot
  disagree. There is no `value4`: `references/themes.md` will not invent a fourth colour.
  `CHART-013` warns that a donut past three parts hits the same wall from the other side, because
  the factory cycles the same three colours and parts four and five repeat parts one and two.
- Route motion for the nine new factories. `slope` and `waterfall` are reveals like `line`;
  `donut`, `heatmap`, `stackedArea`, `panels` and `divHbars` are value-scaled like `columns`; and
  `boxplot` and `interval` get the shortest run in the table, 300–500 ms, because they grow spread
  outward from a value already in place — every intermediate frame shows a **narrower** interval
  than the data supports, which is an overclaim rather than a delay.
- Fix two colour and layout defects the new types exposed. `VIZ.donut` and `VIZ.slope` take
  `cfg.color` as the *default* handed to `colorOf`, which returns a default unresolved, so the token
  name `s1` was painted as the literal string and canvas kept the previous fill — every arc and every
  slope line drew black. And `VIZ.slope` measured its row labels before setting the font it draws
  them with, so a long label was clipped at the canvas edge instead of ellipsised.

## 3.2.0 — 2026-09-07

- Add `references/motion-features.md`: a per-feature catalogue of the two documentation pages a
  plan is most likely to be written from — [Motion's quick-start](https://motion.dev/docs/quick-start)
  and [anime.js's *Using with vanilla JS*](https://animejs.com/documentation/getting-started/using-with-vanilla-js).
  Every advertised feature gets a one-line summary, the call as the **pinned** 11.11.17 / 3.2.2 file
  would take it, and a verdict — *used*, *shell*, *held*, *absent*, or *refused* with the reason.
  The two pages document 13.x and 4.0.0; the pins are two majors behind on both, so every v4 name
  in the anime.js example (`animate`, `utils`, `createDraggable`, `spring`) is absent from the file
  a report actually inlines, and Motion's `hover`/`press` are not in 11.11.17 either. Registered as
  a conditional reference, read before any motion contract is written.
- Route motion per chart factory rather than per taste. What a chart's progress value scales
  differs — `line` and `concentration` reveal points, `columns`, `hbars`, `lollipop` and `bubbles`
  scale the mark itself — so a reveal takes a steady curve at 600–800 ms and a value-scaled mark one
  that arrives early at 400–600 ms, with `bubbles` at 700–900 ms because radius is the square root
  of area. `assets/validate-plan.py` now warns with `MOTION-FIT-001` (curve) and `MOTION-FIT-002`
  (duration) when a chart leaves its band, and registers `MOTION-FIT-001` in `references/rules.json`.
- Make the portable-path duration ceiling an error rather than a footnote.
  `MOTION-PORTABLE-CEILING-001` fires when a `portable-pattern` chart declares more than 900 ms,
  which the shell's `anim()` silently clamps and no downstream gate compares.
- Add a dedicated theme step: **compatibility, subject fit, then rotation**, in that order.
  `assets/select-candidates.py` now scores every compatible theme against what the dataset is
  *about* — profiled column names, the source file name, and the stated requirements, tokenised and
  matched against each theme's subject keywords — and ranks fit above rotation distance. A
  subject-neutral theme carries a baseline so data whose columns name no domain still has
  candidates. The candidate artifact gains `subject_signals`, and each theme row gains `fit_score`
  and `fit_matched`.
- Require `plan.theme_rationale` — subject, signals, and the `fit_score` and `rotation_distance`
  **copied** from the candidate artifact. `assets/validate-plan.py` checks the record against that
  artifact: `THEME-FIT-002` for a missing or malformed rationale, `THEME-FIT-003` for a number that
  does not match, `THEME-FIT-004` for a signal the artifact never produced, and a `THEME-FIT-001`
  warning when a theme matching nothing was chosen over a compatible theme that fits.
  `THEME-SELECTION-001` provenance is now required in `rule_decisions`, and `THEME-FIT-001` joins
  the rule registry.
- Grow the catalogue from ten themes to **twenty-six**. The sixteen new faces exist because a
  common kind of dataset deserves one that belongs to it: `abacus` (finance), `clinic` (clinical),
  `atlas` (place and movement), `voltage` (energy), `campus` (education), `pitch` (competition),
  `bazaar` (retail), `blueprint` (built environment), `sentinel` (security), `assay` (laboratory),
  `civic` (public sector), `signal` (growth analytics), `roster` (workforce), `desk` (support
  queues), `tide` (climate), and `flux` (network). Six themes are now dark-native.
- Add `references/themes.json` as the canonical catalogue — axes, character, subjects, fit baseline
  — read by both `select-candidates.py` and `validate-plan.py`, which no longer keep their own
  copies of the theme list.
- Add `assets/make-themes.py`, which solves the new blocks rather than picking them: a hue and
  chroma are chosen for the role, then lightness is searched until the token clears its contrast
  floor on the darkest *and* lightest ground a card can present — `--bg`, `--surface-1` and
  `--surface-2` — not only on the page. The ten original hand-frozen themes are untouched.
- Add `assets/check-themes.py`, which proves the contrast contract for all 26 themes across all
  three drops and fails when `themes.css` and `references/themes.json` disagree about which themes
  exist (`THEME-CATALOGUE-001`/`-002`). It is what makes "hand-editing a value breaks the contract"
  checkable rather than merely stated.
- Add `assets/theme-sheet.py` and regenerate `docs/themes.png` for all 26 themes, each shown in the
  band it ships as its default. The sheet is composed by Chrome from real reports rather than by an
  image library, so a tile cannot drift from what a reader sees.

## 3.1.0 — 2026-09-07

- Remove Lottie and Rive from tool selection, documentation, lab pages, generated sample assets,
  vendored runtimes, fetch checksums, and licence inventory.
- Separate visualization/state sources from motion engines: D3 and Plotly can no longer satisfy
  `motion.source_tool`; only GSAP, Motion, and anime.js can.
- Add pinned vendored-runtime build and real-clock validation paths for GSAP 3.12.5, Motion
  11.11.17, and anime.js 3.2.2, including runtime version and SHA verification.
- Make `references/external-tools.md` a required toolchain router for D3, Plotly, GSAP, Motion,
  and anime.js patterns.
- Add `creative_direction` to plan/spec contracts with external-tool selection provenance and a
  report-level motion story.
- Make chart motion executable per chart with declared trigger, duration, and value-safe easing;
  the builder now honors those settings instead of applying one global animation duration.
- Align the motion reference and final scorecard with the deterministic builder's actual `entry`
  motion capability.
- Let render and motion gates use `CR_CHROME` when Chrome is installed outside the executable
  search path.
- Measure motion in the window a reader opens the file into. `check-motion.py` now loads the
  report at 1280×800 first and records whether any chart with motion is on the first screen,
  then runs its existing wiring, engine and final-state checks in the taller viewport as
  before. Where every chart sits below the fold — which a masthead-first macrostructure makes
  the common case — it reports `MOTION-VIEWPORT-001`.
- Rebuild the example under that reference. Its lead chart is a `line`, where `c.t` is a point
  count rather than a value, so the easing is the pace of the sweep: `linear` at 720 ms paces the
  24 months evenly, where `outCubic` — what the run had — puts seven of them on screen in the first
  tenth and crawls through the rest. Same three charts, same claims, new run from `INIT` to
  `COMPLETE` with no repair attempts.
- Note that the two integration paths do not enforce the same duration bound. The plan schema and
  the motion gate take 180–1200 ms, and the vendored path clamps to exactly that, but the shell's
  own `anim()` caps at 900 ms — so a `portable-pattern` chart declaring 1,000 ms passes every check
  and runs for 900, because the gate reads the declared attribute rather than the elapsed time.
  `motion-engines.md` now says not to declare more than 900 ms on the portable path.
- Add `references/motion-engines.md`, and register it as a conditional reference. The engines'
  own getting-started pages advertise scroll-linked motion, springs, staggers, timelines, drag,
  and an SVG toolset; a report calls exactly one of their functions, once per chart, to move one
  number from 0 to 1. The new file maps every advertised feature onto that reality — used, banned
  by `motion.md`, owned by the shell already, or absent from the pinned build — with the pinned
  call form beside the documented one, including the v4-to-3.2.2 translation anime.js's own vanilla
  page now requires (`animate(targets, …)` → `anime({targets, …})`, `ease` → `easing`, `onUpdate` →
  `update`, and a `stagger` whose options were renamed).
- Choose the easing and the duration from what the factory does with the progress value. `c.t` is a
  reveal in `line` and `concentration` (`round(rows.length · t)`), a height in `columns` and
  `divColumns`, a length in `hbars` and `lollipop`, and a **radius** in `bubbles`, where area
  therefore grows with `t²`. A value-scaled mark displays a number smaller than its datum until it
  lands, so those charts take a curve that arrives early and a shorter window; a reveal's easing is
  its reading pace instead. `motion-engines.md` carries the per-factory table.
- Republish the pipeline example as a new report. Making motion contracts executable changed what
  the builder emits, and the shipped `examples/support-intake-pipeline-run.html` predated that: it
  carried no `data-motion-*` contract, so `check-motion.py` rejected it with eight
  `MOTION-CONTRACT-*` errors — the repo's own showcase failing the repo's own gate. Rather than
  reprint the old plan, the example is written again from the same published CSV and rotated:
  **Broadsheet · newsprint · M3** against the previous Briefing · cobalt · M4. Its subject is the
  identity the file actually contains — `backlog_end` moves by exactly `tickets_opened` minus
  `tickets_resolved` in all 23 consecutive month pairs, which makes the backlog a running total
  rather than a measurement and implies a balance of 180 before the file opens. Three charts, one
  of which moves.
- Say that `VIZ.bubbles` scales both axes from zero. Writing that example turned up the constraint:
  the Relationship lens was eligible on the profile, and a scatter of handling hours against
  tickets resolved would have put all 24 marks in one corner of an empty plot, because neither
  measure comes near zero and the factory takes no domain. `references/analysis-lenses.md` now says
  to check the ranges against zero before selecting the lens, and the example demonstrates the
  refusal rather than shipping the smear.
- Leave the pre-3.0.0 DART example as published, and say why in `examples/index.md`: no source rows
  exist to rebuild it from, hand-editing a generated report is what this skill refuses, and one
  fragment of its `read:` stamp no longer resolves because 3.0.0 rewrote the passage it quotes.
- Capture what the pinned motion runtimes actually expose, and stop trusting the links for it.
  `lab/motion-engines/probe-api.py` reads GSAP 3.12.5, Motion 11.11.17, anime.js 3.2.2 and D3
  7.9.0 out of `vendor/` in headless Chrome, resolves the builder's own plan-easing tables against
  each engine, and writes `docs/api-surface.json`; `--expect` fails on drift.
  `docs/api-surface.md` reads that snapshot against what each site documents today. Two gaps
  mattered: **animejs.com now documents v4**, eleven of whose fourteen headline names do not occur
  in the pinned 3.2.2 file, and `references/external-tools.md` was describing them as available;
  and Motion's newer `visualDuration` is absent from the pinned build yet accepted without error,
  because Motion validates no option names. All twenty-one plan-easing mappings resolve.
- Say which state a repair rewinds to. The retry ladder told the Agent to pass the failed state
  to `report-state.py retry`, but three of its four strategies edit `plan.json`, whose hash
  `VALIDATED` owns; retrying `BUILT` after such an edit left the next `advance` failing with
  `STATE-012`, and the wasted retry had already spent one of the four attempts. §6 now names the
  rewind point per repair kind and says what a mistargeted retry costs. The state machine is
  unchanged.
- Honour `severity` in the post-build gates. A diagnostic marked `warning` is recorded in
  `validation.json` without failing its phase; every other severity, including a missing one,
  still blocks. `MOTION-VIEWPORT-001` is the first and only warning: on-view entry motion is
  the declared contract, so a report whose motion waits for the scroll is being described,
  not failed.

Versions are the `version:` field in `SKILL.md`. Dates are the day the work landed on `main`.

## 3.0.0 — 2026-09-07

A break at the level of who is allowed to write what. Through 2.1.3 the skill was prose: `SKILL.md`
described a report and the Agent wrote the HTML. Every guarantee — an honest number, a table twin,
a reason for motion — rested on whoever was reading the instructions that day, and afterwards
nothing could say which requirement had been dropped. A report built against 2.1.3's checklist
does not pass 3.0.0's gates, and several of the mechanisms it relied on are gone rather than
changed.

### The run is a state machine over artifacts

- `INIT → PROFILED → VALIDATED → PLANNED → BUILT → VERIFIED → COMPLETE`. `assets/report-state.py`
  binds each state to the SHA-256 of its inputs and rejects a skipped transition. A changed
  upstream artifact invalidates everything downstream, so a report can no longer stand on a
  profile that no longer holds.
- **One writer per artifact.** `assets/profile-data.py` owns `profile.json`; the Agent owns
  `plan.json` *and nothing else*; `assets/validate-plan.py` owns `report-spec.json`;
  `assets/build-report.py` owns the HTML. The shell, the `VIZ` factories and the motion engines
  are read-only to a run, and validators report without repairing.
- Hand-editing a generated report is now a named anti-pattern rather than a shortcut: a plausible
  patch can contradict the profile it claims to come from and has no reproducible source.
- `schemas/` ships the contracts — `plan`, `profile`, `report-spec`, `diagnostic` — and every
  diagnostic anywhere in the pipeline carries `{severity, id, location, problem, suggested_fix}`.
- A failed gate follows a bounded ladder: **Local Fix → Component Rebuild → Simplify → Drop
  Unsupported Section**, recorded by `report-state.py retry`. The fifth attempt is rejected. No
  step in it edits generated HTML or downgrades an error to a warning.

### Rule IDs are the provenance; a quotation is not

- `references/rules.json` and `references/index.json` make the rules machine-readable, and the
  rule IDs recorded in profile, spec and validator results are what proves a rule ran.
- Every diagnostic anywhere in the pipeline carries a Rule ID in one format — uppercase segments
  and a three-digit number, `AREA-001` or `AREA-DETAIL-001`. `schemas/diagnostic.schema.json`
  enforces it, and `validate-report.py` reports a validator that emits anything else. Where a
  finding *is* a registry rule the registry ID is what gets reported, so a runtime external
  request and a static one both come back as `ZERO-NETWORK-001`, and an overflowing layout as
  `RESPONSIVE-001`, whichever gate caught it.
- 2.1.0 added `assets/check-quotes.py` after a stamp quoted `motion.md`'s "Play once on entry"
  verbatim and recorded the opposite decision; the answer then was to verify the quote. 3.0.0
  stops treating quotation as evidence at all — a correctly copied fragment can still be stale,
  irrelevant, or misapplied. A `read:` stamp is an optional explanatory note and never a gate;
  the checker still ships so older reports remain verifiable on their own terms.

### Motion is declared per chart

2.1.0 made motion opt-out: `R.playAll` wired every registered chart and a chart that must not move
declared `{static:true}`. Where the declaration was simply omitted, "forgot to animate" and
"deliberately static" were indistinguishable, so gate 46 could be satisfied by saying nothing.

- Every canvas now carries `data-motion-enabled` and `data-motion-reason`. `mk()` reads them and
  sets `opt.static` for a disabled chart, so intent lives on the element a validator can see.
- `motion: {enabled, reason}` is a required field on every chart in `plan.json`, and
  `validate-plan.py` rejects a chart that does not state its intent. A non-empty reason is
  required either way — a static chart has to say why it is static.
- `assets/check-motion.py` is rewritten around that contract: it gates only the charts that claim
  to move (wired, animating, landing on `t=1`), requires the others to be visually unchanged
  across the probe, and emits Rule-ID diagnostics with `--json`.
- The shell and the published example now declare their intent, which is why their diffs are
  attribute-only.

### Two more gates, and one artifact for their results

- `assets/check-render.py` drives the built report through the DevTools protocol and validates its
  render and layout surface.
- `assets/validate-report.py` runs the post-build gates progressively into one `validation.json`:
  the HTML must carry the `spec-sha256` of the spec it claims to come from, hold exactly as many
  canvases as the spec declares, and contain no `http(s)` script, link or image; then render; then
  motion, and only where the spec declares motion. `--skip-motion` is itself a diagnostic when any
  chart enables motion.
- `assets/select-candidates.py` derives the compatible macrostructure, theme and lens sets from the
  profile before the Agent chooses, so rotation is a filtered decision rather than an improvised one.

### Gates that a generated report can actually pass

Found by running the pipeline end to end on a 24-month CSV before tagging this version.

- **`FINAL-BUILD-002` counted `<canvas` in the HTML source.** The builder creates every chart
  canvas at runtime, so a correct report contains none, and the one match it did find was the
  word `<canvas height="104">` inside a comment in the shell — the same shape of bug as 2.1.1's
  `<title>` substitution. No generated report could have reached `VERIFIED`. The static phase now
  compares the chart ids the builder embedded against the spec, and the rendered count moved to
  `check-render.py --expect-canvases`, which counts elements in the DOM at each viewport and
  reports `RENDER-CANVAS-003`.
- **A chart could ship a runtime refusal message and pass every gate.** `VIZ.lollipop` draws at
  most 20 marks and otherwise prints "a lollipop chart shows at most 20 items" onto the canvas.
  With 24 rows that is what the reader got: the plan validated, the build succeeded, the render
  gate saw a canvas with sensible bounds, and the motion gate saw a chart declared static that
  did not move. `validate-plan.py` now knows the runtime's mark caps and rejects the chart at
  plan time as `CHART-007`, which is what the retry ladder's **Simplify** step is for.

### Installable as a plugin

- The skill was only ever installable by cloning it and pointing Claude at `SKILL.md`. This
  repository is now also a Claude Code plugin and the marketplace that lists it:
  `/plugin marketplace add seohyunjun/canvas-report`, then
  `/plugin install canvas-report@seohyunjun`. Nothing moved to make that work — a plugin with no
  `skills/` directory loads its root `SKILL.md` as a single skill, and the invocation name comes
  from that file's frontmatter. Requires Claude Code v2.1.142 or later.
- `.claude-plugin/plugin.json` carries the version, so it has to be bumped alongside `SKILL.md`
  at every release: a plugin that declares a version is pinned to it, and users are offered an
  update only when that string changes.

### Rotation, insight count, and offline output

- **`.canvas-report/log.json` and the HTML stamp comment are no longer where rotation history
  lives.** It lives in run artifacts. The rule is also sharper: discard incompatible themes first,
  then require **rotation distance ≥ 2** from the previous compatible theme. A user may request a
  compatible nearer theme; the override and its compatibility evidence are recorded in `plan.json`,
  and an incompatible request gets a diagnostic and an alternative.
- **The 4–6 insight floor is gone.** An evidence-driven set, typically 2–6. Padding a report to
  fill a quota promotes weak observations to claims, and is listed as an anti-pattern.
- **The Google Fonts opt-out is removed** from `themes.md`. Offline output is unconditional; there
  is no acceptable single request.
- **A bar chart's zero baseline no longer has an escape hatch.** 2.x allowed breaking it if the
  axis help said so; a bar's length *is* the value, so the guidance is now to use a different
  chart.

## 2.1.3 — 2026-09-06

- **A report served over HTTP fetched one thing after all** — not from the page, from the browser,
  which probes the origin for `/favicon.ico` when no icon is declared. Measured on the published
  example: one request, 5,442 bytes. The shell now inlines a `data:` SVG icon, so the count is
  zero over HTTP as it always was from `file://`, and a report has a tab icon offline too.
- `examples/` and GitHub Pages: one report published exactly as the skill produced it.

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
- `lab/motion-engines/`: one page per engine (GSAP, Motion, anime.js, D3) with
  usage notes, vendored runtimes pinned and SHA256-verified, and licences flagged. Every page
  carries an explicit final-state paint, because none of the engines guarantees one.
- `README.md` documents how to use the skill, not only how to install it.

## 2.0.0 — 2026-09-05

Initial commit. `canvas-report` merges two lineages: the analytical disciplines of
`canvas-data-report` (data shape to lens, table twins, help tooltips, a methodology section) and
the structural variety of `hallmark` (rotating macrostructure, theme and masthead).
