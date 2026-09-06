#!/usr/bin/env python3
"""Build a deterministic, honest profile for CSV, JSON, or JSONL data."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INTEGER_RE = re.compile(r"^[+-]?(?:0|[1-9]\d*)$")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$|^[+-]?\d+[eE][+-]?\d+$")
SENTINELS = {"n/a", "na", "unknown", "unclassified", "-", "-1", "9999"}


class ProfileError(Exception):
    def __init__(self, identifier: str, location: str, problem: str, suggested_fix: str):
        self.identifier = identifier
        self.location = location
        self.problem = problem
        self.suggested_fix = suggested_fix
        super().__init__(problem)


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ProfileError("invalid_arguments", "command line", message, "Run with --help and provide an input file and --output path.")


def fail(identifier: str, location: str, problem: str, suggested_fix: str) -> None:
    raise ProfileError(identifier, location, problem, suggested_fix)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                fail("missing_csv_header", str(path), "CSV input has no header row.", "Add a header row with unique column names.")
            columns = list(reader.fieldnames)
            if any(name is None or name == "" for name in columns) or len(set(columns)) != len(columns):
                fail("invalid_csv_header", str(path), "CSV header names must be non-empty and unique.", "Rename empty or duplicate header fields.")
            records: list[dict[str, Any]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    fail("csv_extra_fields", f"{path}:{row_number}", "A CSV row has more fields than the header.", "Make each row contain the same number of fields as the header.")
                records.append({name: parse_csv_scalar(row[name]) for name in columns})
            return columns, records
    except UnicodeDecodeError as exc:
        fail("invalid_encoding", str(path), f"Input is not valid UTF-8: {exc}.", "Save the input as UTF-8 text.")
    except csv.Error as exc:
        fail("invalid_csv", str(path), f"CSV could not be parsed: {exc}.", "Fix CSV quoting and delimiters.")


def parse_csv_scalar(value: str) -> Any:
    """Infer only unambiguous scalar types; preserve identifiers such as 001."""
    if value == "":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if INTEGER_RE.fullmatch(value) and not (
        value.lstrip("+-").startswith("0") and len(value.lstrip("+-")) > 1
    ):
        return int(value)
    if NUMBER_RE.fullmatch(value):
        number = float(value)
        return number if math.isfinite(number) else value
    return value


def columns_and_records(records: list[Any], location: str) -> tuple[list[str], list[dict[str, Any]]]:
    columns: list[str] = []
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            fail("invalid_record", f"{location}:{index}", "Every record must be a JSON object.", "Use an array, object-of-records, or JSONL file containing objects.")
        for key in record:
            if not isinstance(key, str):
                fail("invalid_column_name", f"{location}:{index}", "Column names must be strings.", "Use string property names in each JSON record.")
            if key not in columns:
                columns.append(key)
        normalized.append(record)
    return columns, normalized


def read_json(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=lambda token: fail(
                "invalid_json_number",
                str(path),
                f"JSON contains unsupported numeric constant {token}.",
                "Use only finite JSON numbers.",
            ),
        )
    except UnicodeDecodeError as exc:
        fail("invalid_encoding", str(path), f"Input is not valid UTF-8: {exc}.", "Save the input as UTF-8 text.")
    except json.JSONDecodeError as exc:
        fail("invalid_json", f"{path}:{exc.lineno}:{exc.colno}", exc.msg + ".", "Fix the JSON syntax.")
    if isinstance(value, list):
        return columns_and_records(value, str(path))
    if isinstance(value, dict):
        return columns_and_records(list(value.values()), str(path))
    fail("invalid_json_root", str(path), "JSON input must be an array of records or an object whose values are records.", "Use a JSON array/object-of-records, or use JSONL.")


def read_jsonl(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    records: list[Any] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(
                        json.loads(
                            line,
                            parse_constant=lambda token: fail(
                                "invalid_json_number",
                                f"{path}:{number}",
                                f"JSON contains unsupported numeric constant {token}.",
                                "Use only finite JSON numbers.",
                            ),
                        )
                    )
                except json.JSONDecodeError as exc:
                    fail("invalid_jsonl", f"{path}:{number}:{exc.colno}", exc.msg + ".", "Put one valid JSON object on each non-empty line.")
    except UnicodeDecodeError as exc:
        fail("invalid_encoding", str(path), f"Input is not valid UTF-8: {exc}.", "Save the input as UTF-8 text.")
    return columns_and_records(records, str(path))


def input_format(path: Path) -> str:
    extension = path.suffix.lower()
    if extension == ".csv":
        return "csv"
    if extension in {".jsonl", ".ndjson"}:
        return "jsonl"
    if extension == ".json":
        return "json"
    fail("unsupported_format", str(path), "Input format is not recognized.", "Use a .csv, .json, .jsonl, or .ndjson file.")


def value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        if not math.isfinite(value):
            return "mixed"
        return "number"
    if isinstance(value, str):
        if DATE_RE.fullmatch(value):
            try:
                dt.date.fromisoformat(value)
                return "date"
            except ValueError:
                pass
        if "T" in value or " " in value:
            try:
                dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                return "datetime"
            except ValueError:
                pass
        return "string"
    return "mixed"


def profile_column(name: str, values: list[Any]) -> dict[str, Any]:
    null_count = sum(value is None for value in values)
    non_null = [value for value in values if value is not None]
    types = {value_type(value) for value in non_null}
    inferred = "null" if not types else next(iter(types)) if len(types) == 1 else "mixed"
    # JSON values can contain arrays/objects; they are intentionally mixed rather than stringified.
    distinct = {json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for value in non_null}
    result: dict[str, Any] = {
        "name": name,
        "type": inferred,
        "null_count": null_count,
        "null_rate": null_count / len(values) if values else 0.0,
        "distinct_count": len(distinct),
        "candidate_key": bool(values) and null_count == 0 and len(distinct) == len(values),
        "sentinel_candidates": {
            label: count
            for label in sorted(SENTINELS)
            if (count := sum(str(value).strip().lower() == label for value in non_null))
        },
    }
    if inferred in {"integer", "number"}:
        result["min"] = min(non_null)
        result["max"] = max(non_null)
    elif inferred in {"date", "datetime"}:
        result["min"] = min(non_null)
        result["max"] = max(non_null)
    return result


def build_profile(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail("missing_input", str(path), "Input file does not exist or is not a regular file.", "Provide the path to an existing data file.")
    format_name = input_format(path)
    if format_name == "csv":
        columns, records = read_csv(path)
    elif format_name == "json":
        columns, records = read_json(path)
    else:
        columns, records = read_jsonl(path)
    profiled_columns = [profile_column(name, [record.get(name) for record in records]) for name in columns]
    date_columns = [column["name"] for column in profiled_columns if column["type"] in {"date", "datetime"}]
    numeric_columns = [column["name"] for column in profiled_columns if column["type"] in {"integer", "number"}]
    dimension_columns = [column["name"] for column in profiled_columns if column["type"] in {"string", "boolean"}]
    time_grains = {}
    for name in date_columns:
        values = [record.get(name) for record in records if record.get(name) is not None]
        if next(column["type"] for column in profiled_columns if column["name"] == name) == "datetime":
            time_grains[name] = "datetime"
            continue
        parsed = [dt.date.fromisoformat(value) for value in values]
        if parsed and all(value.month == 1 and value.day == 1 for value in parsed):
            time_grains[name] = "year"
        elif parsed and all(value.month in {1, 4, 7, 10} and value.day == 1 for value in parsed):
            time_grains[name] = "quarter"
        elif parsed and all(value.day == 1 for value in parsed):
            time_grains[name] = "month"
        else:
            time_grains[name] = "day"
    return {
        "schema_version": SCHEMA_VERSION,
        "source": {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "format": format_name},
        "row_count": len(records),
        "column_count": len(columns),
        "columns": profiled_columns,
        "candidate_keys": [column["name"] for column in profiled_columns if column["candidate_key"]],
        "date_columns": date_columns,
        "numeric_columns": numeric_columns,
        "dimension_columns": dimension_columns,
        "time_grains": time_grains,
        "comparable_periods": any(
            column["name"] in date_columns and column["distinct_count"] >= 2
            for column in profiled_columns
        ),
    }


def main() -> int:
    parser = Parser(description="Create a deterministic profile JSON for CSV, JSON records, or JSONL records.")
    parser.add_argument("input", metavar="INPUT", help="Input .csv, .json, .jsonl, or .ndjson data file")
    parser.add_argument("--output", required=True, metavar="PROFILE_JSON", help="Path for the generated profile JSON")
    try:
        args = parser.parse_args()
        profile = build_profile(Path(args.input))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(profile, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        return 0
    except ProfileError as exc:
        print(json.dumps({"severity": "error", "id": exc.identifier, "location": exc.location, "problem": exc.problem, "suggested_fix": exc.suggested_fix}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1
    except OSError as exc:
        print(json.dumps({"severity": "error", "id": "io_error", "location": str(getattr(exc, "filename", "filesystem")), "problem": str(exc), "suggested_fix": "Check file paths and read/write permissions."}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
