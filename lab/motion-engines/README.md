# Motion-engine lab — what is on the other side of closing the skill

`references/external-tools.md` assesses five motion tools and **refuses all five as
dependencies**. The refusal is right, but that page carried no worked example of *"and if you do
reach for the real thing, then what?"* This directory is that missing half.

## These are not reports

canvas-report ships **one HTML file with zero network requests**. The five pages here break that
contract **on purpose**. Do not mistake them for reports and do not add them to
`.canvas-report/log.json`.

| | The shell (a report) | This lab |
|---|---|---|
| Network requests | 0 | 1–3 |
| Weight | 100 KB, everything included | see the table below |
| Final state guaranteed | yes — timer + token inside `anim()` | **you have to add it** |

## The six pages

| # | Page | Engine | Vendored | One line |
|---|---|---|---|---|
| 1 | [01-gsap.html](01-gsap.html) | GSAP 3.12.5 | 72 KB | timelines — unlike things on one shared axis |
| 2 | [02-motion.html](02-motion.html) | Motion 11.11.17 | 63 KB | hands transforms to WAAPI; real spring physics |
| 3 | [03-anime.html](03-anime.html) | anime.js 3.2.2 | **17 KB** | stagger — the exact effect this skill bans |
| 4 | [04-lottie.html](04-lottie.html) | lottie-web 5.12.2 | 306 KB | replays a baked clip; takes no data at runtime |
| 5 | [05-rive.html](05-rive.html) | @rive-app/canvas 2.21.6 | 219 KB + **1.2 MB wasm** | state machines; the asset only comes from the editor |
| 6 | [06-d3.html](06-d3.html) | D3 7.9.0 | 280 KB | the keyed join — marks travel instead of being relabelled |

Page 6 is the odd one: D3 is a **chart-form vocabulary** (`external-tools.md` § A), not a motion
engine. It sits here because the thing worth showing about D3 *is* its transitions, and because
this is where vendored runtimes live.

One doc per tool in [`docs/`](docs/). All six pages animate **the same data**
(`lab-data.js` — the five parts of ₩66,147 of GCP spend, July 2026) in **the same layout**, so
that only the engine differs.

## Setup

```bash
bash vendor/fetch.sh        # pinned download + SHA256 verification
python3 make-lottie.py      # regenerate assets/july.json (optional)
```

`vendor/` is already populated. Re-running `fetch.sh` only verifies that nothing changed.
Third-party licences and attribution: [`vendor/LICENSES.md`](vendor/LICENSES.md) —
note that **GSAP is the one item that is not MIT**.

Pages 04 and 05 use `fetch()`. From `file://` a browser needs
`--allow-file-access-from-files`; without it 04 shows an empty frame and 05 shows its notice.
Serving the directory (`python3 -m http.server`) avoids the issue.

## What the lab actually taught

**None of the four runtimes with a JS animation loop guarantees a final state.** When rAF stops — background tab, headless
capture, low-power mode — they freeze mid-frame. This was reproduced during headless verification.
Worse: **painting the final value is not enough**, because a frame that wakes up late writes over
it. On the anime.js page four of five bars snapped back to 0%.

The shell blocks both with `setTimeout(finish, dur+260)` and `c.__token` inside `anim()`.
These engines do not. The `stopAll()` + `paintFinal()` pattern in every page is the minimum you
have to write yourself. D3 adds two of its own: `.interrupt()` cancels a transition **without**
running its `.remove()`, and `.duration(0)` is still a transition that needs a frame to land.

## When you cross over

Straight from `references/external-tools.md` § When to close this skill:
the deliverable is an **application**, not a document · someone must brush, zoom and re-query ·
the artefact is a **designed animation** · the data is geographic, hierarchical or a network.

If none of those four is true, the 2.1 MB in here is decoration.

## Applying the lab to an application

1. Choose one semantic intent in `references/motion-decision.md`.
2. Select an engine whose strength matches that intent; do not choose an effect first.
3. Keep the static fallback and reduced-motion path equivalent to the animated final state.
4. Cancel active engine handles before teardown, capture, or a replacement transition.

The lab deliberately demonstrates external runtimes without making them dependencies of generated
reports. Copy the decision discipline and final-state safeguards, not the vendor bundles.
