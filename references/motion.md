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

## What must actually be wired

The four places above are where motion is *allowed*. This is what a report must *do*, and the
gap between the two is where reports go wrong: every audited report before this rule declared the
motion vocabulary and then wired one chart out of five.

**Play-once-on-entry is the default, not an extra.** The last line of the wiring block reads:

```js
R.wireHelp(); R.wireToggles(); R.reveal(); R.paintAll(); R.playAll(700);
```

`R.playAll()` walks every chart the page has built and gives it play-once-on-entry. It is
opt-**out**: a chart that must not move is declared static at construction and the reason goes in
the methodology.

```js
V.line(cvs, {rows: …, static:true});   // and say why, in the methodology
```

**"It is a small chart in a column" is not a reason.** Nor is "it is not the lead". Those are
the excuses that produced 9 animated charts out of 27. A chart is static because moving it would
mislead — an axis it shares with a neighbour that does not move, a mark whose growth reads as a
trend it does not have — or it is not static.

Beyond the default:

- A **hero figure** counts up (`R.countUp`). A number rendered flat while the chart under it
  draws itself looks broken.
- A **ranking with a stable identity** gets `cfg.key` and a re-sort control. If you write
  `key:'k'` and never ship a control that re-sorts, the key is dead code and the fourth place
  is unused.
- **03 Scrollytelling** must call `R.scrolly`; it is the macro's whole premise.

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
R.playAll(700);                      // play-once-on-entry for every chart. The default.
R.reduced();                         // true -> do not build the animation at all
```

## Verifying it moved

**A screenshot cannot answer this, and neither can the browser check in
[`slop-test.md`](slop-test.md).** That check passes `--force-prefers-reduced-motion`, which omits
the animation on purpose, and `--virtual-time-budget`, which freezes `requestAnimationFrame`
outright — under virtual time a chart's progress reads one constant value forever, so a trace
taken there shows a stuck animation whether or not one exists.

Motion is verified on a real clock:

```bash
python3 assets/check-motion.py report.html
```

It drives Chrome over the DevTools protocol, scrolls the page as a reader would, and reports per
chart whether anything played it on entry and whether it landed on its final state. It exits
non-zero if a chart never moves. Run it before the stamp.

## Do not

- **Loading skeletons.** The data is already in the file. Do not act out a wait that is not happening.
- **Staggered entrances.** Six cards rising in sequence delays reading six times.
- **Hover zoom on a mark.** The hit target moves, so aiming at the next mark gets harder.
  Emphasise with a **ring**, the way the shell does.
- **Endless particle loops.** Play once and stop.
- **Scroll hijacking.** `scroll-snap` is the ceiling. Never take the scroll with `scrollTo`.
