# GSAP 3.12.5 — timelines and choreography

Lab page: [`../01-gsap.html`](../01-gsap.html) · vendored: `vendor/gsap-3.12.5.min.js` (72 KB)

## What is vendored
| File | Size | Source |
|---|---|---|
| `gsap-3.12.5.min.js` | 72 KB | cdnjs `gsap/3.12.5/gsap.min.js` |

The plugins (ScrollTrigger, MorphSVG, DrawSVG, SplitText, Draggable) are **not** vendored.
Add a line to `vendor/fetch.sh` and regenerate `SHA256SUMS` if you need one.

## Minimum usage
```html
<script src="vendor/gsap-3.12.5.min.js"></script>
<script>
  var tl = gsap.timeline({defaults:{duration:.75, ease:'power3.out'}});
  tl.to('#bar1', {width:'62%'}, 0)        // absolute time 0s
    .to('#bar2', {width:'31%'}, 0.09)     // absolute time 0.09s
    .to(obj, {t:66147, onUpdate:paint}, 0);
</script>
```

## What only this engine does
**The timeline.** Unlike things — bars, per-row numbers, a total — placed on one shared axis at
absolute or relative positions. Relative offsets (`-=0.35`), nested timelines, `timeScale()` on the
whole sequence. If thirty things must move in order against a scrollbar, nothing else comes close.

The shell's `chart.play(dur, easing)` drives **one progress value for one chart**. It cannot
compose. That is the only thing it lacks, and in a report it is fine to lack it.

## Taken / refused by this skill
- **Taken:** the named easing catalogue. It is twenty lines when you only need the curves —
  the shell's nine `easings` are exactly that (`references/motion.md`).
- **Refused:** the 72 KB runtime, and choreography itself. A report may move in four places only
  (`references/motion.md`), none of which sequences one animation after another, which leaves a
  timeline nothing to do.

## The safety net you must add yourself
GSAP **freezes mid-frame when rAF stops** — background tab, headless capture, low-power mode; all
of these happen. The shell guarantees the final state with `setTimeout(finish, dur+260)` and a
token inside `anim()`. GSAP does not do this for you. See `stopAll()` + `paintFinal()` in the lab
page: **painting the final value is not enough**, you must `kill()` the running tweens first or a
late frame overwrites it.

## When to reach for it
`references/external-tools.md` § When to close this skill — when the deliverable is an
**application** rather than a document, or when thirty things must be choreographed against
scroll. Not for an analysis document.
