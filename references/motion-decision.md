# Motion Decision

Motion is optional. Static visualization is the default. Do not add motion for decoration,
novelty, or visual appeal alone. The final static state must contain all information.

## Decision flow

1. Identify the insight and the narrative relationship the visualization must communicate.
2. Decide whether understanding depends on a transition, sequence, reordering, progression, or guided attention.
3. If no temporal or structural change needs to be communicated, use a static visualization.
4. If motion improves comprehension, select exactly one semantic motion intent.
5. Validate that the intent is compatible with the visualization type and narrative.

### Allowed semantic motion intents

| Intent | Meaning |
|---|---|
| `data-transition` | A meaningful change or progression between states. |
| `spatial-reordering` | A ranking, ordering, or position change. |
| `narrative-transition` | A sequential stage change in scrollytelling. |
| `attention-guidance` | A deliberate, one-time reading aid for important information. |

Use motion only when the answer to at least one question is yes:

- Does the reader need to understand how one state becomes another?
- Does an ordering or ranking change carry analytical meaning?
- Does the narrative require a transition between sequential stages?
- Does guided attention materially improve understanding?

Every decision has this shape:

```json
{
  "enabled": true,
  "intent": "data-transition",
  "reason": "The bridge explains how the opening value becomes the closing value.",
  "fallback": "Show the completed waterfall with every component labelled."
}
```

For static output, set `enabled` to `false`, `intent` to `null`, explain why, and name the
equivalent static representation. A missing decision is not a static decision.

## Visualization policies

| Visualization | Default | Recommended motion | Cautions |
|---|---|---|---|
| Line chart | Disabled | `data-transition` when the change over time is the claim; `attention-guidance` for a one-time entry aid. | Do not make a static trend look like a live feed. Keep every period and the final labels. |
| Bar chart | Disabled | `spatial-reordering` only when the same entities change rank; otherwise `attention-guidance` once on entry. | A filter is not a re-sort. Stable keys are required; never imply continuity for entering or leaving rows. |
| Scatter / bubbles | Disabled | `data-transition` when entities move through meaningful states or `attention-guidance` once to register axes. | Do not animate points for decoration or hide outliers; labels and the final state remain available. |
| Waterfall | Disabled | `data-transition` when the bridge from opening to closing is the insight. | Play once, never loop, and show the residual explicitly. Motion must not be required to reconcile totals. |
| Boxplot | Disabled | `attention-guidance` once when the distribution shape benefits from staged reading. | Never animate quartiles as if they were observations. Keep points, sample size, and outliers static and visible. |
| Histogram / diverging columns | Disabled | `data-transition` only for a meaningful distribution change between states. | Do not use staggered bars as decoration; preserve zero, bin labels, and both directions. |
| Tiles / stat boxes | Disabled | `attention-guidance` only for one important value when guided attention materially improves reading. | A grid of moving numbers is noise. Do not count up every tile. |
| Table | Disabled | `spatial-reordering` only when row movement itself is the analytical finding. | Keep sort controls usable, preserve row identity with a stable key, and never animate ordinary filtering. |

## Runtime contract

`cfg.motion` is the source of truth for a chart. It must contain `enabled`, `intent`, `reason`,
and `fallback`. Enabled motion has exactly one allowed intent; disabled motion has `intent: null`.
The shell rejects invalid or incompatible combinations and falls back to a static draw. Runtime
engines decide how a valid intent is implemented; this document does not prescribe duration,
easing, frames, or engine names.

## External tool extension

External engines may be used in the `lab/motion-engines/` experiments or in an application that
does not have the single-file report constraint. Select the engine after selecting the semantic
intent:

| Intent | Useful external tool | What to borrow | Report boundary |
|---|---|---|---|
| `data-transition` | D3 transitions or Motion | Named states and value-safe interpolation. | Keep the completed state in the Canvas shell; do not add a network dependency. |
| `spatial-reordering` | D3 keyed joins | Object constancy through a stable entity key. | Never animate ordinary filtering or unkeyed rows. |
| `narrative-transition` | GSAP timeline or Motion | Explicit step sequencing and scroll-linked state changes. | Each step must remain readable without animation and respect reduced motion. |
| `attention-guidance` | Motion or anime.js | One-shot opacity/transform emphasis. | Do not use stagger, loops, or decorative bounce in a report. |

The external engine is an implementation choice, not a fifth intent. Vendor and pin it only for
the lab or an application; generated reports continue to use the self-contained runtime. Any
experiment must stop or cancel active animations before painting its final state, because external
requestAnimationFrame loops can resume after a capture and overwrite that state.
