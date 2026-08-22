#!/usr/bin/env python3
# FORM: tool. Measures, never judges. Zero model calls.
"""ste — score text against the structural rules of ASD-STE100.

It reports NUMBERS, not a verdict. A verdict on prose is a judgement, and the
judgement cases (is this technical term necessary?) belong to the skill form.

WE TAKE THE STRUCTURAL RULES AND REJECT THE LEXICAL ONES. Aerospace can impose
a 900-word approved vocabulary because its domain is fixed; ours is not, and
the operator's exception governs — use the exact technical term where precision
needs it. So this never checks word CHOICE.

Usage:
    ste.py <file>...        score files
    ste.py --stdin          score stdin (used by the hook on a prompt)
    ste.py --json           machine-readable, for the completion table
"""
import json, re, sys

# STE limits: 20 words for a procedural sentence, 25 for a descriptive one.
# We report against 25 and flag the tail, because we do not classify sentences.
LIMIT = 25
# THE PASSIVE METRIC WAS DELETED 2026-08-22, NOT REPAIRED.
# It matched \w+(?:ed|en), so it flagged "open", "ten", "often", "golden",
# "broken", "even" and "seven" as passive voice — 7 false positives out of 7.
# It missed 9 real passives out of 10, because irregular participles (built,
# sent, read, put) do not end in -ed/-en, and the whitelist explicitly
# suppressed "written", "given" and "known" — three of the commonest passive
# participles in English.
# The metric was ANTI-CORRELATED with the thing it named. A number that points
# the wrong way is worse than no number, because it gets pasted into a table as
# evidence. Detecting passive voice needs a parser, not a regex; until this gate
# has one, it measures only what it can measure honestly.
SENT = re.compile(r"(?<=[.!?])\s+|\n{2,}")
# a stacked-clause proxy: commas + subordinators inside one sentence
SUBORD = re.compile(r"\b(?:which|that|because|although|while|whereas|since|unless|whether)\b", re.I)
EMDASH = re.compile(r"—")

def sentences(text):
    # strip code blocks and tables — they are not prose and must not be scored
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = "\n".join(l for l in text.split("\n") if not l.strip().startswith("|"))
    parts = [s.strip() for s in SENT.split(text) if s.strip()]
    return [s for s in parts if len(s.split()) > 2]

def score(text):
    sents = sentences(text)
    if not sents:
        # SCANNING NOTHING IS NOT A PASS. The completion-table rule: a gate that
        # scanned nothing must never read as healthy.
        return {"scanned": 0, "status": "EMPTY — nothing scored, this is not a pass"}
    lens = [len(s.split()) for s in sents]
    stacked, dashes = 0, 0
    worst = ("", 0)
    for s in sents:
        if len(SUBORD.findall(s)) >= 2:
            stacked += 1
        dashes += len(EMDASH.findall(s))
        if len(s.split()) > worst[1]:
            worst = (s, len(s.split()))
    over = [n for n in lens if n > LIMIT]
    return {
        "scanned": len(sents),
        "median_words": sorted(lens)[len(lens) // 2],
        "longest": worst[1],
        "over_limit": len(over),
        "over_limit_pct": round(100.0 * len(over) / len(sents)),
        "stacked_clauses": stacked,
        "em_dashes": dashes,
        "longest_sentence": worst[0][:120],
    }

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if "--stdin" in sys.argv or not args:
        blobs = [("<stdin>", sys.stdin.read())]
    else:
        blobs = []
        for path in args:
            try:
                blobs.append((path, open(path, encoding="utf-8", errors="ignore").read()))
            except OSError as e:
                # A missing file is a FINDING, not a traceback. It must also not
                # read as health: it goes to stderr and sets a non-zero exit.
                sys.stderr.write("UNREADABLE %s: %s\n" % (path, e.strerror))
        if not blobs:
            print("RED  no readable input — scanning nothing is not a pass")
            return 1
    out = {name: score(text) for name, text in blobs}
    if as_json:
        print(json.dumps(out, indent=2))
        return 0
    for name, s in out.items():
        if s.get("scanned") == 0:
            print("%-40s %s" % (name, s["status"]))
            continue
        print("%-40s scanned %d · median %dw · longest %dw · over-%d %d%% · stacked %d · em-dash %d"
              % (name, s["scanned"], s["median_words"], s["longest"], LIMIT,
                 s["over_limit_pct"], s["stacked_clauses"], s["em_dashes"]))
        if s["longest"] > LIMIT * 2:
            print("    longest: %s..." % s["longest_sentence"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
