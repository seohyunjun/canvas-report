# GSAP 3.15.0 — every plugin, and what a report may do with them

Lab page: [`../01-gsap.html`](../01-gsap.html) · vendored: `vendor/gsap-3.15.0.min.js` (72 KB) and
`vendor/gsap-all-3.15.0.min.js` (325 KB)

## What is vendored

| File | Size | Source | Contains |
|---|---|---|---|
| `gsap-3.15.0.min.js` | 72 KB | cdnjs `gsap/3.15.0/gsap.min.js` | the core only — **no plugins** |
| `gsap-all-3.15.0.min.js` | 325 KB | cdnjs `gsap/3.15.0/all.min.js` | the core **plus all 24 plugin files** |

Two files, because the two uses are different. A report that names `gsap` as a `vendored-runtime`
motion engine inlines the **core**, and inlining 325 KB into an offline document to run one entry
tween would be indefensible. The lab page is where the plugins are exercised, and the lab is
[deliberately outside the report contract](../vendor/fetch.sh).

**This changed with the pin.** The previous pin was 3.12.5, and at that version cdnjs carried
**12** plugin files: the bonus set — SplitText, MorphSVG, DrawSVG, ScrollSmoother, Inertia,
ScrambleText, Physics2D, PhysicsProps, GSDevTools, MotionPathHelper, CustomWiggle, CustomBounce —
was Club GSAP and was not publicly distributable. From **3.13.0** onward all **24** are on the CDN,
and `all.min.js` appears alongside them. Webflow's Standard "No Charge" GSAP License of
30 April 2025 is what made that possible; [`../vendor/LICENSES.md`](../vendor/LICENSES.md) records
the terms and the one restriction that still applies.

## Loading a plugin is not registering it

This is the part the site's install snippets make look automatic, and it is the first thing that
bites. Measured on the pinned `all.min.js`, in a headless browser, with and without a
`gsap.registerPlugin()` call:

| Check | Core file | All file, loaded | All file, **registered** |
|---|---|---|---|
| plugin names on `window` | 1 (`gsap`) | **27** | 27 |
| `Object.keys(gsap.plugins)` | 6 | **6** | **18** |
| `gsap.core.globals()` entries | 29 | **29** | **48** |
| `gsap.parseEase('rough' / 'slow' / 'expoScale(1,2)')` | fails | **fails** | resolves |
| `CustomEase.create(...)` as an ease | fails | resolves | resolves |

Three things follow.

**`gsap.plugins` is not the check.** It holds six built-in property plugins — `attr`, `css`,
`endArray`, `modifiers`, `roundProps`, `snap` — in the bare core and in the full bundle alike. It
only grows when you register, and even then it reaches 18, not 27, because two thirds of the set
are not property plugins at all. The check that actually answers "is this plugin here" is the
**window global**.

**Loading the bundle animates nothing extra.** Twenty-seven names appear on `window` and GSAP does
not know about any of them until `gsap.registerPlugin()` is called. The eases prove it: `rough`,
`slow` and `expoScale` are in the file, and `gsap.parseEase` refuses all three until EasePack is
registered.

**The ease plugins are the exception, in one direction.** `CustomEase`, `CustomWiggle` and
`CustomBounce` work unregistered, because they do not extend the tween — they mint a named ease and
hand it back. Registering them is still the documented call and costs nothing.

```html
<script src="vendor/gsap-all-3.15.0.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin, MorphSVGPlugin, SplitText, EasePack);
  // …or, when you genuinely want the lot:
  // gsap.registerPlugin(...[ScrollTrigger, ScrollSmoother, /* … */].filter(Boolean));
</script>
```

## The catalogue

Every plugin in the pinned bundle, grouped as <https://gsap.com/docs/v3/Plugins> groups them. **Kind**
is measured, not read off the site: *property* plugins appear in `gsap.plugins` once registered and
extend what a tween can write to; *behaviour* plugins add their own object or method; *ease* plugins
add curves. **Here** is the verdict for this skill, in the vocabulary
[`references/motion-features.md`](../../../references/motion-features.md) uses.

### Scroll

| Plugin | Kind | What it does | Here |
|---|---|---|---|
| `ScrollTrigger` | behaviour | starts, scrubs and pins an animation against scroll position | **shell.** The report contract allows one trigger, `on-view`, and the shell's `onView()` already fires it from an IntersectionObserver. ScrollTrigger would replace 30 lines with 44 KB. |
| `ScrollSmoother` | behaviour | replaces native scrolling with an interpolated one | **refused.** It takes over the scrollbar. A report is a document; hijacking the reader's scroll to make it feel expensive is the definition of what [`anti-patterns.md`](../../../references/anti-patterns.md) calls a generated screen. |
| `ScrollToPlugin` | property | tweens `window.scrollTo` / an element's scroll offset | **shell.** The methodology links and the table twins scroll with the browser's own `scroll-behavior`. |

### Text

| Plugin | Kind | What it does | Here |
|---|---|---|---|
| `SplitText` | behaviour | splits an element into per-character, per-word or per-line spans | **refused.** Report headings are claims. Animating a claim letter by letter draws the eye to the typography and away from the number the sentence carries. |
| `ScrambleTextPlugin` | property | scrambles characters while tweening to a new string | **refused.** Same reason, plus a figure mid-scramble is a wrong number on screen. |
| `TextPlugin` | property | replaces text content over time | **shell.** `R.countUp()` animates a figure to its value and lands on the formatted string; that is the only text a report has cause to move. |

### SVG

| Plugin | Kind | What it does | Here |
|---|---|---|---|
| `DrawSVGPlugin` | property | animates an SVG stroke's dash so the path draws itself | **held.** The nearest thing a report does is `VIZ.line`'s reveal, which draws on canvas by point count and needs no path. If a report ever ships an SVG diagram, this is the plugin for it. |
| `MorphSVGPlugin` | property | morphs one SVG path into another, matching points | **held**, for the same reason. Nothing in the chart vocabulary is an SVG path. |
| `MotionPathPlugin` | property | moves an element along a path, optionally auto-rotating | **held.** A legitimate chart use exists — a mark travelling a computed route — and no lens asks for one. |
| `MotionPathHelper` | behaviour | an in-page editor for tuning a motion path | **refused.** An authoring tool. It has no place in a generated artifact. |

### UI

| Plugin | Kind | What it does | Here |
|---|---|---|---|
| `Flip` | behaviour | records DOM state, lets you change it, then animates the difference | **refused.** Flip exists for layout that rearranges. A report's filters redraw rather than reflow, deliberately: [`motion.md`](../../../references/motion.md) requires a filter to redraw immediately rather than imply continuity between two different populations. |
| `Draggable` | behaviour | makes an element draggable, with bounds and snapping | **refused.** An application affordance. Nothing in a report is the reader's to move. |
| `InertiaPlugin` | property | continues a drag with momentum and lands on a snap point | **refused.** It exists to finish what Draggable starts. |
| `Observer` | behaviour | one normalised listener for wheel, touch, pointer and scroll | **shell.** The tooltip engine binds `pointermove`, `pointerdown` and `keydown` directly, and the whole surface is two dozen lines. |

### Physics and integrations

| Plugin | Kind | What it does | Here |
|---|---|---|---|
| `Physics2DPlugin` | property | velocity, angle, gravity and friction on a mark | **refused.** A chart mark's position is a value. Giving it gravity says something about the data that the data does not say. |
| `PhysicsPropsPlugin` | property | the same, per arbitrary property | **refused**, identically. |
| `EaselPlugin` | property | tweens EaselJS / CreateJS display objects | **n/a.** This repository draws with the canvas 2D context directly and loads no scene graph. |
| `PixiPlugin` | property | tweens PixiJS display objects | **n/a**, identically — and Pixi is WebGL, which a zero-network offline document has no reason to carry. |
| `CSSRulePlugin` | property | tweens a stylesheet rule, reaching pseudo-elements | **refused.** The themes are CSS custom properties resolved at draw time ([`themes.md`](../../../references/themes.md)); animating a rule would fight the theme toggle. |
| `GSDevTools` | behaviour | a scrub bar over any animation, for development | **refused** in output, **useful in the lab.** It is a authoring instrument; a generated report must not ship one. |

### Eases

| Plugin | Kind | What it does | Here |
|---|---|---|---|
| `CustomEase` | ease | any cubic-bezier path as a named ease | **held, and the closest of all of them.** It would work unregistered and it is value-safe. What blocks it is the plan contract, not the engine: `assets/validate-plan.py` takes seven easing names by enum, and a curve nobody can name is a curve no gate can check. |
| `EasePack` (`RoughEase`, `SlowMo`, `ExpoScaleEase`) | ease | jittered, hold-the-middle and scale-compensated curves | **refused.** `RoughEase` adds noise to a progress value; on a value-scaled mark that is a number wobbling around its datum. |
| `CustomWiggle` | ease | oscillates a set number of times before settling | **refused**, same reason. |
| `CustomBounce` | ease | a bounce with a matching squash-and-stretch curve | **refused.** A bar that overshoots its value and returns has, for those frames, drawn a number the data does not contain. |

### Framework

| | | | |
|---|---|---|---|
| `useGSAP()` | React hook | scopes and cleans up GSAP inside a React component | **n/a.** The builder emits one HTML file with no framework, and it is not in the bundle — it ships as `@gsap/react`. |

**Nothing in that table is missing from the pin.** Every *refused* and *held* above is a decision
about what a report should do, not a report of what the file lacks — which is the opposite of the
position this document was in at 3.12.5, when half the catalogue was simply not there to refuse.

## What only this engine does

**The timeline.** Unlike things — bars, per-row numbers, a total — placed on one shared axis at
absolute or relative positions. Relative offsets (`-=0.35`), nested timelines, `timeScale()` on the
whole sequence. If thirty things must move in order against a scrollbar, nothing else comes close.

```html
<script src="vendor/gsap-3.15.0.min.js"></script>
<script>
  var tl = gsap.timeline({defaults:{duration:.75, ease:'power3.out'}});
  tl.to('#bar1', {width:'62%'}, 0)        // absolute time 0s
    .to('#bar2', {width:'31%'}, 0.09)     // absolute time 0.09s
    .to(obj, {t:66147, onUpdate:paint}, 0);
</script>
```

The shell's `chart.play(dur, easing)` drives **one progress value for one chart**. It cannot
compose. That is the only thing it lacks, and in a report it is fine to lack it.

## Taken / refused by this skill

- **Taken:** the named easing catalogue. It is twenty lines when you only need the curves —
  the shell's nine `easings` are exactly that ([`motion.md`](../../../references/motion.md)).
- **Refused:** the 72 KB runtime for the portable path, and choreography itself. A report may move
  in four places only, none of which sequences one animation after another, which leaves a timeline
  nothing to do. The plugins are refused one at a time in the catalogue above, and the reasons are
  about the document rather than about the engine.

## The safety net you must add yourself

GSAP **freezes mid-frame when rAF stops** — background tab, headless capture, low-power mode; all
of these happen. The shell guarantees the final state with `setTimeout(finish, dur+260)` and a
token inside `anim()`. GSAP does not do this for you. See `stopAll()` + `paintFinal()` in the lab
page: **painting the final value is not enough**, you must `kill()` the running tweens first or a
late frame overwrites it.

This applies to the plugins too, and to some of them harder. A `ScrollTrigger` that never reaches
its end because the page was captured at 1280×800 leaves its animation part-played, and
`MOTION-FINAL-STATE-001` is not a suggestion.

## When to reach for it

[`external-tools.md`](../../../references/external-tools.md) § When to close this skill — when the
deliverable is an **application** rather than a document, or when thirty things must be
choreographed against scroll. Not for an analysis document.

If you are here because you want one plugin and nothing else: take
`gsap-3.15.0.min.js` plus that plugin's own file from
`https://cdnjs.cloudflare.com/ajax/libs/gsap/3.15.0/<Plugin>.min.js`, add both to
[`../vendor/fetch.sh`](../vendor/fetch.sh), delete `SHA256SUMS` and re-run it. `all.min.js` is the
convenience, not the requirement.

## Reproducing the measurements on this page

```bash
python3 lab/motion-engines/probe-api.py --output lab/motion-engines/docs/api-surface.json
python3 lab/motion-engines/probe-api.py --expect lab/motion-engines/docs/api-surface.json
```

The counts in *Loading a plugin is not registering it* come from that probe, which loads the pinned
files in a headless browser and reads their surface rather than the site's.
