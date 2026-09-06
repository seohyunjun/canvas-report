#!/usr/bin/env python3
"""Validate a declarative Canvas Report plan and write its verified specification."""
import argparse, hashlib, json, sys
from pathlib import Path

VERSION="1.0"; RETRY=("Local Fix","Component Rebuild","Simplify","Drop Unsupported Section")
THEMES=(
 {"id":"almanac","paper_band":"light","display_class":"humanist-sans","accent_hue":"cool"},{"id":"specimen","paper_band":"light","display_class":"high-contrast-serif","accent_hue":"warm"},{"id":"newsprint","paper_band":"light","display_class":"roman-serif","accent_hue":"warm"},{"id":"cobalt","paper_band":"light","display_class":"techno-grotesk","accent_hue":"cool"},{"id":"grid","paper_band":"light","display_class":"neo-grotesk","accent_hue":"warm"},{"id":"terminal","paper_band":"dark","display_class":"mono","accent_hue":"green"},{"id":"lumen","paper_band":"dark","display_class":"classical-serif","accent_hue":"warm"},{"id":"garden","paper_band":"light","display_class":"roman-serif","accent_hue":"green"},{"id":"carnival","paper_band":"light","display_class":"display-heavy","accent_hue":"warm"},{"id":"riso","paper_band":"light","display_class":"reverse-pair","accent_hue":"cool"})
EXEC=("html","javascript","script","onload","onclick","onerror","eval","function")
CHARTS={"line":("x","value"),"columns":("x","value"),"divColumns":("label","value"),
 "hbars":("label","value"),"lollipop":("label","value"),"bubbles":("label","x","y","size"),
 "concentration":("label","value")}
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
 return {"lenses":lens,"macros":macros,"themes":list(THEMES)}
def history(h,k):
 rows=h if isinstance(h,list) else h.get("runs",[]) if isinstance(h,dict) else []
 for x in reversed(rows):
  if isinstance(x,dict) and isinstance(x.get(k),str):return x[k]
 return h.get(k) if isinstance(h,dict) and isinstance(h.get(k),str) else None
def distance(a,b):return sum(a[k]!=b[k] for k in ("paper_band","display_class","accent_hue"))
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
 if theme not in tm:d.e("THEME-001","plan.theme","Theme is not in the canonical catalogue.","Use one of almanac, specimen, newsprint, cobalt, grid, terminal, lumen, garden, carnival, riso.")
 explicit=requirements.get("theme")
 if explicit is not None and explicit != theme:d.e("THEME-003","plan.requirements.theme","Explicit theme requirement does not match plan.theme.","Set plan.theme to the requested compatible theme or remove the override.")
 if explicit is not None and explicit not in tm:d.e("THEME-004","plan.requirements.theme","Explicit theme requirement is not in the canonical compatible catalogue.","Choose a canonical theme or remove the override.")
 allowed_themes={x.get("id") for x in candidate_artifact.get("themes",[]) if isinstance(x,dict) and x.get("compatible") is True and x.get("rotation_excluded") is not True}
 if theme not in allowed_themes:d.e("THEME-002","plan.theme","Theme is incompatible or excluded by the authenticated candidate set.","Choose a compatible non-excluded theme or record a compatible explicit override in requirements.")
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
  for f in x["fields"]+x["table"]["columns"]:
   if f not in names:d.e("CHART-003",l,"Chart field %s is not profiled."%f,"Use source column names.")
  for role,f in x["encodings"].items():
   if not isinstance(f,str) or f not in names:d.e("CHART-006",l+".encodings."+role,"Encoding references an unprofiled field.","Use a field from profile.columns.")
 meth=req(plan,"methodology",dict,"plan",d) or {}
 for k in ("basis","formulas","limitations"):
  if not arr(meth.get(k)) or not meth[k]:d.e("METHOD-001","plan.methodology."+k,"Methodology %s must be a nonempty string array."%k,"Document it explicitly.")
 rules=read(Path(__file__).parent.parent/"references/rules.json","rules",d);known={x.get("id") for x in rules.get("rules",[]) if isinstance(x,dict)}; decisions=req(plan,"rule_decisions",list,"plan",d) or []
 if not decisions:d.e("RULE-001","plan.rule_decisions","At least one Rule-ID decision is required.","Record applicable canonical rule decisions.")
 for i,x in enumerate(decisions):
  if not isinstance(x,dict) or x.get("rule_id") not in known or not isinstance(x.get("decision"),str) or not x["decision"]:d.e("RULE-002","plan.rule_decisions[%d]"%i,"Decision needs a canonical Rule-ID and nonempty decision.","Use references/rules.json ids.")
 if not d.bad():
  canonical=json.dumps(plan,ensure_ascii=False,sort_keys=True,separators=(",",":"));spec={"schema_version":VERSION,"source":{"path":source["path"],"sha256":sha},"plan_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"metadata":meta,"masthead":plan["masthead"],"grain":plan["grain"],"candidates":cand,"lenses":ld,"insights":insights,"macro":macro,"theme":theme,"sections":sections,"charts":charts,"methodology":meth,"rule_decisions":decisions,"retry_policy":{"max_attempts":4,"steps":list(RETRY)},"ownership":{"writable":["report content","sections","charts","methodology","rule decisions"],"immutable":["runtime engines","generated HTML","builder"]}}
  Path(a.output).write_text(json.dumps(spec,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"diagnostics":d.x},ensure_ascii=False,sort_keys=True));return 1 if d.bad() else 0
if __name__=="__main__":sys.exit(main())
