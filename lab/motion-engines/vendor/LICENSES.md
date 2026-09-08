# Vendored third-party runtimes

The files in this directory were **not written by this repository.** Each is a pinned upstream
distribution, retained verbatim, with the attribution redistribution requires recorded below.
How they are fetched and verified: [`fetch.sh`](fetch.sh) and [`SHA256SUMS`](SHA256SUMS).

| File | Package | Version | Licence | Source |
|---|---|---|---|---|
| `gsap-3.15.0.min.js` | gsap | 3.15.0 | **Standard "No Charge" GSAP License** (not MIT) | <https://gsap.com> |
| `gsap-all-3.15.0.min.js` | gsap | 3.15.0 | the same licence; core **plus all 25 plugins** | <https://gsap.com> |
| `motion-11.11.17.js` | motion | 11.11.17 | MIT | <https://motion.dev> |
| `anime-3.2.2.min.js` | animejs | 3.2.2 | MIT | <https://animejs.com> |
| `d3-7.9.0.min.js` | d3 | 7.9.0 | **ISC** | <https://d3js.org> |

## Two licences that are not MIT

**GSAP** is under GreenSock's own terms, and **D3** is ISC (a permissive licence equivalent to
MIT in effect, but a different text — keep D3's own copyright notice with the file).

## GSAP is the exception, and the exception changed

```
/*!
 * GSAP 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license.
 * @author: Jack Doyle, jack@greensock.com
 */
```

That banner is the pinned file's own, copied from it rather than from the site. Two things in it
are worth reading twice.

**It no longer mentions Club GSAP.** The 3.12.5 banner this repository used to pin ended
"or for Club GSAP members, the agreement issued with that membership", because a dozen plugins —
SplitText, MorphSVG, DrawSVG, ScrollSmoother, Inertia and the rest — were paid. Under Webflow the
Standard "No Charge" GSAP License, effective 30 April 2025, made the whole library free for
commercial use, and the bonus plugins went with it. That is why this repository can pin
`all.min.js` at all, and why [`docs/gsap.md`](../docs/gsap.md) can describe every plugin as
reachable rather than as a catalogue of things you would have to buy.

**It is still not MIT.** GSAP remains Webflow's property under its own terms, and the licence
carries a restriction the MIT-licensed runtimes here do not: you may not put GSAP inside a tool
that lets people build animations visually without code, and you may not reverse-engineer it to
build a competitor. Neither bites a report generator, but read
<https://gsap.com/standard-license> yourself rather than taking this paragraph for it.

The other runtime entries keep their upstream notices above. GSAP is retained here for study and
this repository does not resell it. If the terms do not suit you, delete both GSAP lines from
`vendor/fetch.sh` and drop `01-gsap.html`; the other three files and the lab structure are
unaffected, and no generated report depends on GSAP unless a plan names it as a
`vendored-runtime` motion engine.

## Updating
```bash
# after bumping a version in fetch.sh
rm SHA256SUMS && bash fetch.sh     # writes fresh hashes
```
Running it without deleting `SHA256SUMS` rejects a changed file. That is the intended behaviour.
