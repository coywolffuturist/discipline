#!/usr/bin/env python3
# FORM: code. Exits non-zero. Canon outlives the session.
"""lint_ste.py — gate canon pages and agent definitions at commit time.

A canon page is read months later by an agent with none of the author's
context. That reader is the mechanic in the hangar: it cannot ask what a
sentence meant. So ambiguity in canon is a defect, not a style preference.

SCANNING NOTHING IS RED. Four of seven gates tested on 2026-08-22 returned
exit 0 while scanning nothing, including a scanner that exits 0 by contract
even when broken. This one reports what it scanned and fails on zero.

Usage: lint_ste.py <path>...     paths may be files or directories
"""
import os, sys, glob, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
STE = os.path.join(HERE, "ste.py")
MEDIAN_MAX = 24
OVER_PCT_MAX = 50

def targets(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(glob.glob(p + "/**/*.md", recursive=True))
        elif p.endswith(".md"):
            out.append(p)
    return out

def main():
    paths = sys.argv[1:]
    if not paths:
        print("RED  no path given — a gate that scans nothing is not a pass")
        return 1
    files = targets(paths)
    if not files:
        print("RED  0 files matched %s — scanning nothing is NOT health" % paths)
        return 1
    r = subprocess.run([sys.executable, STE, "--json"] + files,
                       capture_output=True, text=True, timeout=120)
    try:
        scores = json.loads(r.stdout)
    except Exception:
        print("RED  scorer produced no parseable output — treat as blocked")
        return 1
    bad, empty = [], []
    for name, s in scores.items():
        if s.get("scanned", 0) == 0:
            empty.append(name); continue
        if s["median_words"] > MEDIAN_MAX or s["over_limit_pct"] > OVER_PCT_MAX:
            bad.append((name, s))
    print("STE LINT: scanned %d file(s)%s" %
          (len(files), (", %d with no prose" % len(empty)) if empty else ""))
    for name, s in bad:
        print("  RED  %-46s median %dw · %d%% over 25w · longest %dw"
              % (os.path.basename(name), s["median_words"], s["over_limit_pct"], s["longest"]))
    if bad:
        print("VERDICT: RED — %d file(s) exceed the structural limits." % len(bad))
        print("         Shorten sentences. One idea each. Exact technical terms stay.")
        return 1
    print("VERDICT: GREEN — %d file(s) within the structural limits." % (len(files) - len(empty)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
