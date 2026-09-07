#!/usr/bin/env python3
"""Validate a declarative Canvas Report plan and write its verified specification."""
import argparse, hashlib, json, sys
from pathlib import Path

VERSION="1.0"; RETRY=("Local Fix","Component Rebuild","Simplify","Drop Unsupported Section")
ROOT=Path(__file__).resolve().parent.parent
CATALOGUE=ROOT/"references/themes.json"
AXES=("paper_band","display_class","accent_hue")
def catalogue():
 # A missing catalogue must reach the reader as THEME-CATALOGUE-001, not as an
 # import-time traceback with no diagnostic envelope around it.
 try:rows=json.loads(CATALOGUE.read_text(encoding="utf-8")).get("themes",[])
 except (OSError,ValueError):return ()
 return tuple(x for x in rows if isinstance(x,dict) and all(k in x for k in ("id",)+AXES))
THEMES=catalogue()
EXEC=("html","javascript","script","onload","onclick","onerror","eval","function")
CHARTS={"line":("x","value"),"columns":("x","value"),"divColumns":("label","value"),
 "hbars":("label","value"),"lollipop":("label","value"),"bubbles":("label","x","y","size"),
 "concentration":("label","value")}
# The runtime refuses to draw past these and prints a message instead of the data
# (assets/report-shell.html, VIZ.lollipop). The builder hands every source row to
# every chart, so the cap is a plan-time incompatibility, not a rendering detail.
MAX_ROWS={"lollipop":20}
MOTION_EASINGS={"linear","outCubic","inOutCubic","outQuint","outExpo","outCirc","inOutQuint"}
TOOLS={"d3-gallery","d3","plotly","gsap","motion","anime"}
TOOL_ROLES={"chart-form","data-transform","state-model","motion-engine","illustration"}
MOTION_TOOLS={"gsap","motion","anime"}
# What c.t scales differs per factory, so the curve that keeps a mark honest differs
# too. A reveal (line, concentration) can afford a steady curve; a value-scaled mark
# reads a number smaller than the datum for the whole run and needs one that arrives
# early. references/motion-features.md carries the reasoning; these are the bands.
MOTION_FIT={
 "line":({"outCubic","linear"},(600,800)),
 "concentration":({"outCubic","linear"},(600,800)),
 "columns":({"outQuint","outExpo"},(400,600)),
 "divColumns":({"outQuint","outExpo"},(400,600)),
 "hbars":({"outQuint","outExpo"},(400,600)),
 "lollipop":({"outQuint","outExpo"},(400,600)),
 "bubbles":({"outExpo","outQuint"},(700,900)),
}
# The portable path runs through the shell's anim(), which caps at 900 ms. Nothing
# downstream reports the difference: the motion gate reads the declared attribute,
# so a longer declaration passes every check and still runs for 900.
PORTABLE_CEILING_MS=900
class D:
 def __init__(s):s.x=[]
 def add(s,se,i,l,p,f):s.x.append({"severity":se,"id":i,"location":l,"problem":p,"suggested_fix":f})
 def e(s,*a):s.add("error",*a)
 def w(s,*a):s.add("warning",*a)
 def bad(s):return any(x["severity"]=="error" for x in s.x)
def read(p,label,d):
 try:
  x=json.loads(Path(p).read_text(encoding="utf-8"))
  if isinstance(x,dict):return x
  d.e("JSON-002",label,"Root is not a JSON object.","Supply an object.")
 except (OSError,json.JSONDecodeError) as e:d.e("JSON-001",label,"Cannot read valid JSON: %s"%e,"Supply readable valid JSON.")
 return {}
def badfields(x,l,d):
 if isinstance(x,dict):
  for k,v in x.items():
   if any(q in k.lower() for q in EXEC):d.e("SECURITY-001",l+"."+k,"Executable HTML/JavaScript fields are prohibited.","Use declarative source data only.")
   badfields(v,l+"."+k,d)
 elif isinstance(x,list):
  for i,v in enumerate(x):badfields(v,"%s[%d]"%(l,i),d)
def arr(x):return isinstance(x,list) and all(isinstance(v,str) and v for v in x)
def req(x,k,t,l,d):
 v=x.get(k)
 if not isinstance(v,t):d.e("PLAN-001",l+"."+k,"Required %s is missing or has the wrong type."%k,"Provide %s as %s."%(k,t.__name__))
 return v
def compatible(p,r,n):
 cols=p.get("columns",[]); nums=sum(c.get("type") in ("integer","number","float","numeric") for c in cols if isinstance(c,dict)); dims=sum(c.get("type") in ("string","categorical","boolean") for c in cols if isinstance(c,dict)); dates=p.get("date_columns",[]); keys=p.get("candidate_keys",[])
 lens=[]
 if nums and any(isinstance(c,dict) and c.get("name") in dates and c.get("distinct_count",0)>=6 for c in cols):lens.append("trend")
 if nums and dims:lens += ["comparison","ranking"]
 if nums:lens.append("distribution")
 if nums>=2:lens.append("relationship")
 if nums and dims:lens.append("composition")
 if keys and dates:lens.append("cohort")
 macros=["Briefing","Broadsheet"]
 if nums>=8:macros.append("Ledger")
 if r.get("staged_subject") is True and isinstance(r.get("stage_count"),int) and r["stage_count"]>=4:macros.append("Scrolly")
 if dims>=3:macros.append("Workbench")
 if isinstance(r.get("homogeneous_series_count"),int) and r["homogeneous_series_count"]>=12:macros.append("Poster")
 if 5<=n<=8:macros.append("Deck")
 if keys and dates and any(isinstance(c,dict) and c.get("name") in dates and c.get("distinct_count",0)>=2 for c in cols):macros.append("Bridge")
 if r.get("comparable_sets")==2:macros.append("Spread")
 if r.get("qualitative_notes") is True:macros.append("Fieldnotes")
 return {"lenses":lens,"macros":macros,"themes":[{k:t[k] for k in ("id",)+AXES} for t in THEMES]}
def history(h,k):
 rows=h if isinstance(h,list) else h.get("runs",[]) if isinstance(h,dict) else []
 for x in reversed(rows):
  if isinstance(x,dict) and isinstance(x.get(k),str):return x[k]
 return h.get(k) if isinstance(h,dict) and isinstance(h.get(k),str) else None
def distance(a,b):return sum(a[k]!=b[k] for k in AXES)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--profile",required=True);ap.add_argument("--plan",required=True);ap.add_argument("--candidates",required=True);ap.add_argument("--requirements");ap.add_argument("--output",required=True);ap.add_argument("--history");a=ap.parse_args();d=D()
 Path(a.output).unlink(missing_ok=True)
 p=read(a.profile,"profile",d);plan=read(a.plan,"plan",d);candidate_artifact=read(a.candidates,"candidates",d);requirements=read(a.requirements,"requirements",d) if a.requirements else {};h=read(a.history,"history",d) if a.history else {};badfields(plan,"plan",d)
 source=p.get("source",{}); sha=source.get("sha256") if isinstance(source,dict) else None
 profile_artifact_sha=hashlib.sha256(Path(a.profile).read_bytes()).hexdigest() if Path(a.profile).is_file() else None
 requirements_sha=hashlib.sha256(Path(a.requirements).read_bytes()).hexdigest() if a.requirements and Path(a.requirements).is_file() else hashlib.sha256(b"{}").hexdigest()
 if p.get("schema_version")!=VERSION:d.e("PROFILE-001","profile.schema_version","Unsupported profile schema version.","Use schema_version 1.0.")
 if not isinstance(source.get("path") if isinstance(source,dict) else None,str) or not isinstance(sha,str) or len(sha)!=64:d.e("PROFILE-002","profile.source","Profile requires source.path and 64-character source.sha256.","Regenerate the profile from source data.")
 if plan.get("schema_version")!=VERSION:d.e("PLAN-002","plan.schema_version","Unsupported plan schema version.","Use schema_version 1.0.")
 if plan.get("profile_sha256")!=profile_artifact_sha:d.e("PLAN-003","plan.profile_sha256","Plan SHA does not match the profile artifact SHA.","Hash profile.json exactly and copy that SHA-256.")
 if candidate_artifact.get("profile_sha256")!=profile_artifact_sha or candidate_artifact.get("requirements_sha256")!=requirements_sha:d.e("CANDIDATE-001","candidates","Candidate artifact is stale or belongs to different inputs.","Regenerate candidates from this profile and requirements file.")
 meta=req(plan,"metadata",dict,"plan",d) or {}
 for k in ("title","subtitle","eyebrow","locale"):
  if not isinstance(meta.get(k),str) or not meta[k]:d.e("META-001","plan.metadata."+k,"Metadata %s must be a nonempty string."%k,"Provide reader-facing metadata.")
 for k in ("masthead","grain"):
  if not isinstance(req(plan,k,str,"plan",d),str) or not plan.get(k):d.e("PLAN-004","plan."+k,"%s must be nonempty."%k,"Provide it explicitly.")
 ld=req(plan,"lenses",dict,"plan",d) or {}; sel=ld.get("selected");rej=ld.get("rejected")
 if not arr(sel) or not sel:d.e("LENS-001","plan.lenses.selected","Select one or more unique lenses.","Use compatible generated candidates.")
 if not arr(rej):d.e("LENS-002","plan.lenses.rejected","Rejected lenses must be a string array.","Use [] when none are rejected.")
 cand=compatible(p,requirements,len(plan.get("insights",[]) if isinstance(plan.get("insights"),list) else []))
 allowed_lenses={x.get("id") for x in candidate_artifact.get("lenses",[]) if isinstance(x,dict) and x.get("eligible") is True}
 for v in (sel or []):
  if v not in allowed_lenses:d.e("LENS-003","plan.lenses.selected","%s is incompatible with the authenticated candidate set."%v,"Choose an eligible generated candidate.")
 if set(sel or [])&set(rej or []):d.e("LENS-004","plan.lenses","A lens is both selected and rejected.","Make each decision once.")
 insights=req(plan,"insights",list,"plan",d) or []; ids=set()
 for i,x in enumerate(insights):
  l="plan.insights[%d]"%i
  if not isinstance(x,dict) or not all(isinstance(x.get(k),str) and x[k] for k in ("id","claim","limitation")) or not arr(x.get("evidence_fields")):d.e("INSIGHT-001",l,"Insight needs id, falsifiable claim, evidence_fields, and limitation.","Cite profile fields and state uncertainty.");continue
  if x["id"] in ids:d.e("INSIGHT-002",l+".id","Insight ids must be unique.","Use a distinct id.")
  ids.add(x["id"])
 if len(insights)>6:d.w("INSIGHT-003","plan.insights","More than six insights can dilute the report.","Keep only independently evidenced insights; no minimum count is imposed.")
 macro=req(plan,"macro",str,"plan",d); theme=req(plan,"theme",str,"plan",d)
 allowed_macros={x.get("id") for x in candidate_artifact.get("macros",[]) if isinstance(x,dict) and x.get("compatible") is True and x.get("rotation_excluded") is not True}
 if macro not in allowed_macros:d.e("MACRO-001","plan.macro","Macro is incompatible or excluded by the authenticated candidate set.","Choose a compatible non-excluded macro candidate.")
 tm={x["id"]:x for x in THEMES}
 if not tm:d.e("THEME-CATALOGUE-001","references/themes.json","Theme catalogue is empty or unreadable.","Restore references/themes.json; selection cannot proceed without it.")
 if theme not in tm:d.e("THEME-001","plan.theme","Theme is not in the canonical catalogue.","Use an id from references/themes.json (%d themes)."%len(tm))
 explicit=requirements.get("theme")
 if explicit is not None and explicit != theme:d.e("THEME-003","plan.requirements.theme","Explicit theme requirement does not match plan.theme.","Set plan.theme to the requested compatible theme or remove the override.")
 if explicit is not None and explicit not in tm:d.e("THEME-004","plan.requirements.theme","Explicit theme requirement is not in the canonical compatible catalogue.","Choose a canonical theme or remove the override.")
 theme_rows={x.get("id"):x for x in candidate_artifact.get("themes",[]) if isinstance(x,dict)}
 allowed_themes={i for i,x in theme_rows.items() if x.get("compatible") is True and x.get("rotation_excluded") is not True}
 if theme not in allowed_themes:d.e("THEME-002","plan.theme","Theme is incompatible or excluded by the authenticated candidate set.","Choose a compatible non-excluded theme or record a compatible explicit override in requirements.")
 # ── the theme is fitted to the dataset before it is rotated ──────────────────
 # The rationale is checked against the candidate artifact rather than read as
 # prose: a plan cannot claim a subject match the profile does not evidence.
 chosen=theme_rows.get(theme,{})
 rationale=plan.get("theme_rationale")
 if not isinstance(rationale,dict):
  d.e("THEME-FIT-002","plan.theme_rationale","No theme rationale was recorded.","State the dataset subject, the signals that evidenced it, the candidate fit_score, and the rotation distance.")
 else:
  if not isinstance(rationale.get("subject"),str) or not rationale["subject"]:
   d.e("THEME-FIT-002","plan.theme_rationale.subject","Theme rationale needs the dataset subject in the report's own words.","Name what the data is about, not what the theme looks like.")
  signals=rationale.get("signals")
  if not arr(signals) or not signals:
   d.e("THEME-FIT-002","plan.theme_rationale.signals","Theme rationale needs the subject signals it relied on.","List the matched column-name or requirement tokens from the candidate artifact.")
  else:
   evidenced=set(candidate_artifact.get("subject_signals",[]))|set(chosen.get("fit_matched",[]))
   unknown=[v for v in signals if v not in evidenced]
   if unknown:d.e("THEME-FIT-004","plan.theme_rationale.signals","Signals absent from the candidate artifact: "+", ".join(sorted(unknown)[:6])+".","Cite only tokens the profile and requirements actually produced.")
  for key,expected in (("fit_score",chosen.get("fit_score")),("rotation_distance",chosen.get("rotation_distance"))):
   given=rationale.get(key)
   if isinstance(given,bool) or not isinstance(given,(int,float)):
    d.e("THEME-FIT-002","plan.theme_rationale."+key,"%s must be the number the candidate artifact computed."%key,"Copy it from the theme row in candidates.json.")
   elif expected is not None and abs(float(given)-float(expected))>1e-6:
    d.e("THEME-FIT-003","plan.theme_rationale."+key,"Recorded %s %s does not match the candidate artifact's %s."%(key,given,expected),"Copy the value instead of estimating it.")
  better=sorted(((theme_rows[i].get("fit_score") or 0,i) for i in allowed_themes if i!=theme),reverse=True)
  if (chosen.get("fit_score") or 0)==0 and better and better[0][0]>=0.4:
   d.w("THEME-FIT-001","plan.theme","The chosen theme matches nothing in the dataset's subject; %s scores %.2f and is also compatible."%(better[0][1],better[0][0]),"Prefer the fitted theme, or record why this subject is better served by a neutral face.")
 selected_tool_names=set();tool_integration={};creative=plan.get("creative_direction")
 if creative is None:
  d.e("CREATIVE-DIRECTION-001","plan.creative_direction","No report-level creative direction was recorded.","Add concept, hierarchy, selected external tools, and a restrained motion story.")
 elif not isinstance(creative,dict):
  d.e("CREATIVE-DIRECTION-002","plan.creative_direction","Creative direction must be an object.","Provide concept, hierarchy, external_tools, and motion_story fields.")
 else:
  for k in ("concept","hierarchy"):
   if not isinstance(creative.get(k),str) or not creative[k]:d.e("CREATIVE-DIRECTION-003","plan.creative_direction."+k,"Creative direction %s must be nonempty."%k,"Describe the report-specific visual decision.")
  selected_tools=creative.get("external_tools")
  if not isinstance(selected_tools,list) or not selected_tools or len(selected_tools)>3:
   d.e("TOOL-SELECTION-001","plan.creative_direction.external_tools","Select one to three external tool influences.","Choose one chart/state source and at most one primary motion source from references/external-tools.md.")
  else:
   motion_sources=0;chart_sources=0
   for i,item in enumerate(selected_tools):
    location="plan.creative_direction.external_tools[%d]"%i
    if not isinstance(item,dict) or item.get("tool") not in TOOLS or item.get("role") not in TOOL_ROLES or item.get("integration") not in ("portable-pattern","vendored-runtime") or not isinstance(item.get("reason"),str) or not item["reason"]:
     d.e("TOOL-SELECTION-002",location,"Tool selection needs a known tool, role, integration mode, and reason.","Use the selection contract in references/external-tools.md.")
     continue
    selected_tool_names.add(item["tool"]);tool_integration[item["tool"]]=item["integration"]
    if item["role"]=="motion-engine":motion_sources+=1
    if item["role"] in ("chart-form","data-transform","state-model"):chart_sources+=1
    if item["role"]=="motion-engine" and item["tool"] not in MOTION_TOOLS:
     d.e("TOOL-MOTION-001",location+".tool","A visualization or state-model tool was classified as a motion engine.","Use GSAP, Motion, or anime.js as the motion engine; keep D3 and Plotly in chart/state roles.")
    if item["integration"]=="vendored-runtime" and not (item["tool"] in MOTION_TOOLS and item["role"]=="motion-engine"):
     d.e("TOOL-RUNTIME-001",location+".integration","The deterministic builder only vendors dedicated motion engines for chart entry.","Use GSAP, Motion, or anime.js as the vendored motion-engine, or use portable-pattern for visualization tools.")
   if motion_sources>1:d.e("TOOL-SELECTION-003","plan.creative_direction.external_tools","More than one primary motion source creates competing motion systems.","Keep at most one motion-engine selection.")
   if chart_sources<1:d.e("TOOL-SELECTION-004","plan.creative_direction.external_tools","No chart or state source was selected.","Select D3 gallery, D3, or Plotly for a chart-form, data-transform, or state-model role.")
  story=creative.get("motion_story")
  if not isinstance(story,dict) or not all(isinstance(story.get(k),str) and story[k] for k in ("goal","restraint")) or not arr(story.get("sequence")):
   d.e("MOTION-STORY-001","plan.creative_direction.motion_story","Motion story needs goal, nonempty sequence, and restraint.","Describe one reading sequence before assigning chart motion.")
 sections=req(plan,"sections",list,"plan",d) or []; sids=set()
 for i,x in enumerate(sections):
  if not isinstance(x,dict) or not all(isinstance(x.get(k),str) and x[k] for k in ("id","title","lede")):d.e("SECTION-001","plan.sections[%d]"%i,"Section needs id, title, and lede.","Provide rich reader-facing section content.")
  elif x["id"] in sids:d.e("SECTION-002","plan.sections[%d].id"%i,"Section id repeats.","Use a unique id.")
  else:sids.add(x["id"])
 charts=req(plan,"charts",list,"plan",d) or []; names={x.get("name") for x in p.get("columns",[]) if isinstance(x,dict)}
 for i,x in enumerate(charts):
  l="plan.charts[%d]"%i
  if not isinstance(x,dict) or not all(isinstance(x.get(k),str) and x[k] for k in ("id","section_id","type","title","note","aria_label","help")) or x.get("dataset")!="source" or not arr(x.get("fields")) or not isinstance(x.get("encodings"),dict) or not x["encodings"] or not isinstance(x.get("table"),dict) or not arr(x["table"].get("columns")) or not isinstance(x.get("motion"),dict) or not isinstance(x["motion"].get("enabled"),bool) or not isinstance(x["motion"].get("reason"),str) or not x["motion"].get("reason"):d.e("CHART-001",l,"Chart must be declarative with rich labels, source dataset, encodings, table columns, and explicit motion.","Complete every required chart field.");continue
  if x["section_id"] not in sids:d.e("CHART-002",l+".section_id","Chart references no declared section.","Use a section id.")
  if x["type"] not in CHARTS:d.e("CHART-004",l+".type","Chart type is outside the deterministic builder vocabulary.","Use one of: "+", ".join(CHARTS)+".")
  else:
   missing=[key for key in CHARTS[x["type"]] if not isinstance(x["encodings"].get(key),str) or not x["encodings"][key]]
   if missing:d.e("CHART-005",l+".encodings","Required encodings are missing: "+", ".join(missing)+".","Map each encoding to a profiled field.")
  cap=MAX_ROWS.get(x["type"])
  if cap is not None and isinstance(p.get("row_count"),int) and p["row_count"]>cap:d.e("CHART-007",l+".type","%s draws at most %d marks but the source has %d rows; the runtime would print a message instead of the data."%(x["type"],cap,p["row_count"]),"Simplify to a chart type without a mark cap, such as columns or hbars.")
  for f in x["fields"]+x["table"]["columns"]:
   if f not in names:d.e("CHART-003",l,"Chart field %s is not profiled."%f,"Use source column names.")
  for role,f in x["encodings"].items():
   if not isinstance(f,str) or f not in names:d.e("CHART-006",l+".encodings."+role,"Encoding references an unprofiled field.","Use a field from profile.columns.")
  motion=x["motion"]
  if motion.get("enabled") is True:
   missing=[k for k in ("kind","trigger","duration_ms","easing","source_tool") if k not in motion]
   if missing:d.w("MOTION-CONTRACT-001",l+".motion","Enabled motion omits executable fields: "+", ".join(missing)+".","Set kind entry, trigger on-view, duration_ms 180–1200, a value-safe easing, and the selected source tool.")
   if motion.get("kind","entry")!="entry":d.e("MOTION-CONTRACT-002",l+".motion.kind","The deterministic builder currently supports entry motion only.","Use entry, or switch to a builder/runtime that implements the requested motion kind.")
   if motion.get("trigger","on-view")!="on-view":d.e("MOTION-CONTRACT-003",l+".motion.trigger","The deterministic builder currently supports on-view triggering only.","Use on-view.")
   duration=motion.get("duration_ms",700)
   if not isinstance(duration,int) or isinstance(duration,bool) or not 180<=duration<=1200:d.e("MOTION-CONTRACT-004",l+".motion.duration_ms","Motion duration must be an integer from 180 to 1200 ms.","Choose a bounded duration that resolves without delaying reading.")
   if motion.get("easing","outCubic") not in MOTION_EASINGS:d.e("MOTION-CONTRACT-005",l+".motion.easing","Motion easing is not value-safe.","Use a non-overshooting easing from the plan schema.")
   if motion.get("source_tool") is not None and motion.get("source_tool") not in MOTION_TOOLS:d.e("MOTION-CONTRACT-006",l+".motion.source_tool","Enabled chart motion cites a visualization or state-model tool as its motion engine.","Use GSAP, Motion, or anime.js as source_tool.")
   elif selected_tool_names and motion.get("source_tool") is None:d.e("MOTION-CONTRACT-006",l+".motion.source_tool","Enabled chart motion does not identify its selected external source tool.","Set source_tool to the report-level motion source.")
   elif motion.get("source_tool") is not None and motion["source_tool"] not in selected_tool_names:d.e("MOTION-CONTRACT-006",l+".motion.source_tool","Chart motion cites a tool absent from creative_direction.external_tools.","Select the source tool at report level or use the tool already selected there.")
   # The portable path never sees a duration above the shell's own cap, and no gate
   # downstream compares the two, so an over-long declaration is silently untrue.
   if tool_integration.get(motion.get("source_tool"),"portable-pattern")!="vendored-runtime" and isinstance(duration,int) and not isinstance(duration,bool) and duration>PORTABLE_CEILING_MS:
    d.e("MOTION-PORTABLE-CEILING-001",l+".motion.duration_ms","A portable-pattern chart declares %d ms but the shell's anim() caps at %d; the report would not run for the declared time."%(duration,PORTABLE_CEILING_MS),"Declare %d ms or less, or select the engine as a vendored-runtime."%PORTABLE_CEILING_MS)
   fit=MOTION_FIT.get(x.get("type"))
   if fit and motion.get("easing") in MOTION_EASINGS and isinstance(duration,int) and not isinstance(duration,bool):
    curves,(low,high)=fit
    if motion["easing"] not in curves:
     d.w("MOTION-FIT-001",l+".motion.easing","%s reads better on %s than on %s for a %s."%(x["type"]," or ".join(sorted(curves)),motion["easing"],"reveal" if x["type"] in ("line","concentration") else "value-scaled mark"),"See the per-factory table in references/motion-features.md, or record why this chart differs.")
    if not low<=duration<=high:
     d.w("MOTION-FIT-002",l+".motion.duration_ms","%d ms is outside the %d–%d ms band that suits %s."%(duration,low,high,x["type"]),"Use the recommended band, or record why this chart's reading pace differs.")
 meth=req(plan,"methodology",dict,"plan",d) or {}
 for k in ("basis","formulas","limitations"):
  if not arr(meth.get(k)) or not meth[k]:d.e("METHOD-001","plan.methodology."+k,"Methodology %s must be a nonempty string array."%k,"Document it explicitly.")
 rules=read(Path(__file__).parent.parent/"references/rules.json","rules",d);known={x.get("id") for x in rules.get("rules",[]) if isinstance(x,dict)}; decisions=req(plan,"rule_decisions",list,"plan",d) or []
 if not decisions:d.e("RULE-001","plan.rule_decisions","At least one Rule-ID decision is required.","Record applicable canonical rule decisions.")
 for i,x in enumerate(decisions):
  if not isinstance(x,dict) or x.get("rule_id") not in known or not isinstance(x.get("decision"),str) or not x["decision"]:d.e("RULE-002","plan.rule_decisions[%d]"%i,"Decision needs a canonical Rule-ID and nonempty decision.","Use references/rules.json ids.")
 decision_ids={x.get("rule_id") for x in decisions if isinstance(x,dict)}
 if isinstance(creative,dict) and "MOTION-STORY-001" not in decision_ids:d.e("RULE-003","plan.rule_decisions","Creative direction lacks MOTION-STORY-001 provenance.","Record how the report-level motion sequence was bounded.")
 if "THEME-SELECTION-001" not in decision_ids:d.e("RULE-006","plan.rule_decisions","Theme selection lacks THEME-SELECTION-001 provenance.","Record how compatibility, subject fit, and rotation distance produced this theme.")
 if isinstance(creative,dict) and "TOOL-SELECTION-001" not in decision_ids:d.e("RULE-004","plan.rule_decisions","External tool use lacks TOOL-SELECTION-001 provenance.","Record why the selected toolchain is minimal, useful, and compatible with the build boundary.")
 if any(isinstance(x,dict) and isinstance(x.get("motion"),dict) and x["motion"].get("enabled") is True for x in charts) and "MOTION-INTENT-001" not in decision_ids:d.e("RULE-005","plan.rule_decisions","Enabled chart motion lacks MOTION-INTENT-001 provenance.","Record the reader benefit for enabled chart motion.")
 if not d.bad():
  canonical=json.dumps(plan,ensure_ascii=False,sort_keys=True,separators=(",",":"));spec={"schema_version":VERSION,"source":{"path":source["path"],"sha256":sha},"plan_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"metadata":meta,"masthead":plan["masthead"],"grain":plan["grain"],"candidates":cand,"lenses":ld,"insights":insights,"macro":macro,"theme":theme,"theme_rationale":plan.get("theme_rationale"),"sections":sections,"charts":charts,"methodology":meth,"rule_decisions":decisions,"retry_policy":{"max_attempts":4,"steps":list(RETRY)},"ownership":{"writable":["report content","sections","charts","methodology","rule decisions"],"immutable":["runtime engines","generated HTML","builder"]}}
  if isinstance(creative,dict):spec["creative_direction"]=creative
  Path(a.output).write_text(json.dumps(spec,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"diagnostics":d.x},ensure_ascii=False,sort_keys=True));return 1 if d.bad() else 0
if __name__=="__main__":sys.exit(main())
