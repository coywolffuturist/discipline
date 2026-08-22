#!/usr/bin/env python3
"""baits.py — every check in checks.py, seen to fail.

A bait builds a real input, runs the real gate, and asserts the verdict. It does
NOT test the code by reading it. It tests the gate by using it.

Honest limit, stated the way spirals states its own: this file proves each
condition FIRES. It does not prove the condition is WELL CHOSEN. A bait can be
weak and still pass. What it removes is the silent case, which is a check
nobody ever tried to break.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "lint_ste.py")
results = []

def check(label, cond, detail=""):
    results.append((label, cond))
    print("%s  %-58s %s" % ("OK " if cond else "XX ", label, detail[:34]))

def lint(*args):
    r = subprocess.run([sys.executable, LINT] + list(args),
                       capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout

# ---- S1 ----
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "real.md"), "w").write("The gate runs. It scores text.\n")
    os.symlink("/nowhere/gone.md", os.path.join(d, "broken.md"))
    rc, out = lint(d)
    check("BAIT S1 a broken symlink makes the gate RED", rc == 1 and "UNREADABLE" in out)

# ---- S2 ----
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "t.md"), "w").write("# T\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    rc, out = lint(d)
    check("BAIT S2 a table-only file makes the gate RED", rc == 1 and "NOTHING WAS SCORED" in out)

# ---- S3 ----
# EACH KNOB IS BAITED SEPARATELY. The old bait used one long sentence, so the
# per-sentence rule, the median and the percentage all fired at once. A refuter
# then set every threshold to 100000 and the chain stayed green, because no bait
# could tell which one was alive.
with tempfile.TemporaryDirectory() as d:
    # ONLY the hard per-sentence limit: median tiny, over-pct 33%, one huge line
    open(os.path.join(d, "dilute.md"), "w").write(
        "The gate runs.\nIt works.\n\n" + " ".join(["alpha"] * 300) + ".\n")
    rc, out = lint(os.path.join(d, "dilute.md"))
    check("BAIT S3a padding does NOT hide a long sentence",
          rc == 1 and "hard limit" in out)

with tempfile.TemporaryDirectory() as d:
    # ONLY the median: every sentence 30w, none over the hard limit
    body = " ".join(["word"] * 30) + "."
    open(os.path.join(d, "med.md"), "w").write("\n".join([body] * 4) + "\n")
    rc, out = lint(os.path.join(d, "med.md"))
    check("BAIT S3b a high median alone makes the gate RED",
          rc == 1 and "median" in out)

with tempfile.TemporaryDirectory() as d:
    # the off-by-one: exactly at the limit is NOT over it
    body = " ".join(["word"] * 25) + "."
    open(os.path.join(d, "exact.md"), "w").write("\n".join([body] * 5) + "\n")
    rc, out = lint(os.path.join(d, "exact.md"))
    check("BAIT S3c a sentence exactly AT the limit is not RED", rc == 0)

# ---- S4 ----
rc, out = lint("app.py")
check("BAIT S4 a code-only changeset is N/A, and never GREEN",
      rc == 0 and "N/A" in out and "GREEN" not in out)

# ---- S5 ----
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "ok.md"), "w").write("The gate runs. It scores the text.\n")
    rc, out = lint(d)
    check("BAIT S5 short clear prose is GREEN, so RED is not unconditional",
          rc == 0 and "GREEN" in out)

# ---- S6 ----
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "ok.md"), "w").write("The gate runs. It scores text.\n")
    rc, out = lint(os.path.join(d, "ok.md"))
    check("BAIT S6 the GREEN line states the proposition it CHECKED",
          rc == 0 and "no sentence over" in out and "all within the structural" not in out)

# ---- S7 ----
with tempfile.TemporaryDirectory() as d:
    items = ["Read the staged file from the index",
             "Score every sentence against the limit",
             "Write the number into the completion table"]
    open(os.path.join(d, "bq.md"), "w").write("\n".join("> - " + i for i in items) + "\n")
    open(os.path.join(d, "plain.md"), "w").write("\n".join("- " + i for i in items) + "\n")
    a, _ = lint(os.path.join(d, "bq.md"))
    c, _ = lint(os.path.join(d, "plain.md"))
    check("BAIT S7 a blockquoted list scores like a plain one", a == c == 0,
          "bq=%s plain=%s" % (a, c))

with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "bqt.md"), "w").write(
        "> | a | b |\n> |---|---|\n> | one | two |\n\nThe gate runs.\n")
    rc, out = lint(os.path.join(d, "bqt.md"))
    check("BAIT S7 a blockquoted TABLE is not scored as prose", rc == 0)

bad = [l for l, ok in results if not ok]
print("\n%s  %d/%d" % ("BAITS PASS" if not bad else "BAITS FAIL",
                       len(results) - len(bad), len(results)))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
