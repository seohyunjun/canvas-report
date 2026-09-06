#!/usr/bin/env python3
"""Create and advance a hash-bound canvas-report run state.

Examples:
  python3 assets/report-state.py init --run-dir RUN --input data.csv --output report.html
  python3 assets/report-state.py advance --run-dir RUN --state PROFILED --artifact RUN/profile.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = "1.0"
STATES = ("INIT", "PROFILED", "VALIDATED", "PLANNED", "BUILT", "VERIFIED", "COMPLETE")
ARTIFACT_NAMES = {
    "PROFILED": "profile.json",
    "VALIDATED": "plan.json",
    "PLANNED": "report-spec.json",
    "BUILT": "report.html",
    "VERIFIED": "validation.json",
}
RETRY_STEPS = ("Local Fix", "Component Rebuild", "Simplify", "Drop Unsupported Section")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(status: str, diagnostics: list[dict], manifest: dict | None = None) -> None:
    result = {"schema_version": VERSION, "status": status, "diagnostics": diagnostics}
    if manifest is not None:
        result["run"] = manifest
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def error(identifier: str, location: str, problem: str, fix: str) -> dict[str, str]:
    return {"severity": "error", "id": identifier, "location": location,
            "problem": problem, "suggested_fix": fix}


def verify_recorded_inputs(manifest: dict) -> list[dict[str, str]]:
    diagnostics = []
    records = [("input", manifest.get("input"))]
    records.extend(
        (f"artifacts.{state}", record)
        for state, record in manifest.get("artifacts", {}).items()
    )
    for location, record in records:
        if not isinstance(record, dict):
            diagnostics.append(error(
                "STATE-010", location, "Recorded hash metadata is missing.",
                "Restart from the earliest artifact whose provenance cannot be verified.",
            ))
            continue
        path = Path(record.get("path", ""))
        expected = record.get("sha256")
        if not path.is_file():
            diagnostics.append(error(
                "STATE-011", location, f"Recorded file no longer exists: {path}.",
                "Restore the recorded file or retry from the state that produces it.",
            ))
        elif not isinstance(expected, str) or digest(path) != expected:
            diagnostics.append(error(
                "STATE-012", location, f"Recorded file changed after its state passed: {path}.",
                "Run report-state.py retry from the earliest changed state and regenerate downstream artifacts.",
            ))
    return diagnostics


def atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def initialize(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    manifest_path = run_dir / "run.json"
    source = Path(args.input).resolve()
    if manifest_path.exists():
        emit("fail", [error("STATE-001", str(manifest_path), "Run already exists.", "Resume this run or choose a new run directory.")]); return 1
    if not source.is_file():
        emit("fail", [error("STATE-002", str(source), "Input is not a readable file.", "Provide an existing CSV, JSON, or JSONL input.")]); return 1
    manifest = {"schema_version": VERSION, "state": "INIT", "input": {"path": str(source), "sha256": digest(source)},
                "output": str(Path(args.output).resolve()), "artifacts": {}, "attempts": {}, "diagnostics": []}
    atomic_write(manifest_path, manifest)
    emit("pass", [], manifest)
    return 0


def advance(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve(); manifest_path = run_dir / "run.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        emit("fail", [error("STATE-003", str(manifest_path), f"Run manifest cannot be read: {exc}.", "Initialize a run or repair the manifest from verified artifacts.")]); return 1
    current, target = manifest.get("state"), args.state
    if current not in STATES or target not in STATES:
        emit("fail", [error("STATE-004", "run.state", "Current or target state is unknown.", "Use one of " + ", ".join(STATES) + ".")]); return 1
    if STATES.index(target) != STATES.index(current) + 1:
        emit("fail", [error("STATE-005", "run.state", f"Invalid transition {current} → {target}.", f"Advance exactly once to {STATES[STATES.index(current)+1] if current != 'COMPLETE' else 'no further state'}.")]); return 1
    stale = verify_recorded_inputs(manifest)
    if stale:
        emit("fail", stale); return 1
    artifact = Path(args.artifact).resolve() if args.artifact else None
    if target in ARTIFACT_NAMES:
        if artifact is None or not artifact.is_file():
            emit("fail", [error("STATE-006", target, "Required state artifact is missing.", "Provide --artifact for " + ARTIFACT_NAMES[target] + ".")]); return 1
        if artifact.name != ARTIFACT_NAMES[target]:
            emit("fail", [error("STATE-013", target, f"Expected {ARTIFACT_NAMES[target]}, received {artifact.name}.", "Provide the canonical artifact produced by this state.")]); return 1
        if target == "VERIFIED":
            try:
                validation = json.loads(artifact.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                emit("fail", [error("STATE-014", str(artifact), f"Validation result cannot be read: {exc}.", "Rerun assets/validate-report.py and provide its validation.json output.")]); return 1
            if validation.get("status") != "pass":
                emit("fail", [error("STATE-015", str(artifact), "Validation result is not passing.", "Resolve every error diagnostic and rerun progressive validation.")]); return 1
        manifest["artifacts"][target] = {"path": str(artifact), "sha256": digest(artifact)}
    if target == "COMPLETE":
        verified = manifest.get("artifacts", {}).get("VERIFIED")
        if not verified:
            emit("fail", [error("STATE-007", "COMPLETE", "No VERIFIED artifact is recorded.", "Pass progressive validation and record validation.json first.")]); return 1
    manifest["state"] = target
    atomic_write(manifest_path, manifest)
    emit("pass", [], manifest)
    return 0


def retry(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve(); manifest_path = run_dir / "run.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        emit("fail", [error("STATE-003", str(manifest_path), f"Run manifest cannot be read: {exc}.", "Initialize a run or repair the manifest from verified artifacts.")]); return 1
    failed_state = args.state
    current = manifest.get("state")
    if current not in STATES or STATES.index(failed_state) > STATES.index(current):
        emit("fail", [error("STATE-008", "run.state", "Cannot retry a stage that the run has not reached.", "Choose the failing current or earlier state.")]); return 1
    attempts = manifest.setdefault("attempts", {})
    count = int(attempts.get(failed_state, 0)) + 1
    total = sum(int(value) for value in attempts.values()) + 1
    if total > 4:
        emit("fail", [error("STATE-009", "run.attempts", "The run has exhausted its four repair attempts.", "Stop the run and report the unresolved limitation; do not add a more complex workaround.")]); return 1
    attempts[failed_state] = count
    target_index = max(0, STATES.index(failed_state) - 1)
    manifest["state"] = STATES[target_index]
    for state in STATES[STATES.index(failed_state):]:
        manifest.get("artifacts", {}).pop(state, None)
    manifest["next_retry"] = {"attempt": total, "strategy": RETRY_STEPS[total - 1], "failed_state": failed_state}
    atomic_write(manifest_path, manifest)
    emit("pass", [], manifest)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage a canvas-report run state without skipping gates.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("--run-dir", required=True); init.add_argument("--input", required=True); init.add_argument("--output", required=True)
    step = sub.add_parser("advance"); step.add_argument("--run-dir", required=True); step.add_argument("--state", required=True, choices=STATES[1:]); step.add_argument("--artifact")
    repair = sub.add_parser("retry"); repair.add_argument("--run-dir", required=True); repair.add_argument("--state", required=True, choices=STATES[1:-1])
    args = parser.parse_args()
    if args.command == "init":
        return initialize(args)
    return advance(args) if args.command == "advance" else retry(args)


if __name__ == "__main__":
    raise SystemExit(main())
