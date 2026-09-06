# Vendored third-party runtimes

The files in this directory were **not written by this repository.** Each is a pinned upstream
distribution, retained verbatim, with the attribution redistribution requires recorded below.
How they are fetched and verified: [`fetch.sh`](fetch.sh) and [`SHA256SUMS`](SHA256SUMS).

| File | Package | Version | Licence | Source |
|---|---|---|---|---|
| `gsap-3.12.5.min.js` | gsap | 3.12.5 | **Standard "no charge" license** (not MIT) | <https://gsap.com> |
| `motion-11.11.17.js` | motion | 11.11.17 | MIT | <https://motion.dev> |
| `anime-3.2.2.min.js` | animejs | 3.2.2 | MIT | <https://animejs.com> |
| `d3-7.9.0.min.js` | d3 | 7.9.0 | **ISC** | <https://d3js.org> |

## Two licences that are not MIT

**GSAP** is under GreenSock's own terms, and **D3** is ISC (a permissive licence equivalent to
MIT in effect, but a different text — keep D3's own copyright notice with the file).

## GSAP is the exception

```
GSAP 3.12.5 · https://gsap.com
@license Copyright 2024, GreenSock. All rights reserved.
Subject to the terms at https://gsap.com/standard-license
or for Club GSAP members, the agreement issued with that membership.
@author: Jack Doyle, jack@greensock.com
```

The other runtime entries keep their upstream notices above. **GSAP is not MIT.** It is retained here
for study, and this repository does not resell GSAP as a product. Check the linked terms yourself
before putting it in a commercial product. If the terms do not suit you, delete that line from
`vendor/fetch.sh` and drop `01-gsap.html`; the other four and the lab structure are unaffected.

## Updating
```bash
# after bumping a version in fetch.sh
rm SHA256SUMS && bash fetch.sh     # writes fresh hashes
```
Running it without deleting `SHA256SUMS` rejects a changed file. That is the intended behaviour.
