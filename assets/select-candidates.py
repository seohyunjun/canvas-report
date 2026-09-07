#!/usr/bin/env python3
"""Generate deterministic macrostructure, theme, and lens candidates before planning.\n\nThemes are ranked by how well their subject matches the dataset, then by rotation\ndistance from the previous run. references/themes.json is the catalogue.\n"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CATALOGUE = Path(__file__).resolve().parent.parent / "references" / "themes.json"
AXES = ("paper_band", "display_class", "accent_hue")
MIN_KEYWORD = 4
FIT_SATURATION = 5.0

INTENTS = {"conclusion":{"Briefing","Deck"},"lookup":{"Ledger","Workbench"},
           "persuade":{"Scrolly","Broadsheet","Bridge"},"scan":{"Poster","Spread"},
           "explore":{"Workbench","Fieldnotes"}}


def themes() -> list[dict[str, Any]]:
    """The canonical catalogue. Selection reads it; themes.css only holds tokens."""
    rows = json.loads(CATALOGUE.read_text(encoding="utf-8")).get("themes", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{CATALOGUE} lists no themes")
    return rows


def tokens(value: Any, sink: set[str]) -> None:
    """Collect lowercase word tokens from any nested requirement or profile value."""
    if isinstance(value, str):
        word = ""
        for ch in value.lower():
            if ch.isalnum():
                word += ch
            else:
                if word:
                    sink.add(word)
                word = ""
        if word:
            sink.add(word)
    elif isinstance(value, dict):
        for key, item in value.items():
            tokens(key, sink)
            tokens(item, sink)
    elif isinstance(value, list):
        for item in value:
            tokens(item, sink)


def subject_signals(profile: dict[str, Any], requirements: dict[str, Any]) -> list[str]:
    """What the dataset is about, as far as the artifacts can evidence it.

    Column names carry the subject far more reliably than a title does, so they are
    the first source; the file name and the stated requirements fill in the rest.
    Nothing here inspects cell values — the profile is the only view of the data.
    """
    sink: set[str] = set()
    for column in profile.get("columns", []):
        if isinstance(column, dict):
            tokens(column.get("name"), sink)
    source = profile.get("source")
    if isinstance(source, dict):
        tokens(Path(str(source.get("path", ""))).stem, sink)
    for key in ("subject", "domain", "title", "audience", "question", "notes", "purpose"):
        tokens(requirements.get(key), sink)
    return sorted(token for token in sink if len(token) >= 3)


def subject_fit(theme: dict[str, Any], signals: list[str]) -> tuple[float, list[str]]:
    """Score one theme against the dataset's subject.

    A keyword matches when a signal token equals it or starts with it, so `enrol`
    catches `enrolment` without `enrol` also catching an unrelated `enrolled_by_id`
    twice. The score saturates: five matches is as fitted as a theme gets, and the
    catalogue baseline keeps subject-neutral themes selectable for data whose
    columns say nothing about their domain.
    """
    matched = sorted({
        keyword for keyword in theme.get("subjects", [])
        if len(keyword) >= MIN_KEYWORD and any(token.startswith(keyword) for token in signals)
    })
    earned = min(1.0, len(matched) / FIT_SATURATION)
    return round(max(earned, float(theme.get("baseline", 0.0))), 3), matched


def load(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def previous(history: dict[str, Any], key: str) -> str | None:
    rows = history.get("runs", []) if isinstance(history.get("runs"), list) else []
    for row in reversed(rows):
        if isinstance(row, dict) and isinstance(row.get(key), str):
            return row[key]
    return history.get(key) if isinstance(history.get(key), str) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter compatible report choices before applying rotation.")
    parser.add_argument("--profile", required=True); parser.add_argument("--requirements"); parser.add_argument("--history"); parser.add_argument("--output")
    args = parser.parse_args()
    try:
        profile, requirements, history = load(args.profile), load(args.requirements), load(args.history)
        profile_sha256 = hashlib.sha256(Path(args.profile).read_bytes()).hexdigest()
        requirements_sha256 = (
            hashlib.sha256(Path(args.requirements).read_bytes()).hexdigest()
            if args.requirements else hashlib.sha256(b"{}").hexdigest()
        )
        columns = [item for item in profile.get("columns", []) if isinstance(item, dict)]
        numeric = [item for item in columns if item.get("type") in ("integer", "number")]
        dimensions = [item for item in columns if item.get("type") in ("string", "boolean")]
        dates = [item for item in columns if item.get("type") in ("date", "datetime")]
        keys = profile.get("candidate_keys", [])
        lenses: list[dict[str, Any]] = []
        lens_tests = {
            "trend": (bool(dates and numeric and any(item.get("distinct_count", 0) >= 6 for item in dates)), "requires a date column with at least 6 periods and a numeric measure"),
            "comparison": (bool(dimensions and numeric), "requires a dimension and numeric measure"),
            "distribution": (bool(numeric), "requires a numeric measure"),
            "relationship": (len(numeric) >= 2, "requires at least two numeric measures"),
            "cohort": (bool(keys and dates), "requires a candidate key and date column"),
        }
        for identifier, (eligible, reason) in lens_tests.items():
            lenses.append({"id": identifier, "eligible": eligible, "reason": "profile satisfies requirements" if eligible else reason})
        claim_count = requirements.get("claim_count", 0)
        macro_tests = {
            "Briefing": (True, "general conclusion-first structure"),
            "Broadsheet": (requirements.get("narrative_evidence", True) is True, "requires narrative evidence"),
            "Ledger": (len(numeric) >= 8, "requires at least 8 numeric measures"),
            "Scrolly": (requirements.get("staged_subject") is True and requirements.get("stage_count", 0) >= 4, "requires a staged subject with at least 4 stages"),
            "Workbench": (len(dimensions) >= 3, "requires at least 3 dimensions"),
            "Poster": (requirements.get("homogeneous_series_count", 0) >= 12, "requires at least 12 homogeneous series"),
            "Deck": (5 <= claim_count <= 8, "requires 5–8 evidence-backed claims"),
            "Bridge": (bool(keys and profile.get("comparable_periods")), "requires a candidate key and at least 2 comparable periods"),
            "Spread": (requirements.get("comparable_sets") == 2, "requires exactly 2 comparable sets"),
            "Fieldnotes": (requirements.get("qualitative_notes") is True, "requires qualitative notes"),
        }
        prior_macro = previous(history, "macro")
        intent = requirements.get("reader_intent")
        explicit_macro = requirements.get("macro")
        macros = []
        for identifier, (compatible, reason) in macro_tests.items():
            rotated = compatible and identifier == prior_macro and identifier != explicit_macro
            macros.append({"id": identifier, "compatible": compatible, "rotation_excluded": rotated,
                           "intent_match": identifier in INTENTS.get(intent, set()), "reason": reason})
        catalogue = themes()
        signals = subject_signals(profile, requirements)
        prior_theme = next((item for item in catalogue if item["id"] == previous(history, "theme")), None)
        requested_mode = requirements.get("native_mode")
        explicit_theme = requirements.get("theme")
        theme_rows = []
        for item in catalogue:
            compatible = requested_mode in (None, item["paper_band"])
            distance = 3 if prior_theme is None else sum(item[key] != prior_theme[key] for key in AXES)
            rotation_excluded = compatible and distance < 2 and item["id"] != explicit_theme
            fit_score, fit_matched = subject_fit(item, signals)
            theme_rows.append({
                "id": item["id"], "paper_band": item["paper_band"],
                "display_class": item["display_class"], "accent_hue": item["accent_hue"],
                "suits": item.get("suits", ""), "compatible": compatible,
                "rotation_distance": distance, "rotation_excluded": rotation_excluded,
                "explicit_override": item["id"] == explicit_theme,
                "fit_score": fit_score, "fit_matched": fit_matched,
            })
        result = {"schema_version":"1.0", "profile_sha256":profile_sha256,
                  "requirements_sha256":requirements_sha256, "lenses":lenses,
                  "subject_signals":signals,
                  "macros":sorted(macros, key=lambda item: (not item["compatible"], item["rotation_excluded"], not item["intent_match"], item["id"])),
                  # Subject fit outranks rotation distance: a report about payroll should
                  # look like payroll first, and merely differ from the last report second.
                  "themes":sorted(theme_rows, key=lambda item: (not item["compatible"], item["rotation_excluded"], -item["fit_score"], -item["rotation_distance"], item["id"]))}
        encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output: Path(args.output).write_text(encoded, encoding="utf-8")
        else: print(encoded, end="")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"diagnostics":[{"severity":"error","id":"CANDIDATE-001","location":"candidate selection","problem":str(exc),"suggested_fix":"Provide valid profile, requirements, and history JSON objects, and a readable references/themes.json catalogue."}]}, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
