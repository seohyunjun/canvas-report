#!/usr/bin/env python3
"""Run progressive post-build gates and persist one validation artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

VERSION = "1.0"
ROOT = Path(__file__).resolve().parent.parent


def diagnostic(identifier: str, location: str, problem: str, fix: str) -> dict[str, str]:
    return {"severity": "error", "id": identifier, "location": location,
            "problem": problem, "suggested_fix": fix}


def run_json(script: str, html: Path) -> tuple[list[dict], int]:
    process = subprocess.run([sys.executable, str(ROOT / "assets" / script), str(html), "--json"],
                             text=True, capture_output=True)
    try:
        payload = json.loads(process.stdout)
        diagnostics = payload.get("diagnostics", [])
        if not isinstance(diagnostics, list):
            raise ValueError("diagnostics is not an array")
    except (json.JSONDecodeError, ValueError) as exc:
        diagnostics = [diagnostic("FINAL-TOOL-001", script, f"Validator returned invalid JSON: {exc}.",
                                  "Run the validator directly and fix its environment or output contract.")]
    if process.returncode != 0 and not diagnostics:
        diagnostics = [diagnostic(
            "FINAL-TOOL-002", script,
            f"Validator exited with status {process.returncode} without a diagnostic.",
            "Run the validator directly and repair its exit/output contract.",
        )]
    return diagnostics, process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a built canvas report through progressive gates.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--skip-motion", action="store_true", help="Allowed only when every chart declares motion.enabled=false.")
    args = parser.parse_args()
    spec_path, html_path = Path(args.spec), Path(args.html)
    phases: dict[str, dict] = {}
    diagnostics: list[dict] = []
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8")); html = html_path.read_text(encoding="utf-8")
        canonical = json.dumps(spec, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        spec_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        static: list[dict] = []
        if f"spec-sha256: {spec_hash}" not in html:
            static.append(diagnostic("FINAL-BUILD-001", str(html_path), "HTML provenance does not match report-spec.json.", "Rebuild HTML from this spec; never patch generated HTML."))
        expected = len(spec.get("charts", [])); actual = len(re.findall(r"<canvas\b", html))
        if actual != expected:
            static.append(diagnostic("FINAL-BUILD-002", str(html_path), f"Expected {expected} generated canvases but found {actual}.", "Rebuild from the validated spec and inspect the builder diagnostics."))
        if re.search(r"<(?:script|link|img)[^>]+(?:src|href)=[\"']https?://", html, re.I):
            static.append(diagnostic("ZERO-NETWORK-001", str(html_path), "HTML contains an external resource URL.", "Inline the resource or remove it from the declarative spec."))
        phases["build"] = {"status": "fail" if static else "pass", "diagnostics": static}; diagnostics.extend(static)
        if not static:
            render, _ = run_json("check-render.py", html_path)
            phases["render"] = {"status": "fail" if render else "pass", "diagnostics": render}; diagnostics.extend(render)
            motion_enabled = any(isinstance(chart, dict) and chart.get("motion", {}).get("enabled") is True for chart in spec.get("charts", []))
            if args.skip_motion and motion_enabled:
                motion = [diagnostic("MOTION-SKIP-001", "--skip-motion", "Motion validation was skipped although enabled motion exists.", "Run without --skip-motion.")]
            elif not motion_enabled:
                motion = []
            else:
                motion, _ = run_json("check-motion.py", html_path)
            phases["motion"] = {"status": "fail" if motion else "pass", "diagnostics": motion}; diagnostics.extend(motion)
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(diagnostic("FINAL-INPUT-001", "validate-report", str(exc), "Provide readable matching report-spec.json and HTML files."))
        phases["input"] = {"status": "fail", "diagnostics": diagnostics[:]}
    result = {"schema_version": VERSION, "status": "fail" if diagnostics else "pass",
              "spec_sha256": hashlib.sha256(spec_path.read_bytes()).hexdigest() if spec_path.is_file() else None,
              "html_sha256": hashlib.sha256(html_path.read_bytes()).hexdigest() if html_path.is_file() else None,
              "phases": phases, "diagnostics": diagnostics}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
