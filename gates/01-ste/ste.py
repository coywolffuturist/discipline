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
# FINDING 4, closed 2026-08-22. The old splitter broke only on [.!?] or a blank
# line, so a markdown bullet list with no trailing periods parsed as ONE long
# sentence and went RED — while the identical list WITH periods went GREEN. The
# verdict flipped on punctuation the content does not need. A list item is a
# sentence whether or not it ends in a full stop, so the marker itself is a
# boundary. Abbreviations are protected first, or "3 a.m." splits into two.
ABBREV = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf|approx|a\.m|p\.m|Dr|Mr|Ms|St|Fig|No)\.", re.I)
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+", re.M)
HEADING = re.compile(r"^#{1,6}\s+", re.M)
SENT = re.compile(r"(?<=[.!?])\s+|\n{2,}|\x00")
# a stacked-clause proxy: subordinators inside one sentence
SUBORD = re.compile(r"\b(?:which|that|because|although|while|whereas|since|unless|whether)\b", re.I)
EMDASH = re.compile(r"—")

# FINDING 5, closed 2026-08-22. The gate exists because two agents misread their
# SCOPE. That is an ambiguity failure, and the gate measured no proxy for it:
# six unresolvable pronouns scored perfect.
#
# THIS IS A SIGNAL, NOT A DETECTOR. Real reference resolution needs a parser.
# What is counted here is deterministic and checkable:
#   - a sentence-initial pronoun ALWAYS points outside its own sentence
#   - a bare demonstrative ("do this", "fix that") names no object
#   - vague-scope words defer the boundary to the reader, which is the exact
#     move that let an agent stop early and call it done
OPEN_PRONOUN = re.compile(r"^\s*(?:It|This|That|These|Those|They|Them|Its|Their)\b")
BARE_DEM = re.compile(r"\b(?:do|fix|check|run|handle|review|update|address)\s+(?:this|that|it|these|those)\b[^\w]", re.I)
VAGUE = re.compile(r"\b(?:as needed|if necessary|where relevant|as appropriate|"
                   r"and so on|etc\b|various|several|some other|suitable|accordingly|"
                   r"the rest|and more|among others)", re.I)

def sentences(text):
    # strip fenced code and tables — not prose, must not be scored. An UNCLOSED
    # fence used to swallow the rest of the file, so only balanced fences strip.
    if text.count("```") % 2 == 0:
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
    else:
        text = re.sub(r"```[^\n]*", " ", text)
    text = "\n".join(l for l in text.split("\n") if not l.strip().startswith("|"))
    text = ABBREV.sub(lambda m: m.group(0).replace(".", "\x01"), text)   # protect
    text = LIST_MARK.sub("\x00", text)                                   # list item = boundary
    text = HEADING.sub("\x00", text)
    parts = [p.replace("\x01", ".").strip() for p in SENT.split(text) if p.strip()]
    return [p for p in parts if len(p.split()) > 2]

def score(text):
    sents = sentences(text)
    if not sents:
        # SCANNING NOTHING IS NOT A PASS. The completion-table rule: a gate that
        # scanned nothing must never read as healthy.
        return {"scanned": 0, "status": "EMPTY — nothing scored, this is not a pass"}
    lens = [len(s.split()) for s in sents]
    stacked, dashes, openref, bare, vague = 0, 0, 0, 0, 0
    worst = ("", 0)
    for s in sents:
        if len(SUBORD.findall(s)) >= 2:
            stacked += 1
        dashes += len(EMDASH.findall(s))
        if OPEN_PRONOUN.search(s):
            openref += 1
        bare += len(BARE_DEM.findall(s + " "))
        vague += len(VAGUE.findall(s))
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
        "open_reference": openref,
        "bare_demonstrative": bare,
        "vague_scope": vague,
        "ambiguity_signals": openref + bare + vague,
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
        print("%-40s scanned %d · median %dw · longest %dw · over-%d %d%% · stacked %d · ambig %d"
              % (name, s["scanned"], s["median_words"], s["longest"], LIMIT,
                 s["over_limit_pct"], s["stacked_clauses"], s["ambiguity_signals"]))
        if s["longest"] > LIMIT * 2:
            print("    longest: %s..." % s["longest_sentence"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
