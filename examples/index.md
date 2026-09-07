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
| [Two years of support intake](support-intake-pipeline-run.html) | Briefing · cobalt · M4 | **Synthetic data.** 24 monthly rows, generated for this example, published with the CSV it was built from ([support-intake-pipeline-run.csv](support-intake-pipeline-run.csv)). It is here to show what the 3.0.0 pipeline emits end to end, not to say anything about support work. |

The second report is the whole state path run once: `profile-data.py` → an Agent-written `plan.json`
→ `validate-plan.py` → `build-report.py` → `validate-report.py`, with every state bound to its
artifact hashes. Two of its four charts declare entry motion and two declare themselves static, and
`check-motion.py` gates them on that declaration rather than on whether anything moved. Each
enabled contract now names its kind, trigger, duration, easing and motion engine, and the plan
records the report-level motion story and the tool selection behind them — which is why the file
carries `MOTION-STORY-001` and `TOOL-SELECTION-001` in its stamp.

The first report predates all of that. It was built before 3.0.0, so it carries the older `read:`
stamp rather than a spec hash, its charts declare no executable motion contract, and the current
`check-motion.py` therefore has nothing to gate them against. One fragment in its stamp no longer
resolves: it quotes `references/motion.md` as it read before 3.0.0 rewrote that file. The quote was
true when the report was built and `check-quotes.py` is right to say it no longer matches — the
report is kept as published rather than edited to agree with a reference it never read.
