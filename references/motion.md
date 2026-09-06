# Motion — why the canvas moves

Reports from this skill move. But **movement that carries no information is noise.**
There are exactly four places where canvas animation earns its cost.

| Place | Why |
|---|---|
| **The waterfall's flow** (08 Bridge) | value moving from opening to closing *is* the claim |
| **Scroll transitions** (03 Scrollytelling) | on one coordinate system, the eye tracks the change directly |
| **Play once on entry** | watching a chart draw makes the axis and the baseline register first |
| **A re-sort of the same marks** | the mark that moved *is* the information — see below |

Everything else — looping, hover zoom, colour pulses, staggered entrances — gets deleted.

## The fourth place: re-sorting, and only re-sorting

Give `VIZ.hbars` or `VIZ.lollipop` a `cfg.key` and a `chart.play(420)` after a sort change makes
each mark **travel** from the row it held to the row it now belongs in, rather than regrowing from
zero. The reader follows one series through the reorder instead of re-reading every label. That
property is called **object constancy**; it is D3's, ported without the runtime
([`external-tools.md`](external-tools.md) § What was actually adopted).

```js
var c = VIZ.hbars(canvas, { rows: current, label:'k', value:'v', key:'k' });
sortBtn.onclick = function(){ order = 'value'; c.play(420); };   // marks travel
filterBtn.onclick = function(){ drop = true;   R.paintAll(); };  // marks vanish: no animation
```

**The bound is strict, because the failure is a lie.** Movement here claims "this is the same
thing, somewhere else". Animate a change where that is false and the animation asserts something
untrue:

- **A re-sort only.** The same marks, reordered. Rows may change value at the same time.
- **Never a filter.** If marks appear or disappear, the survivors' travel implies a continuity the
  data does not have, and `motion.md`'s own duration table still says a filter redraws in **0ms**.
  A row with no previous position fades in rather than sliding from nowhere.
- **Never without a key.** With no `cfg.key` the factory falls back to growing from zero, which is
  the honest default. A key that is not stable — an array index, a formatted string that changes —
  makes marks swap identities mid-flight, which is worse than no animation at all.
- **≤ 420ms**, like a scroll step. A sort control is a control.

## Absolute rules

1. **The animation always ends.** Even when rAF stops (background tab, headless capture) the
   final state must be drawn. The shell's `anim()` and `countUp()` do this with a safety timer.
   Any new factory must do the same.
2. **The final state holds all the information.** Nobody who misses the animation — print,
   screenshot, reduced-motion — may lose anything.
3. **`prefers-reduced-motion` means omit, not slow down.** The shell handles it globally; check
   `R.reduced()` for anything you add.
4. **Play once.** `R.onView` does not replay on re-entry. If a replay is genuinely useful, give
   the reader a button.

## Easing

The named-curve catalogue is the portable half of GSAP, Motion and anime.js — you do not need
their runtimes to use their curves. The shell ships nine, split by whether they are legal on a
mark whose size *is* the value.

| Value-safe — monotonic, never exceeds 1 | Overshoot — passes 1 before settling |
|---|---|
| `linear` `outCubic` (default) `inOutCubic` `outQuint` `outExpo` `outCirc` `inOutQuint` | `outBack` `spring` |

**The split is enforced.** A chart's progress `t` scales the data, so an overshoot curve draws a
bar past its own axis for a few frames — that is slop-test gate 3, a mark outside the plot.
`anim()` refuses an overshoot easing on a chart, warns in the console and falls back to `outCubic`.

They are legal wherever nothing is scaled to an axis:

```js
chart.play(700, 'outExpo');                        // fine
chart.play(700, 'spring');                         // refused + warned
R.countUp(el, 1024, 900, R.compact, 'spring');     // fine — a number is not a mark
R.motion(node, {opacity:1}, {duration:300, easing:'outBack'});   // fine
```

Reach past the default only for a reason you can name. Nine curves is a vocabulary, not a menu to
graze; a report that uses six of them is decorated, not designed.

## Durations

| Target | Time | Easing |
|---|---|---|
| chart entry | 600–900ms | `1-(1-t)³` (shell default) |
| scroll step transition | ≤ 420ms | same |
| re-sort of the same marks | ≤ 420ms | same |
| figure count-up | 700–900ms | same |
| `.reveal` element | 480ms | `cubic-bezier(.22,.61,.36,1)` |
| redraw after a filter change | **0ms** | a control must respond instantly |

## What the shell gives you

```js
R.reveal();                          // switch .reveal elements on once, as they enter view
R.countUp(el, 1024, 900, R.compact, 'outCubic');  // a number. Final value under reduced motion
R.onView(node, function(){ … });     // once, when it enters the viewport
R.scrolly(container, function(i){ … });  // .step activates -> repaint the pinned canvas
R.shrinkMasthead(el, 140);           // M6 sticky shrink
chart.play(700, 'outExpo');          // any VIZ handle; value-safe easings only
// hbars / lollipop with cfg.key: play() after a re-sort makes marks travel
R.motion(node, frames, opts);        // Web Animations, opacity + small translate only
R.easings                            // the nine curves, if you need one directly
R.reduced();                         // true -> do not build the animation at all
```

## Do not

- **Loading skeletons.** The data is already in the file. Do not act out a wait that is not happening.
- **Staggered entrances.** Six cards rising in sequence delays reading six times.
- **Hover zoom on a mark.** The hit target moves, so aiming at the next mark gets harder.
  Emphasise with a **ring**, the way the shell does.
- **Endless particle loops.** Play once and stop.
- **Scroll hijacking.** `scroll-snap` is the ceiling. Never take the scroll with `scrollTo`.
