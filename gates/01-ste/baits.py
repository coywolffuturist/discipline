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
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "long.md"), "w").write(" ".join(["word"] * 60) + ".\n")
    rc, out = lint(d)
    check("BAIT S3 a 60-word sentence makes the gate RED", rc == 1 and "RED" in out)

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

bad = [l for l, ok in results if not ok]
print("\n%s  %d/%d" % ("BAITS PASS" if not bad else "BAITS FAIL",
                       len(results) - len(bad), len(results)))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
