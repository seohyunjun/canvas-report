# Motion — evidence, not a default

For the decision framework and chart-by-chart policy, see
[`motion-decision.md`](motion-decision.md). This file documents the lower-level runtime contract.

Motion is optional. A chart is static unless its validated `report-spec.json` declares a specific
reader benefit. The plan records that decision per chart, and `assets/check-motion.py` runs only for charts
that declare motion. Motion never substitutes for a table, label, or explanation; the final static
state must contain all information.

## Permitted meaningful cases

| Case | What motion communicates | Contract |
|---|---|---|
| Waterfall flow | movement from opening to closing is the claim | one bounded sequence |
| Scrollytelling transition | the reader follows a change on one coordinate system | transition tied to step change |
| Keyed re-sort | the same entity moved position | stable `cfg.key`, ≤420ms |
| Intentional entry reading aid | axes/baseline register before marks settle | play once, never required to understand the chart |

Every other case is static unless the plan proves a distinct information benefit. Loops, hover zoom,
colour pulses, staggered entrances, loading skeletons, and motion merely to make a report feel
alive are decorative and prohibited.

## Per-chart plan contract

For every chart, the plan/spec says either:

```json
{"motion":{"enabled":false,"reason":"Static comparison is clearer."}}
```

or:

```json
{"motion":{"enabled":true,"kind":"keyed-resort","reason":"Preserves entity identity across ordering.","key":"entity_id","duration_ms":420}}
```

A filter is never a keyed re-sort. When rows appear or disappear, redraw at `0ms`; travelling
survivors falsely implies continuity. A missing, positional, or formatted-changing key is not
stable and must disable re-sort motion.

## Runtime boundaries

Report runs do not edit the runtime shell, resize/layout code, tooltip engine, `VIZ` factories, or
motion engine. The deterministic builder applies the validated motion contract to the read-only
runtime. `R.reduced()` omits motion rather than slowing it; `R.onView` plays once; `R.paintAll()`
repaints filters; `chart.play(duration, easing)` must always resolve to a final draw.

Use only value-safe curves for marks whose geometry represents values. Overshoot is not valid for
such marks because it temporarily asserts a value outside the axis. `R.countUp` and opacity/small
translate UI effects may use their documented non-mark curves.

## Validation

Render screenshots with reduced motion for layout, but do not treat that as motion evidence.
`assets/check-motion.py` validates declared motion on a real clock and reports structured Rule-ID
diagnostics. It checks that the declared animation starts when intended, reaches final state, and
does not require motion for comprehension. A static chart has no motion gate.

The required ordering is: validate the per-chart contract in `assets/validate-plan.py`, build from
`report-spec.json`, then run `assets/check-motion.py` only where the spec requires it. A failure follows
the run retry ladder: Local Fix → Component Rebuild → Simplify → Drop Unsupported Section.

## Legacy provenance

Reports created before the declarative motion contract may cite the former rule
“Play-once-on-entry is the default, not an extra.” That sentence is retained only so their
historical quote stamps remain verifiable; it is superseded by explicit per-chart motion intent.
