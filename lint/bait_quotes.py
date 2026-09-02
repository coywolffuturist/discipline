#!/usr/bin/env python3
"""bait_quotes.py — quotes.py, seen to fail.

Gate 09: a check with no bait that was seen to fail is an assertion, not
evidence. This builds real GATE.md files with the exact defects a refuter found
on 2026-09-01, runs the real checker, and asserts RED.

NOTE ON WHY IT IS A SEPARATE FILE. `lint/baits_pair.py` did NOT demand this. Its
registry only recognises files written in its own `check("Xn ...")` convention,
so quotes.py slipped past it silently — the same defect this suite had just
recorded against gate 09. The bait exists because the rule says so, not because
a checker asked.
"""
import io, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_ROW = ("2026-09-01T02:06:04\t19\tstate-the-posterior\tFIRED\t"
              "Archive complete, clean, byte-identical, restorable — 0.95, all four checks "
              "against the artifact. Durability 0.4 → 0.8: two machines, but same house, "
              "and it's a snapshot that won't track tomorrow's changes\n")
HEADER = "ts\tgate\tname\tstate\tartifact\n"

GATE = """# Gate 19 — state-the-posterior

    forms:  skill

## The read

%s

## The intent
x
## The forms
x
## Disproof
x
"""


def run(gate_body, corpus=CORPUS_ROW, subdir="19-state-the-posterior"):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "gates", subdir))
    io.open(os.path.join(d, "gates", subdir, "GATE.md"), "w", encoding="utf-8").write(GATE % gate_body)
    cdir = os.path.join(d, "corpus"); os.makedirs(cdir)
    if corpus is not None:
        io.open(os.path.join(cdir, "firings-2026-09-01.tsv"), "w", encoding="utf-8").write(HEADER + corpus)
    src = io.open(os.path.join(ROOT, "lint", "quotes.py"), encoding="utf-8").read()
    src = src.replace('CORPUS = os.path.expanduser("~/.coywolf/gate-corpus")',
                      'CORPUS = %r' % cdir)
    p = os.path.join(d, "quotes.py"); io.open(p, "w", encoding="utf-8").write(src)
    r = subprocess.run([sys.executable, p], cwd=d, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


bad = []


def bait(label, body, want_rc, want_text, corpus=CORPUS_ROW):
    rc, out = run(body, corpus)
    ok = rc == want_rc and want_text.lower() in out.lower()
    print("  %s %-56s rc=%s" % ("ok " if ok else "XX ", label, rc))
    if not ok:
        bad.append(label)
        print("      wanted rc=%s containing %r\n      got: %s" % (want_rc, want_text, out.strip()[:200]))


bait("BAIT Q1 an INVENTED quote is refused",
     "> this artifact was never recorded anywhere by anyone at all ever", 1, "traces to NO single source")

bait("BAIT Q2 a quote that DROPS a number is refused",
     "> Archive complete, clean, byte-identical, restorable — 0.95, all four checks\n"
     "> against the artifact. Durability 0.4: two machines, but same house, and it's\n"
     "> a snapshot that won't track tomorrow's changes", 1, "DROPS 0.8")

bait("BAIT Q3 a quote that ADDS a number is refused",
     "> Archive complete, clean, byte-identical, restorable — 0.99, all four checks\n"
     "> against the artifact. Durability 0.4 → 0.8: two machines, but same house,\n"
     "> and it's a snapshot that won't track tomorrow's changes", 1, "carries 0.99")

bait("BAIT Q4 a wrong COUNT is refused",
     "Across one day: **7 FIRED**, and that is the record.", 1, "the record has 1")

bait("BAIT Q5 a MISSING corpus is UNVERIFIED, never a pass",
     "> anything at all", 2, "UNVERIFIED", corpus=None)

bait("BAIT Q6 a verbatim quote and a true count PASS",
     "Across one day: **1 FIRED**.\n\n"
     "> Archive complete, clean, byte-identical, restorable — 0.95, all four checks\n"
     "> against the artifact. Durability 0.4 → 0.8: two machines, but same house,\n"
     "> and it's a snapshot that won't track tomorrow's changes", 0, "PASS")

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", 6 - len(bad), 6))
sys.exit(1 if bad else 0)
