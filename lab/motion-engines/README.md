# Motion-engine lab — what is on the other side of closing the skill

`references/external-tools.md` routes reports through selected chart and motion tools. The normal
report path adopts portable patterns through the shipped runtime; this directory demonstrates the
actual vendored runtimes for the rarer case where a compatible builder deliberately inlines one.

## These are not reports

canvas-report ships **one HTML file with zero network requests**. The four pages here break that
contract **on purpose**. Do not mistake them for reports and do not add them to
`.canvas-report/log.json`.

| | The shell (a report) | This lab |
|---|---|---|
| Network requests | 0 | 1–3 |
| Weight | 100 KB, everything included | see the table below |
| Final state guaranteed | yes — timer + token inside `anim()` | **you have to add it** |

## The four pages

| # | Page | Engine | Vendored | One line |
|---|---|---|---|---|
| 1 | [01-gsap.html](01-gsap.html) | GSAP 3.15.0 | 325 KB | timelines — unlike things on one shared axis; loads the all-plugin bundle and reports what registering actually changes |
| 2 | [02-motion.html](02-motion.html) | Motion 11.11.17 | 63 KB | hands transforms to WAAPI; real spring physics |
| 3 | [03-anime.html](03-anime.html) | anime.js 3.2.2 | **17 KB** | stagger — the exact effect this skill bans |
| 6 | [06-d3.html](06-d3.html) | D3 7.9.0 | 280 KB | the keyed join — marks travel instead of being relabelled |

Page 6 is the odd one: D3 is a **chart-form vocabulary** (`external-tools.md` § A), not a motion
engine. It sits here because the thing worth showing about D3 *is* its transitions, and because
this is where vendored runtimes live.

One doc per tool in [`docs/`](docs/), plus
[`docs/api-surface.md`](docs/api-surface.md) — what the pinned runtimes actually expose, versus what
their sites document today. `python3 probe-api.py --expect docs/api-surface.json` re-reads the
bundles offline and fails on drift. All four pages animate **the same data**
(`lab-data.js` — the five parts of ₩66,147 of GCP spend, July 2026) in **the same layout**, so
that only the engine differs.

## Setup

```bash
bash vendor/fetch.sh        # pinned download + SHA256 verification
```

`vendor/` is already populated. Re-running `fetch.sh` only verifies that nothing changed.
Third-party licences and attribution: [`vendor/LICENSES.md`](vendor/LICENSES.md) —
note that **GSAP is the one item that is not MIT**.

## What the lab actually taught

**None of the four runtimes with a JS animation loop guarantees a final state.** When rAF stops — background tab, headless
capture, low-power mode — they freeze mid-frame. This was reproduced during headless verification.
Worse: **painting the final value is not enough**, because a frame that wakes up late writes over
it. On the anime.js page four of five bars snapped back to 0%.

The shell blocks both with `setTimeout(finish, dur+260)` and `c.__token` inside `anim()`.
These engines do not. The `stopAll()` + `paintFinal()` pattern in every page is the minimum you
have to write yourself. D3 adds two of its own: `.interrupt()` cancels a transition **without**
running its `.remove()`, and `.duration(0)` is still a transition that needs a frame to land.

## When you select a vendored runtime

Use the real runtime only when the requested behavior cannot be expressed as a portable pattern:
the deliverable behaves like an **application** · someone must brush, zoom and re-query · the
artefact needs a **designed explanatory animation** · the data is geographic, hierarchical or a
network.

If none of those cases is true, the additional runtime weight is decoration.
