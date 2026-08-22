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
# One ambiguity signal per three sentences is dense. Deliberately loose: these
# are SIGNALS, not a detector, so the threshold must not manufacture false reds.
# no ambiguity threshold: the signal is reported, never judged (see below)

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
        # N/A, NOT RED — and the distinction is the difference between a usable
        # gate and one that gets disabled on day one. Wired into pre-commit, the
        # old code RED-ed every commit that touched no markdown, i.e. almost
        # every code commit. That is the gate's own trigger not firing, which our
        # three-state rule calls N/A. It still SAYS so; it never passes silently.
        print("N/A  no markdown in %d path(s) given — this gate's trigger is a"
              " prose file, and none was staged." % len(paths))
        return 0
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
        # AMBIGUITY IS REPORTED, NOT JUDGED. A refuter showed the signal both
        # ways round: it RED-ed clear writing ("This parser rejects...") and
        # GREEN-ed genuinely unresolvable scope ("the other one", "theirs").
        # That is the same anti-correlation that got the passive metric deleted,
        # and this one reached the verdict, which is worse. It stays as a
        # measurement until it is proven; it does not decide anything.
        s["_amb_rate"] = s.get("ambiguity_signals", 0) / max(1, s["scanned"])
        if s["median_words"] > MEDIAN_MAX or s["over_limit_pct"] > OVER_PCT_MAX:
            bad.append((name, s))
    # A file ste.py could not open never appears in the JSON at all, so it fell
    # into NEITHER bucket and was counted as SCORED. Measured in the real
    # pre-commit shape: a staged-but-deleted file reported "1 SCORED" while zero
    # sentences were read, and a brand-new markdown file went in on that GREEN.
    unreadable = [f for f in files if f not in scores]
    scored = len([f for f in files if f in scores and scores[f].get("scanned", 0) > 0])
    print("STE LINT: %d given · %d SCORED · %d no-prose · %d UNREADABLE"
          % (len(files), scored, len(empty), len(unreadable)))
    if unreadable:
        print("  RED  %d file(s) could not be read — that is a finding, not a skip:"
              % len(unreadable))
        for f in unreadable[:5]:
            print("       %s" % f)
    for name, s in bad:
        print("  RED  %-40s median %dw · %d%% over 25w · longest %dw · ambiguity %.2f/sentence"
              % (os.path.basename(name), s["median_words"], s["over_limit_pct"],
                 s["longest"], s.get("_amb_rate", 0)))
    if unreadable:
        print("VERDICT: RED — %d file(s) unreadable. An unread file is never a pass."
              % len(unreadable))
        return 1
    if bad:
        print("VERDICT: RED — %d file(s) exceed the structural limits." % len(bad))
        print("         Shorten sentences. One idea each. Exact technical terms stay.")
        print("         Ambiguity signals: sentence-initial pronouns, bare 'do this',")
        print("         and vague scope ('as needed', 'etc'). Name the object instead.")
        return 1
    # THE FOUNDING RULE, and it was broken here until 2026-08-22. The old code
    # put no-prose files in `empty`, never looked at them again, and printed
    # "GREEN — 0 file(s)" with exit 0. A refuter found seven real canon pages
    # that passed this way, including a mermaid diagram. A pre-commit hook wired
    # to it returned green on a commit it never inspected.
    if scored == 0:
        print("VERDICT: RED — NOTHING WAS SCORED. %d file(s) hold no prose "
              "(diagram-only, table-only, or fenced-only)." % len(empty))
        print("         Scanning nothing is not a pass. Name the files or widen the path.")
        for name in empty[:5]:
            print("         no prose: %s" % os.path.basename(name))
        return 1
    amb = sum(v.get("ambiguity_signals", 0) for v in scores.values())
    print("VERDICT: GREEN — %d file(s) scored, all within the structural limits." % scored)
    if amb:
        print("         NOTE: %d ambiguity signal(s) counted, NOT judged — the signal"
              " is not verdict-grade yet." % amb)
    if empty:
        print("         NOTE: %d file(s) held no prose and were NOT scored." % len(empty))
    return 0

if __name__ == "__main__":
    sys.exit(main())
