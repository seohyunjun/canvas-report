# anime.js 3.2.2 — features per byte, and the banned stagger

Lab page: [`../03-anime.html`](../03-anime.html) · vendored: `vendor/anime-3.2.2.min.js` (17 KB)

## What is vendored
| File | Size | Source |
|---|---|---|
| `anime-3.2.2.min.js` | **17 KB** | cdnjs `animejs/3.2.2/anime.min.js` |

The smallest of the five: a quarter of GSAP, a eighteenth of Lottie, an eighty-third of Rive.

## Minimum usage
```html
<script src="vendor/anime-3.2.2.min.js"></script>
<script>
  anime({targets:'.bar', width:function(el){ return el.dataset.w+'%'; },
         duration:750, easing:'easeOutCubic', delay:anime.stagger(90)});
  anime({targets:obj, t:66147, duration:900, easing:'easeOutCubic',
         update:function(){ paint(obj.t); }});
</script>
```

## Its signature — and the thing this skill bans
`anime.stagger()` distributes delay for you: by time, by value, even by **grid position**. It is
the most developed stagger utility of the three engines.

canvas-report **forbids the effect**.

> Six cards rising in sequence delays reading six times. — `references/motion.md` § Do not

The lab page shows it anyway, deliberately. Five bars grow 90 ms apart. It looks good. It also
costs anyone reading the fifth value 360 ms. Put it on the thirty-one cells of the poster report
and that becomes 2.7 seconds.

## What this skill took
**Almost nothing, deliberately.** Only the modular instinct — the shell's motion surface is five
small functions (`reveal` `countUp` `onView` `scrolly` `motion`), not an engine.

## The safety net you must add yourself
anime freezes when rAF stops, and **a late frame overwrites the value you painted afterwards.**
This page is where that was actually observed: with only a settle timer, four of five bars snapped
back to 0%. Call `anime.remove(targets)` first, then paint. The shell blocks the same race with
`c.__token`.

## When to reach for it
Product UI on a tight byte budget. If you would not use stagger, most of the reason to reach for
it disappears too.

## Motion decision

Use only a validated `data-transition`, `narrative-transition`, or one-time `attention-guidance`
intent. Staggering is not an intent; when it adds no analytical meaning, use the static fallback.
