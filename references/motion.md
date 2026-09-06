# Motion — choreograph the reading, preserve the evidence

Motion is considered for every report and decided per chart. Start with one report-level reading
sequence, then enable only the transitions that help the eye acquire axes, follow marks, or retain
object identity. The final static state, table twin, labels, and methodology carry the full meaning.

## Start with a motion story

Before assigning chart animations, write `creative_direction.motion_story`:

- `goal` names the reader benefit;
- `sequence` orders the masthead, lead evidence, supporting evidence, and resolution;
- `restraint` names what will not move.

Avoid simultaneous motion in competing cards. A practical default is one lead transition followed
by play-once, on-view entry for later evidence charts. Returning to a chart does not replay it.

Tie every enabled chart to one dedicated motion engine selected in
`creative_direction.external_tools` through `motion.source_tool`. Valid chart-entry sources are
GSAP, Motion, and anime.js. D3 remains a visualization/data-join tool and Plotly remains a
visualization/state-model tool; neither may be reported as the primary motion engine.

## Current deterministic builder contract

The shipped builder supports one executable chart motion. It can be driven either by the compact
portable runtime or by one pinned vendored engine selected at report level: GSAP 3.12.5, Motion
11.11.17, or anime.js 3.2.2.

| Kind | Trigger | Use | Bounds |
|---|---|---|---|
| `entry` | `on-view` | axes/baseline register before marks settle into the final reading | 180–1200ms, value-safe easing, once |

An eligible chart should use this reading aid unless data density, comparison speed, or cognitive
load makes static presentation clearer. Static is not a shortcut: its reason must be specific to
that chart.

```json
{
  "motion": {
    "enabled": true,
    "reason": "The baseline appears first so the size comparison resolves in reading order.",
    "kind": "entry",
    "trigger": "on-view",
    "duration_ms": 620,
    "easing": "outCubic",
    "source_tool": "motion"
  }
}
```

```json
{
  "motion": {
    "enabled": false,
    "reason": "Dense labels are faster to scan without mark growth."
  }
}
```

Value-safe easing values are `linear`, `outCubic`, `inOutCubic`, `outQuint`, `outExpo`,
`outCirc`, and `inOutQuint`. Overshoot curves temporarily assert values beyond the axis and are
therefore invalid for data marks.

## Richer motion

Waterfall flow, scrollytelling transitions, and keyed re-sorts can communicate more than entry
motion, but only use them with a selected builder/runtime that implements their state model and
validator. The current deterministic builder does not compile those kinds from `plan.json`; do
not declare them and hope the shell will infer the choreography.

Filters always redraw at `0ms`. Rows appearing or disappearing are not a keyed re-sort. Travelling
survivors would falsely imply continuity.

## Runtime boundaries

Report runs do not edit the runtime shell, resize/layout code, tooltip engine, `VIZ` factories, or
motion engine. The builder applies the validated contract. `R.reduced()` omits motion rather than
slowing it, `R.onView` plays once, and every `chart.play(duration, easing)` resolves to a final draw.

Loops, stagger cascades, hover zoom, colour pulses, loading skeletons, and motion used merely to
make a report feel alive are prohibited. Small UI affordances may move only when they clarify a
state change and must remain usable under reduced motion.

## Validation

Render screenshots with reduced motion for layout, but do not treat them as motion evidence.
`assets/check-motion.py` uses a real clock to verify that enabled charts are wired, produce multiple
states, finish at `t === 1`, and leave disabled charts static. When `vendored-runtime` is declared,
it also verifies that the selected GSAP, Motion, or anime.js runtime actually drove the chart and
that its version/SHA marker matches the pinned vendor file. Run it through
`assets/validate-report.py` whenever any chart enables motion.

A failure follows the retry ladder: Local Fix → Component Rebuild → Simplify → Drop Unsupported
Section. Never turn motion off merely to silence the gate; disable it only when the revised plan
gives a better reader-centered reason.
