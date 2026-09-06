#!/usr/bin/env bash
# Vendor the chart and motion runtimes external-tools.md assesses.
#
# These are DELIBERATELY outside the canvas-report output contract: a report ships
# one HTML with zero network requests, and every file below is a network request or
# a build step. They live here so that "when to close this skill" has a worked
# example instead of a sentence.
#
# Versions are pinned. Re-running verifies SHA256 and refuses a changed artefact.
set -euo pipefail
cd "$(dirname "$0")"

fetch() {  # url  filename
  if [[ -f "$2" ]]; then echo "have   $2"; return; fi
  echo "fetch  $2"
  curl -fsSL --retry 2 -m 120 -o "$2.part" "$1"
  mv "$2.part" "$2"
}

fetch https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js                 gsap-3.12.5.min.js
fetch https://cdn.jsdelivr.net/npm/motion@11.11.17/dist/motion.js                    motion-11.11.17.js
fetch https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.2/anime.min.js              anime-3.2.2.min.js
fetch https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js                     d3-7.9.0.min.js

if [[ -f SHA256SUMS ]]; then
  echo "--- verifying ---"; sha256sum -c SHA256SUMS
else
  sha256sum *.js > SHA256SUMS
  echo "--- SHA256SUMS written (first run) ---"; cat SHA256SUMS
fi
