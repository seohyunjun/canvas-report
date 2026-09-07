# Motion 11.11.17 — handing animation to the browser

Lab page: [`../02-motion.html`](../02-motion.html) · vendored: `vendor/motion-11.11.17.js` (63 KB)

## What is vendored
| File | Size | Source |
|---|---|---|
| `motion-11.11.17.js` | 63 KB | jsdelivr `motion@11.11.17/dist/motion.js` (UMD, global `Motion`) |

npm ships ESM by default. To use `<script src>` directly from `file://` you need the UMD path above.

## Minimum usage — there are two signatures
```html
<script src="vendor/motion-11.11.17.js"></script>
<script>
  var animate = Motion.animate;
  // (1) element: transform goes to the Web Animations API, off the main thread
  animate('#bar', {scaleX:[0, 0.62]}, {duration:.8, type:'spring', stiffness:120, damping:18});
  // (2) number: from, to, {onUpdate}
  animate(0, 66147, {duration:.95, ease:[.22,.61,.36,1], onUpdate:function(v){ … }});
</script>
```
**Two traps.** The easing key is **`ease`**, not `easing`. And animate **`scaleX`**, not `width` —
`width` forces layout every frame and never reaches WAAPI.

## The pin is two majors behind the site, and says nothing about it
motion.dev documents **13.1.1**; this is **11.11.17**. Most of the surface matches, but the newer
spring option `visualDuration` does not occur anywhere in the pinned file — and passing it raises
nothing, because **Motion does not validate option names**. Neither does it reject a nonsense
easing string. A contract copied from the current docs will run and quietly ignore the part that
does not exist; only `assets/check-motion.py` observing real progress catches it.
[`api-surface.md`](api-surface.md) lists what this build does expose.

## What only this engine does
- **A hardware-accelerated path.** transform and opacity are handed to the browser's own engine.
- **Real spring physics.** `type:'spring'` responds to input velocity instead of replaying a fixed
  curve. This is where it parts company with the shell's fixed `spring` easing.

The shell's `R.motion()` is the **first half** of that (driving WAAPI directly), written by hand.
The physics half is absent, and a report does not need it.

## The safety net you must add yourself
Same as GSAP. Collect the handles `animate()` returns, `stop()` them, then paint the final values.
See the `RUN` array and `stopAll()` in the lab page.

## When to reach for it
Product UI that needs layout transitions and exit animations. Overkill for an analysis document.
