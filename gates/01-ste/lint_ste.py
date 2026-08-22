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
# S3 SAYS "a sentence over the word limit is RED". Until 2026-08-22 that was
# FALSE. The gate red-ed on MEDIAN and on PERCENTAGE, so two short sentences of
# padding hid a sentence of any length: it measured longest=300 and printed
# "all within the structural limits". Measured on real canon, 118 of 600 GREEN
# files held a sentence over 50 words. Every one was told it was within limits.
#
# The per-sentence rule is now the PRIMARY rule, because it is the one declared.
# MEDIAN_MAX is 25, not 24 — the old 24 red-ed a file of exactly-25-word
# sentences while reporting over_limit=0, an off-by-one against LIMIT itself.
LIMIT_REF  = 25          # the STE descriptive limit, used in messages
HARD_LIMIT = 60          # no single sentence may exceed this, ever
MEDIAN_MAX = 25          # matches LIMIT; was 24, which contradicted it
OVER_PCT_MAX = 50
# One ambiguity signal per three sentences is dense. Deliberately loose: these
# are SIGNALS, not a detector, so the threshold must not manufacture false reds.

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
        why = []
        if s["longest"] > HARD_LIMIT:
            why.append("a %dw sentence (hard limit %d)" % (s["longest"], HARD_LIMIT))
        if s["median_words"] > MEDIAN_MAX:
            why.append("median %dw" % s["median_words"])
        if s["over_limit_pct"] > OVER_PCT_MAX:
            why.append("%d%% over %dw" % (s["over_limit_pct"], LIMIT_REF))
        if why:
            s["_why"] = "; ".join(why)
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
        print("  RED  %-34s %s" % (os.path.basename(name), s["_why"]))
    if unreadable:
        print("VERDICT: RED — %d file(s) unreadable. An unread file is never a pass."
              % len(unreadable))
        return 1
    if bad:
        print("VERDICT: RED — %d file(s) exceed the structural limits." % len(bad))
        print("         Shorten sentences. One idea each. Exact technical terms stay.")
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
    # The GREEN line must state the PROPOSITION IT CHECKED, not a broader one.
    # "all within the structural limits" was a claim the gate had not tested.
    print("VERDICT: GREEN — %d file(s) scored; no sentence over %dw, median <= %dw."
          % (scored, HARD_LIMIT, MEDIAN_MAX))
    if empty:
        print("         NOTE: %d file(s) held no prose and were NOT scored." % len(empty))
    return 0

if __name__ == "__main__":
    sys.exit(main())
