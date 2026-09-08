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
# Required encodings per chart type. Every name here is a role the factory reads;
# the plan maps each role to one profiled column. references/analysis-lenses.md
# says which data shape earns which of these.
SUPPORTED = {
    "line": ("x", "value"),
    "columns": ("x", "value"),
    "divColumns": ("label", "value"),
    "hbars": ("label", "value"),
    "lollipop": ("label", "value"),
    "bubbles": ("label", "x", "y", "size"),
    "concentration": ("label", "value"),
    "divHbars": ("label", "value"),
    "donut": ("label", "value"),
    "heatmap": ("x", "y", "value"),
    "slope": ("label", "before", "after"),
    "waterfall": ("label", "value"),
    "boxplot": ("label", "lo", "q1", "med", "q3", "hi"),
    "stackedArea": ("x", "value", "value2"),
    "panels": ("label", "value", "value2"),
    "interval": ("label", "value", "lo", "hi"),
    "scatter": ("label", "x", "y"),
    "dumbbell": ("label", "before", "after"),
    "bullet": ("label", "value", "target"),
    "histogram": ("value",),
    "spark": ("value",),
}
# Roles a type accepts but does not require. The series ceiling is three because
# references/themes.md refuses to invent a fourth colour, not because the factory
# could not draw one.
OPTIONAL = {
    "columns": ("value2", "value3"),
    "stackedArea": ("value3",),
    "panels": ("value3",),
}
# Marks a factory refuses to draw past. The runtime prints a message instead of the
# data, so this is a plan-time incompatibility rather than a rendering detail.
ROW_LIMITS = {"lollipop": (1, 20), "donut": (2, 5), "slope": (1, 12), "heatmap": (1, 100),
              "stackedArea": (2, None), "concentration": (2, None)}

# Charts that read a magnitude as a share, an area, or an intensity. A negative
# value has no length on any of them.
NON_NEGATIVE = {"donut", "heatmap", "stackedArea", "concentration", "bubbles"}
SERIES_ROLES = ("value", "value2", "value3")
INTEGER_RE = re.compile(r"^[+-]?(?:0|[1-9]\d*)$")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$|^[+-]?\d+[eE][+-]?\d+$")
VENDORED_RUNTIMES = {
    "gsap": {
        "version": "3.15.0",
        # The core, not lab/.../gsap-all-3.15.0.min.js: a report inlines what it runs, and
        # it runs one entry tween. The 325 KB all-plugin bundle is the lab's, not a
        # document's. lab/motion-engines/docs/gsap.md carries the plugin catalogue.
        "path": ROOT / "lab" / "motion-engines" / "vendor" / "gsap-3.15.0.min.js",
        "sha256": "92bb9a96476f983d212a2bc4f54c889039c1696dd4461d40a736860938570fbb",
        "license": "Standard \"No Charge\" GSAP License",
    },
    "motion": {
        "version": "11.11.17",
        "path": ROOT / "lab" / "motion-engines" / "vendor" / "motion-11.11.17.js",
        "sha256": "61b3a38dabf65a31778bc7fa9e71936bfa36ec2f567e50de261b958a3037e84e",
        "license": "MIT",
    },
    "anime": {
        "version": "3.2.2",
        "path": ROOT / "lab" / "motion-engines" / "vendor" / "anime-3.2.2.min.js",
        "sha256": "bceef94f964481f7680d95e7fbbe5a8c20d3945a926a754874898a578db7c7ab",
        "license": "MIT",
    },
}


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
        known = set(SUPPORTED[chart_type]) | set(OPTIONAL.get(chart_type, ()))
        extra = sorted(set(encodings) - known)
        if extra:
            errors.append(diagnostic("BUILD-007", location + ".encodings", f"{chart_type} does not read: " + ", ".join(extra) + ".", "Remove the role, or use a chart type that reads it: " + ", ".join(sorted(known)) + "."))
    selected = spec.get("creative_direction", {}).get("external_tools", [])
    for index, item in enumerate(selected if isinstance(selected, list) else []):
        if not isinstance(item, dict) or item.get("integration") != "vendored-runtime":
            continue
        tool = item.get("tool")
        runtime = VENDORED_RUNTIMES.get(tool)
        location = f"spec.creative_direction.external_tools[{index}]"
        if runtime is None:
            errors.append(diagnostic("BUILD-RUNTIME-001", location, f"No vendored runtime is supported for {tool!r}.", "Use portable-pattern or a supported pinned motion engine: GSAP, Motion, or anime.js."))
            continue
        path = runtime["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != runtime["sha256"]:
            errors.append(diagnostic("BUILD-RUNTIME-002", location, f"Pinned {tool} runtime is missing or its SHA-256 changed.", "Restore the recorded vendor file and verify lab/motion-engines/vendor/SHA256SUMS."))
    return errors


def vendored_runtime_records(spec: dict[str, Any]) -> list[dict[str, str]]:
    selected = spec.get("creative_direction", {}).get("external_tools", [])
    records = []
    for item in selected if isinstance(selected, list) else []:
        if isinstance(item, dict) and item.get("integration") == "vendored-runtime":
            tool = item.get("tool")
            runtime = VENDORED_RUNTIMES[tool]
            records.append({"tool": tool, "version": runtime["version"], "sha256": runtime["sha256"], "license": runtime["license"]})
    return records


def inline_vendored_runtimes(html: str, spec: dict[str, Any]) -> str:
    blocks = []
    for record in vendored_runtime_records(spec):
        runtime = VENDORED_RUNTIMES[record["tool"]]
        source = runtime["path"].read_text(encoding="utf-8")
        if "</script" in source.lower():
            raise ValueError(f"vendored {record['tool']} runtime contains a script-closing token")
        blocks.append(
            '<script data-canvas-report-runtime="%s" data-version="%s" data-sha256="%s" data-license="%s">\n%s\n</script>\n'
            % (record["tool"], record["version"], record["sha256"], record["license"], source)
        )
    if not blocks:
        return html
    marker = html.find("* [3] REPORT WIRING")
    if marker < 0:
        raise ValueError("runtime shell lacks the REPORT WIRING marker")
    script_start = html.rfind("<script", 0, marker)
    if script_start < 0:
        raise ValueError("runtime shell wiring script is not open")
    return html[:script_start] + "".join(blocks) + html[script_start:]


WIRING = r'''/* [3] REPORT WIRING — generated by assets/build-report.py; do not edit. */
(function(){
'use strict';
var R=REPORT,D=R.data,S=D.spec,rows=D.rows;
/* Builder chrome is English. The report's own prose — titles, notes, help, methodology —
   is whatever language the plan was written in; these are the words the builder supplies. */
var L={grain:'Grain',table:'Table',method:'Method',methodTitle:'Basis, formulas, and limits',basis:'Basis',formulas:'Formulas',limits:'Limits',data:' data'};
function text(tag,cls,value){return R.el(tag,cls,value==null?'':String(value));}
function add(parent,child){parent.appendChild(child);return child;}
function format(value){return typeof value==='number'?R.nf(value):String(value==null?'—':value);}
function toolIntegration(tool){
  var tools=S.creative_direction&&S.creative_direction.external_tools||[];
  for(var i=0;i<tools.length;i++)if(tools[i].tool===tool)return tools[i].integration;
  return 'portable-pattern';
}
function motionEase(name){return {linear:'linear',outCubic:[.22,.61,.36,1],inOutCubic:[.65,0,.35,1],outQuint:[.23,1,.32,1],outExpo:[.16,1,.3,1],outCirc:[0,.55,.45,1],inOutQuint:[.83,0,.17,1]}[name]||[.22,.61,.36,1];}
function gsapEase(name){return {linear:'none',outCubic:'power3.out',inOutCubic:'power3.inOut',outQuint:'power4.out',outExpo:'expo.out',outCirc:'circ.out',inOutQuint:'power4.inOut'}[name]||'power3.out';}
function animeEase(name){return {linear:'linear',outCubic:'easeOutCubic',inOutCubic:'easeInOutCubic',outQuint:'easeOutQuint',outExpo:'easeOutExpo',outCirc:'easeOutCirc',inOutQuint:'easeInOutQuint'}[name]||'easeOutCubic';}
function runtimeName(tool){return {gsap:'gsap@3.15.0',motion:'motion@11.11.17',anime:'anime@3.2.2'}[tool]||null;}
function hasVendoredRuntime(tool){return tool==='gsap'?!!(window.gsap&&window.gsap.to):tool==='motion'?!!(window.Motion&&window.Motion.animate):tool==='anime'?typeof window.anime==='function':false;}
function playVendoredMotion(canvas,engine,chart){
  var tool=chart.motion.source_tool;engine.__played=true;engine.__motionRuntime=runtimeName(tool);
  var token={};engine.__token=token;
  function paint(){R.paintOne(engine);}
  function finish(){
    if(engine.__token!==token)return;
    if(tool==='gsap'&&engine.__externalMotionHandle&&typeof engine.__externalMotionHandle.kill==='function')engine.__externalMotionHandle.kill();
    if(tool==='motion'&&engine.__externalMotionHandle&&typeof engine.__externalMotionHandle.stop==='function')engine.__externalMotionHandle.stop();
    if(tool==='anime'&&window.anime&&typeof window.anime.remove==='function')window.anime.remove(engine);
    engine.t=1;paint();engine.__externalMotionHandle=null;
  }
  if(R.reduced()){finish();return;}
  engine.t=0;paint();
  var duration=Math.min(1200,Math.max(180,Number(chart.motion.duration_ms)||700));
  if(tool==='gsap')engine.__externalMotionHandle=window.gsap.to(engine,{t:1,duration:duration/1000,ease:gsapEase(chart.motion.easing),onUpdate:function(){if(engine.__token===token){engine.t=Math.max(0,Math.min(1,engine.t));paint();}},onComplete:finish});
  else if(tool==='motion')engine.__externalMotionHandle=window.Motion.animate(0,1,{duration:duration/1000,ease:motionEase(chart.motion.easing),onUpdate:function(value){if(engine.__token===token){engine.t=Math.max(0,Math.min(1,value));paint();}},onComplete:finish});
  else if(tool==='anime')engine.__externalMotionHandle=window.anime({targets:engine,t:1,duration:duration,easing:animeEase(chart.motion.easing),update:function(){if(engine.__token===token){engine.t=Math.max(0,Math.min(1,engine.t));paint();}},complete:finish});
  setTimeout(finish,duration+260);
}
/* A series set is value, value2, value3 in order, named by the column each one
   reads. The field name is what the table twin already prints, so the legend and
   the table cannot disagree about which number is which. Three is the ceiling:
   references/themes.md refuses to invent a fourth colour. */
var SERIES_ROLES=['value','value2','value3'],SERIES_COLORS=['s1','s2','s3'];
function seriesOf(chart){
  var e=chart.encodings,out=[];
  SERIES_ROLES.forEach(function(role,i){
    if(typeof e[role]==='string'&&e[role])out.push({name:e[role],get:e[role],color:SERIES_COLORS[i]});
  });
  return out;
}
/* Plan options are snake_case and the factories are camelCase; this is the whole
   translation. Every name here is a capability the shipped factory already had
   and no plan could previously ask for. validate-plan.py owns which type takes
   which, so an unknown name never reaches this map. */
var OPTION_KEYS={reference:'ref',reference_label:'refLabel',identity_line:'identityLine',
  axis_x:'axisX',axis_y:'axisY',zero_based:'zeroBased',rotate_labels:'rotate',
  axis_note:'axisNote',bins:'bins',marks:'marks',start_label:'startLabel',
  end_label:'endLabel',center_label:'centerLabel',center_note:'centerNote',
  target_label:'targetLabel',before_label:'beforeLabel',after_label:'afterLabel',
  band_note:'bandNote'};
function withOptions(chart,cfg){
  var o=chart.options;
  if(!o) return cfg;
  Object.keys(o).forEach(function(k){
    /* divColumns diverges when it is handed NEITHER colorOf nor a flat colour.
       The option is therefore the absence of one, not a value to pass through. */
    if(k==='diverging'){ if(o[k]) delete cfg.color; return; }
    var name=OPTION_KEYS[k];
    if(name) cfg[name]=o[k];
  });
  return cfg;
}
function chartConfig(chart){
  var e=chart.encodings,base={rows:function(){return rows;},color:'s1'},series=seriesOf(chart);
  if(chart.type==='line')return Object.assign(base,{x:e.x,y:e.value,format:format});
  if(chart.type==='columns')return {rows:function(){return rows;},x:e.x,series:series,format:format};
  if(chart.type==='divColumns')return Object.assign(base,{x:e.label,y:e.value,format:format});
  if(chart.type==='hbars'||chart.type==='lollipop')return Object.assign(base,{label:e.label,value:e.value,format:format});
  if(chart.type==='bubbles')return Object.assign(base,{label:e.label,x:e.x,y:e.y,size:e.size});
  if(chart.type==='concentration')return Object.assign(base,{label:e.label,value:e.value,format:format});
  if(chart.type==='divHbars')return Object.assign(base,{label:e.label,value:e.value,format:format});
  /* donut and slope colour each row from the series ramp, and they do it by taking
     cfg.color as the DEFAULT passed to colorOf — which returns a default unresolved.
     Handing them the token name 's1' would paint the literal string, which canvas
     ignores, leaving every arc the previous fill. Omit color and let them ramp. */
  if(chart.type==='donut')return {rows:function(){return rows;},label:e.label,value:e.value,format:format};
  if(chart.type==='heatmap')return Object.assign(base,{x:e.x,y:e.y,value:e.value,format:format});
  if(chart.type==='slope')return {rows:function(){return rows;},label:e.label,before:e.before,after:e.after,
    labels:{before:e.before,after:e.after},format:format};
  if(chart.type==='waterfall')return {format:format,steps:function(){
    return rows.map(function(r){return {name:String(r[e.label]),value:Number(r[e.value])};});}};
  if(chart.type==='boxplot')return Object.assign(base,{label:e.label,lo:e.lo,q1:e.q1,med:e.med,q3:e.q3,hi:e.hi,format:format});
  if(chart.type==='stackedArea')return {rows:function(){return rows;},x:e.x,series:series,format:format};
  if(chart.type==='panels')return {rows:function(){return rows;},label:e.label,
    panels:series.map(function(s){return {title:s.name,get:s.get,color:s.color};}),format:format};
  if(chart.type==='interval')return Object.assign(base,{label:e.label,value:e.value,lo:e.lo,hi:e.hi,format:format});
  if(chart.type==='scatter')return Object.assign(base,{label:e.label,x:e.x,y:e.y,format:format});
  if(chart.type==='dumbbell')return Object.assign(base,{label:e.label,before:e.before,after:e.after,format:format});
  if(chart.type==='bullet')return Object.assign(base,{label:e.label,value:e.value,target:e.target,format:format});
  if(chart.type==='histogram')return Object.assign(base,{value:e.value,format:format});
  /* spark takes a value list, not rows: it has no axes and reads no x. Row order
     is the source's, exactly as it is for line and stackedArea. */
  if(chart.type==='spark')return {values:function(){return rows.map(function(r){return Number(r[e.value]);});},color:'s1'};
  throw new Error('unsupported validated chart type: '+chart.type);
}
/* A multi-series chart is unreadable without a key, and the key has to survive the
   theme toggle — the swatch colour is a token value, not a class. R.onTheme runs the
   hook now and again on every change. `panels` is not here: it prints each metric's
   name above its own panel, so a second key would only repeat it. */
function legendFor(chart,card){
  var series=seriesOf(chart);
  if(series.length<2||(chart.type!=='columns'&&chart.type!=='stackedArea'))return;
  var node=add(card,text('div','legend',''));
  R.onTheme(function(t){
    node.replaceChildren.apply(node,series.map(function(s){
      var span=R.el('span',null,''),key=R.el('i','key sq','');
      key.style.background=t[s.color];span.appendChild(key);
      span.appendChild(document.createTextNode(s.name));return span;
    }));
  });
}
document.documentElement.lang=S.metadata.locale;
document.title=S.metadata.title;
document.getElementById('hEyebrow').textContent=S.metadata.eyebrow;
document.getElementById('hTitle').textContent=S.metadata.title;
document.getElementById('hSub').textContent=S.metadata.subtitle;
document.getElementById('hMeta').replaceChildren(text('span',null,L.grain+': '+S.grain));
/* The masthead archetype is a plan choice, and until now it was recorded in the
   spec and never applied — every report rendered as M1 whatever it declared.
   M4 and M5 need content the plan has no field for, so validate-plan.py refuses
   them rather than letting them render as something else. */
var MASTHEADS={M1:'',M2:'masthead--figure',M3:'masthead--broadsheet',M6:'masthead--sticky'};
var header=document.querySelector('.masthead'), archetype=MASTHEADS[S.masthead]||'';
if(header&&archetype)header.classList.add(archetype);
var heroFigure=document.getElementById('hFig');
if(heroFigure){
  var fig=S.masthead==='M2'?S.masthead_figure:null;
  if(fig){
    heroFigure.replaceChildren(document.createTextNode(fig.value),text('small',null,fig.label));
    heroFigure.hidden=false;
  } else { heroFigure.textContent=''; heroFigure.hidden=true; }
}
if(header&&S.masthead==='M6')R.shrinkMasthead(header,140);
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
  var button=add(head,text('button','btn',L.table));button.type='button';button.setAttribute('data-table-toggle','tablewrap-'+chart.id);button.setAttribute('aria-expanded','false');
  add(card,text('p','card-note',chart.note));legendFor(chart,card);
  var chartWrap=add(card,text('div','chart','')),canvas=add(chartWrap,document.createElement('canvas'));
  canvas.id=chart.id;canvas.height=chart.height||240;canvas.setAttribute('role','img');canvas.setAttribute('aria-label',chart.aria_label);canvas.dataset.motionEnabled=String(chart.motion.enabled);canvas.dataset.motionReason=chart.motion.reason;canvas.dataset.motionKind=chart.motion.kind||'entry';canvas.dataset.motionTrigger=chart.motion.trigger||'on-view';canvas.dataset.motionDuration=String(chart.motion.duration_ms||700);canvas.dataset.motionEasing=chart.motion.easing||'outCubic';canvas.dataset.motionSource=chart.motion.source_tool||'motion';canvas.dataset.motionIntegration=toolIntegration(chart.motion.source_tool||'motion');
  var tableWrap=add(card,text('div','tablewrap',''));tableWrap.id='tablewrap-'+chart.id;tableWrap.hidden=true;var table=add(tableWrap,document.createElement('table'));table.id='table-'+chart.id;
  var factory=R.VIZ[chart.type];if(typeof factory!=='function')throw new Error('runtime lacks '+chart.type);factory(canvas,withOptions(chart,chartConfig(chart)));
  R.buildTable(table,chart.table.columns.map(function(field){return {name:field,value:function(row){return format(row[field]);},num:false};}),rows,{caption:chart.title+L.data});
});
var method=add(main,text('section','reveal',''));method.id='methodology';var mh=add(method,text('div','sec-head',''));add(mh,text('p','sec-num',L.method));add(mh,text('h2',null,L.methodTitle));var mc=add(method,text('div','card method',''));
[[L.basis,S.methodology.basis],[L.formulas,S.methodology.formulas],[L.limits,S.methodology.limitations]].forEach(function(group){var block=add(mc,text('div',null,''));add(block,text('h3',null,group[0]));group[1].forEach(function(item){add(block,text('p',null,item));});});
R.wireHelp();R.wireToggles();R.reveal();R.paintAll();
S.charts.forEach(function(chart){
  if(!chart.motion.enabled)return;
  var canvas=document.getElementById(chart.id),engine=canvas&&canvas.__chart;
  if(!engine)return;
  var vendored=canvas.dataset.motionIntegration==='vendored-runtime'&&hasVendoredRuntime(chart.motion.source_tool);
  canvas.__reportReplay=vendored?function(){playVendoredMotion(canvas,engine,chart);}:function(){engine.play(chart.motion.duration_ms||700,chart.motion.easing||'outCubic');};
  R.onView(canvas,canvas.__reportReplay);
});
})();
'''


def build(spec: dict[str, Any], records: list[dict[str, Any]], shell: str) -> str:
    public_spec = {key: spec[key] for key in ("schema_version", "plan_sha256", "metadata", "masthead", "grain", "lenses", "insights", "macro", "theme", "sections", "charts", "methodology", "rule_decisions")}
    if isinstance(spec.get("masthead_figure"), dict):
        public_spec["masthead_figure"] = spec["masthead_figure"]
    if isinstance(spec.get("creative_direction"), dict):
        public_spec["creative_direction"] = spec["creative_direction"]
    payload = script_safe_json({"rows": records, "spec": public_spec})
    data_pattern = re.compile(r'(<script id="report-data" type="application/json">)\s*.*?\s*(</script>)', re.S)
    if len(data_pattern.findall(shell)) != 1:
        raise ValueError("runtime shell must contain exactly one report-data script")
    result = data_pattern.sub(lambda match: match.group(1) + "\n" + payload + "\n" + match.group(2), shell)
    result = inline_vendored_runtimes(result, spec)
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
                        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                        "vendored_runtimes": vendored_runtime_records(spec)}
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
