#!/usr/bin/env python3
"""Build a self-contained report from a validated report-spec.json.

The builder is the only report HTML writer. It accepts no executable fields and
compiles a closed chart vocabulary onto the existing read-only REPORT runtime.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "1.0"
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHELL = ROOT / "assets" / "report-shell.html"
APPLY_THEME = ROOT / "assets" / "apply-theme.py"
SUPPORTED = {
    "line": ("x", "value"),
    "columns": ("x", "value"),
    "divColumns": ("label", "value"),
    "hbars": ("label", "value"),
    "lollipop": ("label", "value"),
    "bubbles": ("label", "x", "y", "size"),
    "concentration": ("label", "value"),
}
INTEGER_RE = re.compile(r"^[+-]?(?:0|[1-9]\d*)$")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$|^[+-]?\d+[eE][+-]?\d+$")


def diagnostic(identifier: str, location: str, problem: str, fix: str) -> dict[str, str]:
    return {"severity": "error", "id": identifier, "location": location,
            "problem": problem, "suggested_fix": fix}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def script_safe_json(value: Any) -> str:
    return canonical(value).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return [{key: parse_csv_scalar(value) for key, value in row.items()}
                    for row in csv.DictReader(handle)]
    if suffix in (".jsonl", ".ndjson"):
        with path.open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    if suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return value
        if isinstance(value, dict) and all(isinstance(item, dict) for item in value.values()):
            return list(value.values())
    raise ValueError("source must be CSV, JSON records, JSONL, or NDJSON")


def parse_csv_scalar(value: str | None) -> Any:
    if value in (None, ""):
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    unsigned = value.lstrip("+-")
    if INTEGER_RE.fullmatch(value) and not (unsigned.startswith("0") and len(unsigned) > 1):
        return int(value)
    if NUMBER_RE.fullmatch(value):
        number = float(value)
        return number if number not in (float("inf"), float("-inf")) else value
    return value


def validate(spec: dict[str, Any], source: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if spec.get("schema_version") != VERSION:
        errors.append(diagnostic("BUILD-001", "spec.schema_version", "Unsupported report spec version.", "Compile a schema_version 1.0 spec with validate-plan.py."))
    source_meta = spec.get("source") if isinstance(spec.get("source"), dict) else {}
    digest = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None
    if digest != source_meta.get("sha256"):
        errors.append(diagnostic("BUILD-002", "spec.source.sha256", "Source data no longer matches the validated profile.", "Regenerate profile.json, plan.json, and report-spec.json from the current source."))
    charts = spec.get("charts") if isinstance(spec.get("charts"), list) else []
    ids: set[str] = set()
    for index, chart in enumerate(charts):
        location = f"spec.charts[{index}]"
        if not isinstance(chart, dict):
            errors.append(diagnostic("BUILD-003", location, "Chart is not an object.", "Recompile the declarative plan.")); continue
        chart_id = chart.get("id")
        if not isinstance(chart_id, str) or not chart_id or chart_id in ids:
            errors.append(diagnostic("BUILD-004", location + ".id", "Chart id is missing or duplicated.", "Use a unique nonempty chart id."))
        ids.add(chart_id)
        chart_type = chart.get("type")
        if chart_type not in SUPPORTED:
            errors.append(diagnostic("BUILD-005", location + ".type", f"Builder does not support chart type {chart_type!r}.", "Simplify to a supported type: " + ", ".join(SUPPORTED) + ".")); continue
        encodings = chart.get("encodings") if isinstance(chart.get("encodings"), dict) else {}
        missing = [name for name in SUPPORTED[chart_type] if not isinstance(encodings.get(name), str) or not encodings[name]]
        if missing:
            errors.append(diagnostic("BUILD-006", location + ".encodings", "Required encodings are missing: " + ", ".join(missing) + ".", "Map every required encoding to a profiled source field."))
    return errors


WIRING = r'''/* [3] REPORT WIRING — generated by assets/build-report.py; do not edit. */
(function(){
'use strict';
var R=REPORT,D=R.data,S=D.spec,rows=D.rows;
function text(tag,cls,value){return R.el(tag,cls,value==null?'':String(value));}
function add(parent,child){parent.appendChild(child);return child;}
function format(value){return typeof value==='number'?R.nf(value):String(value==null?'—':value);}
function chartConfig(chart){
  var e=chart.encodings,base={rows:function(){return rows;},color:'s1'};
  if(chart.type==='line')return Object.assign(base,{x:e.x,y:e.value,format:format});
  if(chart.type==='columns')return {rows:function(){return rows;},x:e.x,series:[{name:chart.title,get:e.value,color:'s1'}],format:format};
  if(chart.type==='divColumns')return Object.assign(base,{x:e.label,y:e.value,format:format});
  if(chart.type==='hbars'||chart.type==='lollipop')return Object.assign(base,{label:e.label,value:e.value,format:format});
  if(chart.type==='bubbles')return Object.assign(base,{label:e.label,x:e.x,y:e.y,size:e.size});
  if(chart.type==='concentration')return Object.assign(base,{label:e.label,value:e.value,format:format});
  throw new Error('unsupported validated chart type: '+chart.type);
}
document.documentElement.lang=S.metadata.locale;
document.title=S.metadata.title;
document.getElementById('hEyebrow').textContent=S.metadata.eyebrow;
document.getElementById('hTitle').textContent=S.metadata.title;
document.getElementById('hSub').textContent=S.metadata.subtitle;
document.getElementById('hMeta').replaceChildren(text('span',null,'Grain: '+S.grain));
var heroFigure=document.getElementById('hFig');if(heroFigure)heroFigure.textContent='';
var main=document.getElementById('main');main.replaceChildren();
if(S.insights.length){
  var summary=add(main,text('section','reveal','')),list=add(summary,text('div','insights',''));
  S.insights.forEach(function(insight){var card=add(list,text('article','insight',''));add(card,text('h3',null,insight.claim));add(card,text('p',null,insight.limitation));});
}
var sections={};
S.sections.forEach(function(section,index){
  var node=add(main,text('section','reveal',''));node.id=section.id;
  var head=add(node,text('div','sec-head',''));add(head,text('p','sec-num',String(index+1).padStart(2,'0')));add(head,text('h2',null,section.title));add(head,text('p','lede',section.lede));
  sections[section.id]=node;
});
S.charts.forEach(function(chart){
  var section=sections[chart.section_id],card=add(section,text('div','card','')),head=add(card,text('div','card-head','')),title=add(head,text('h3',null,chart.title));title.id='title-'+chart.id;
  title.appendChild(R.helpDot(chart.title,chart.help));
  var button=add(head,text('button','btn','Table'));button.type='button';button.setAttribute('data-table-toggle','tablewrap-'+chart.id);button.setAttribute('aria-expanded','false');
  add(card,text('p','card-note',chart.note));var chartWrap=add(card,text('div','chart','')),canvas=add(chartWrap,document.createElement('canvas'));
  canvas.id=chart.id;canvas.height=chart.height||240;canvas.setAttribute('role','img');canvas.setAttribute('aria-label',chart.aria_label);canvas.dataset.motionEnabled=String(chart.motion.enabled);canvas.dataset.motionReason=chart.motion.reason;
  var tableWrap=add(card,text('div','tablewrap',''));tableWrap.id='tablewrap-'+chart.id;tableWrap.hidden=true;var table=add(tableWrap,document.createElement('table'));table.id='table-'+chart.id;
  var factory=R.VIZ[chart.type];if(typeof factory!=='function')throw new Error('runtime lacks '+chart.type);factory(canvas,chartConfig(chart));
  R.buildTable(table,chart.table.columns.map(function(field){return {name:field,value:function(row){return format(row[field]);},num:false};}),rows,{caption:chart.title+' data'});
});
var method=add(main,text('section','reveal',''));method.id='methodology';var mh=add(method,text('div','sec-head',''));add(mh,text('p','sec-num','Method'));add(mh,text('h2',null,'Basis, formulas, and limits'));var mc=add(method,text('div','card method',''));
[['Basis',S.methodology.basis],['Formulas',S.methodology.formulas],['Limits',S.methodology.limitations]].forEach(function(group){var block=add(mc,text('div',null,''));add(block,text('h3',null,group[0]));group[1].forEach(function(item){add(block,text('p',null,item));});});
R.wireHelp();R.wireToggles();R.reveal();R.paintAll();R.playAll(700);
})();
'''


def build(spec: dict[str, Any], records: list[dict[str, Any]], shell: str) -> str:
    public_spec = {key: spec[key] for key in ("schema_version", "plan_sha256", "metadata", "masthead", "grain", "lenses", "insights", "macro", "theme", "sections", "charts", "methodology", "rule_decisions")}
    payload = script_safe_json({"rows": records, "spec": public_spec})
    data_pattern = re.compile(r'(<script id="report-data" type="application/json">)\s*.*?\s*(</script>)', re.S)
    if len(data_pattern.findall(shell)) != 1:
        raise ValueError("runtime shell must contain exactly one report-data script")
    result = data_pattern.sub(lambda match: match.group(1) + "\n" + payload + "\n" + match.group(2), shell)
    marker = result.find("* [3] REPORT WIRING")
    if marker < 0:
        raise ValueError("runtime shell lacks the REPORT WIRING marker")
    marker = result.rfind("/*", 0, marker)
    end = result.find("</script>", marker)
    if end < 0:
        raise ValueError("runtime shell wiring script is not closed")
    result = result[:marker] + WIRING + result[end:]
    spec_hash = hashlib.sha256(canonical(spec).encode("utf-8")).hexdigest()
    provenance = "<!-- canvas-report spec-sha256: %s · rules: %s -->\n" % (
        spec_hash, ",".join(item["rule_id"] for item in spec.get("rule_decisions", []) if isinstance(item, dict) and isinstance(item.get("rule_id"), str)))
    return result.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + provenance, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a validated report spec into self-contained HTML.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--shell", default=str(DEFAULT_SHELL))
    parser.add_argument("--manifest")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors: list[dict[str, str]] = []
    try:
        spec_path, shell_path = Path(args.spec), Path(args.shell)
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        source = Path(spec.get("source", {}).get("path", ""))
        errors = validate(spec, source)
        if not errors:
            records = load_records(source)
            if not all(isinstance(row, dict) for row in records):
                raise ValueError("every source record must be an object")
            html = build(spec, records, shell_path.read_text(encoding="utf-8"))
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as handle:
                handle.write(html); temporary = Path(handle.name)
            subprocess.run([sys.executable, str(APPLY_THEME), str(temporary), spec["theme"]], check=True, capture_output=True, text=True)
            os.replace(temporary, output)
            manifest = {"schema_version": VERSION, "builder_version": VERSION,
                        "spec_sha256": hashlib.sha256(canonical(spec).encode()).hexdigest(),
                        "shell_sha256": hashlib.sha256(shell_path.read_bytes()).hexdigest(),
                        "source_sha256": spec["source"]["sha256"],
                        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
            if args.manifest:
                Path(args.manifest).write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            if args.json: print(json.dumps({"status":"pass","diagnostics":[],"manifest":manifest}, sort_keys=True))
            else: print("Built %s" % output)
    except (OSError, KeyError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        errors.append(diagnostic("BUILD-000", "builder", str(error), "Fix the report spec or builder inputs, then rebuild; never patch generated HTML."))
    if errors:
        result = {"status": "fail", "diagnostics": errors}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else "\n".join("ERROR %s %s: %s\n  Fix: %s" % (item["id"], item["location"], item["problem"], item["suggested_fix"]) for item in errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
