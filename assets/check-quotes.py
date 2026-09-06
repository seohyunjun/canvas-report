#!/usr/bin/env python3
"""Verify that every quote in a report's `read:` stamp really appears in the file it cites.

The stamp claims a verbatim fragment from each reference that steered a decision.
A fragment that no longer matches means either the quote was invented or the
reference was edited underneath it — both make the stamp a lie.

    python3 assets/check-quotes.py report.html [more.html ...]

With no arguments it checks every report recorded in .canvas-report/log.json.
Exits non-zero if any quote fails to match.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(HERE, "references")
LINE = re.compile(r'\s*([\w.\-/]+)(?:\s+§(\S+))?\s+"(.+)"\s*$')
BLOCK = re.compile(r'\nread:\n((?:[ \t]+\S.*\n|[ \t]*\n)+)')

def candidates(name):
    """Every reference file a stamp label could mean, most specific first."""
    yield os.path.join(REF, name + ".md")
    yield os.path.join(REF, "macrostructures", name + ".md")
    base = name.split("/")[-1]
    yield os.path.join(REF, "macrostructures", base + ".md")

def resolve(name, frag):
    for c in candidates(name):
        if os.path.exists(c):
            with open(c, encoding="utf-8") as fh:
                if frag in fh.read():
                    return c, True
            return c, False
    for p in sorted(glob.glob(REF + "/**/*.md", recursive=True)):
        with open(p, encoding="utf-8") as fh:
            if frag in fh.read():
                return p, True          # found, but the label points elsewhere
    return None, False

def check(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = BLOCK.search(txt)
    if not m:
        print("  NO STAMP     this file carries no read: block")
        return 0, 0, 1
    ok = bad = 0
    for line in m.group(1).splitlines():
        q = LINE.match(line)
        if not q:
            continue
        name, _sec, frag = q.groups()
        found, matched = resolve(name, frag)
        if matched and found and os.path.basename(found)[:-3] not in (name, name.split("/")[-1]):
            print("  MISLABELLED  %-22s actually in %s"
                  % (name, os.path.relpath(found, HERE)))
            bad += 1
        elif matched:
            ok += 1
        else:
            print("  BROKEN       %-22s %s" % (name, frag[:66]))
            bad += 1
    return ok, bad, 0

def main():
    files = sys.argv[1:]
    if not files:
        log = os.path.join(os.getcwd(), ".canvas-report", "log.json")
        if not os.path.exists(log):
            raise SystemExit(__doc__)
        files = [e["file"] for e in json.load(open(log)) if os.path.exists(e.get("file", ""))]
    tot_ok = tot_bad = tot_none = 0
    for f in files:
        print("== " + os.path.basename(f))
        o, b, n = check(f)
        tot_ok, tot_bad, tot_none = tot_ok + o, tot_bad + b, tot_none + n
    print("\n%d quotes verified, %d broken, %d file(s) with no stamp."
          % (tot_ok, tot_bad, tot_none))
    if tot_bad:
        raise SystemExit("stamp quotes do not match their references")
    if tot_none:
        raise SystemExit("a report built by this skill must carry a read: stamp")

if __name__ == "__main__":
    main()
