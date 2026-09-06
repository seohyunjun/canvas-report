#!/usr/bin/env python3
"""Generate deterministic macrostructure, theme, and lens candidates before planning."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

THEMES = (
    {"id":"almanac","paper_band":"light","display_class":"humanist-sans","accent_hue":"cool"},
    {"id":"specimen","paper_band":"light","display_class":"high-contrast-serif","accent_hue":"warm"},
    {"id":"newsprint","paper_band":"light","display_class":"roman-serif","accent_hue":"warm"},
    {"id":"cobalt","paper_band":"light","display_class":"techno-grotesk","accent_hue":"cool"},
    {"id":"grid","paper_band":"light","display_class":"neo-grotesk","accent_hue":"warm"},
    {"id":"terminal","paper_band":"dark","display_class":"mono","accent_hue":"green"},
    {"id":"lumen","paper_band":"dark","display_class":"classical-serif","accent_hue":"warm"},
    {"id":"garden","paper_band":"light","display_class":"roman-serif","accent_hue":"green"},
    {"id":"carnival","paper_band":"light","display_class":"display-heavy","accent_hue":"warm"},
    {"id":"riso","paper_band":"light","display_class":"reverse-pair","accent_hue":"cool"},
)
INTENTS = {"conclusion":{"Briefing","Deck"},"lookup":{"Ledger","Workbench"},
           "persuade":{"Scrolly","Broadsheet","Bridge"},"scan":{"Poster","Spread"},
           "explore":{"Workbench","Fieldnotes"}}


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
        prior_theme = next((item for item in THEMES if item["id"] == previous(history, "theme")), None)
        requested_mode = requirements.get("native_mode")
        explicit_theme = requirements.get("theme")
        themes = []
        for item in THEMES:
            compatible = requested_mode in (None, item["paper_band"])
            distance = 3 if prior_theme is None else sum(item[key] != prior_theme[key] for key in ("paper_band","display_class","accent_hue"))
            rotation_excluded = compatible and distance < 2 and item["id"] != explicit_theme
            themes.append({**item, "compatible": compatible, "rotation_distance": distance,
                           "rotation_excluded": rotation_excluded, "explicit_override": item["id"] == explicit_theme})
        result = {"schema_version":"1.0", "profile_sha256":profile_sha256,
                  "requirements_sha256":requirements_sha256, "lenses":lenses,
                  "macros":sorted(macros, key=lambda item: (not item["compatible"], item["rotation_excluded"], not item["intent_match"], item["id"])),
                  "themes":sorted(themes, key=lambda item: (not item["compatible"], item["rotation_excluded"], -item["rotation_distance"], item["id"]))}
        encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output: Path(args.output).write_text(encoded, encoding="utf-8")
        else: print(encoded, end="")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"diagnostics":[{"severity":"error","id":"CANDIDATE-001","location":"candidate selection","problem":str(exc),"suggested_fix":"Provide valid profile, requirements, and history JSON objects."}]}, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
