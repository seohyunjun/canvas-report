# Motion — why the canvas moves

Reports from this skill move. But **movement that carries no information is noise.**
There are exactly three places where canvas animation earns its cost.

| Place | Why |
|---|---|
| **The waterfall's flow** (08 Bridge) | value moving from opening to closing *is* the claim |
| **Scroll transitions** (03 Scrollytelling) | on one coordinate system, the eye tracks the change directly |
| **Play once on entry** | watching a chart draw makes the axis and the baseline register first |

Everything else — looping, hover zoom, colour pulses, staggered entrances — gets deleted.

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

## Durations

| Target | Time | Easing |
|---|---|---|
| chart entry | 600–900ms | `1-(1-t)³` (shell default) |
| scroll step transition | ≤ 420ms | same |
| figure count-up | 700–900ms | same |
| `.reveal` element | 480ms | `cubic-bezier(.22,.61,.36,1)` |
| redraw after a filter change | **0ms** | a control must respond instantly |

## What the shell gives you

```js
R.reveal();                          // switch .reveal elements on once, as they enter view
R.countUp(el, 1024, 900, R.compact); // a number. Jumps to the final value under reduced motion
R.onView(node, function(){ … });     // once, when it enters the viewport
R.scrolly(container, function(i){ … });  // .step activates -> repaint the pinned canvas
R.shrinkMasthead(el, 140);           // M6 sticky shrink
chart.play(700);                     // any VIZ handle
R.reduced();                         // true -> do not build the animation at all
```

## Do not

- **Loading skeletons.** The data is already in the file. Do not act out a wait that is not happening.
- **Staggered entrances.** Six cards rising in sequence delays reading six times.
- **Hover zoom on a mark.** The hit target moves, so aiming at the next mark gets harder.
  Emphasise with a **ring**, the way the shell does.
- **Endless particle loops.** Play once and stop.
- **Scroll hijacking.** `scroll-snap` is the ceiling. Never take the scroll with `scrollTo`.
