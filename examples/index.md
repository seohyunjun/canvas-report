---
title: Examples
---

# Examples

Reports this skill produced, published exactly as they came out of it — one HTML file each,
no libraries, no network requests. Open one and view source: the runtime, the data and the
wiring are all in the file.

Each report carries a stamp at the top of its source. From 3.0.0 that stamp is the SHA-256 of the
`report-spec.json` the report was built from, followed by the Rule IDs the plan recorded a decision
against, so a reader can tie the file back to the run that produced it. Reports built before 3.0.0
carry the older stamp instead: macrostructure, theme and masthead, plus a `read:` block quoting the
reference passages behind each decision, machine-checked with `assets/check-quotes.py`.

| Report | Macro · theme · masthead | What it is about |
|---|---|---|
| [평균의 평균은 평균이 아니다](dart-2025-payroll-average.html) | 01 Briefing · almanac · M2 | DART 2025 filings, 446 companies. The mean of company means is ₩83.5M; payroll divided by headcount is ₩99.7M. The gap comes only from the choice of denominator. |
| [The backlog is arithmetic](support-intake-pipeline-run.html) | Broadsheet · newsprint · M3 | **Synthetic data.** 24 monthly rows, generated for this example, published with the CSV it was built from ([support-intake-pipeline-run.csv](support-intake-pipeline-run.csv)). The month-end backlog turns out to be exactly the running sum of opened minus resolved, so the report is about an identity rather than about support work. It is here to show what the pipeline emits end to end. |
| [The backlog was never measured](support-intake-monthly-briefing.html) | Briefing · desk · M2 | **Synthetic data.** The same 24 rows and the same CSV, run again from `INIT` under the expanded chart vocabulary. Five charts instead of three: the backlog line, opened and resolved as paired bars on one axis, the two scatters, and a histogram of the hours column. It leads with the conclusion the other report arrives at. |

The second report is the whole state path run once: `profile-data.py` → an Agent-written `plan.json`
→ `validate-plan.py` → `build-report.py` → `validate-report.py`, with every state bound to its
artifact hashes. Three of its five charts declare entry motion and two declare themselves static,
and `check-motion.py` gates them on that declaration rather than on whether anything moved. The
enabled contract names its kind, trigger, duration, easing and motion engine, and the plan records
the report-level motion story and the tool selection behind them — which is why the file carries
`MOTION-STORY-001` and `TOOL-SELECTION-001` in its stamp.

The easing on that one chart is chosen from what the factory does with the progress value rather
than from taste. `VIZ.line` reveals by point count, so the curve is the pace of the sweep: `linear`
paces the 24 months evenly across 720 ms, where a decelerating curve would put seven of them on
screen in the first tenth of the run and crawl through the rest.
[`references/motion-features.md`](../references/motion-features.md) has the table this came from,
alongside the feature-by-feature reading of the Motion and anime.js documentation it sits in.

It also carries a lens that this repository could not draw until 3.5.0, and the report is worth
reading twice for it. The relationship between handling hours and tickets resolved was always
eligible on the data, and the earlier version of this page did not chart it: the only scatter the
builder compiled was `VIZ.bubbles`, which forces both axes through zero, and measures running from
1,034 to 1,606 against 1,645 to 2,566 would have landed in one corner of an empty plot. The plan
said so in `LENS-ELIGIBILITY-001` and the section said so in its own words — a lens turned down on
build capability rather than on evidence, which is the one reason a lens should never be turned
down. `VIZ.scatter` takes its domain from the data, so both charts are now on the page: hours
against resolutions, and opened against resolved with a `resolved = opened` identity line under
which 18 of the 24 months sit. That line is the report's first claim, drawn instead of counted.

The two support-intake reports are the same file twice, and the pair is the point. Rotation and
subject fit were applied to the second: `Broadsheet · newsprint · M3` became `Briefing · desk · M2`,
with `desk` scoring 1.00 on subject fit — the catalogue's saturation point, matched on *backlog*,
*handling*, *intake*, *queue*, *resolution*, *resolved* and *ticket* — at rotation distance 2 from
`newsprint`. Fit and rotation agreed, so no override was needed. The second report also uses three
chart types the first could not: the two-series `columns` that puts opened and resolved on one
shared axis, and the `scatter` and `histogram` that carry the relationship and distribution lenses.
Its masthead is the first `M2` this repository has built — the archetype a plan declared was, until
3.5.0, recorded in the spec and never applied to the page.

The first report predates all of that. It was built before 3.0.0, so it carries the older `read:`
stamp rather than a spec hash, its charts declare no executable motion contract, and the current
`check-motion.py` therefore has nothing to gate them against. One fragment in its stamp no longer
resolves: it quotes `references/motion.md` as it read before 3.0.0 rewrote that file. The quote was
true when the report was built and `check-quotes.py` is right to say it no longer matches — the
report is kept as published rather than edited to agree with a reference it never read.
