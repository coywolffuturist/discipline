#!/usr/bin/env python3
"""test_gates.py — every surviving script must be SEEN to go red.

SCOPE SHRANK 2026-08-22. Gate 02's code and hook forms were DELETED after three
refutations, and gate 01's ambiguity signal with them. This file no longer tests
them, because they no longer exist. See gates/02-retrieval-economy/DELETED.md.

WHAT THIS FILE IS NOT. It is not proof the gates work. A refuter wrote 24
mutations against a green 48-test suite and 17 escaped — including the 25-word
limit itself. Passing here means the listed behaviours are present. It does not
mean the code is covered.
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(ROOT, "gates")
STE = os.path.join(G, "01-ste", "ste.py")
LINT = os.path.join(G, "01-ste", "lint_ste.py")
HOOK1 = os.path.join(G, "01-ste", "hook_prompt.py")

results = []

def run(args, stdin=None, env=None):
    return subprocess.run([sys.executable] + args, input=stdin, capture_output=True,
                          text=True, timeout=60, env=env or os.environ.copy())

def check(name, cond, detail=""):
    results.append((name, cond, detail))
    print("%s  %-60s %s" % ("OK " if cond else "XX ", name, detail[:40]))

# ---------- RED PATHS ----------
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "noprose.md"), "w").write("# T\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    r = run([LINT, d])
    check("a no-prose file is RED, not 'GREEN - 0 files'",
          r.returncode == 1 and "NOTHING WAS SCORED" in r.stdout)

with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "long.md"), "w").write(" ".join(["word"] * 60) + ".\n")
    r = run([LINT, d])
    check("a 60-word sentence is RED", r.returncode == 1 and "RED" in r.stdout)

with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "real.md"), "w").write("The gate runs. It scores text.\n")
    os.symlink("/nowhere/gone.md", os.path.join(d, "broken.md"))
    r = run([LINT, d])
    check("a broken symlink is RED, never counted as scored",
          r.returncode == 1 and "UNREADABLE" in r.stdout)

# ---------- GREEN, so RED is not unconditional ----------
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "ok.md"), "w").write("The gate runs. It scores the text.\n")
    r = run([LINT, d])
    check("real short prose is GREEN", r.returncode == 0 and "GREEN" in r.stdout)

r = run([LINT, "app.py"])
check("a code-only changeset is N/A, never a blocked commit",
      r.returncode == 0 and "N/A" in r.stdout and "GREEN" not in r.stdout)

# ---------- the splitter ----------
with tempfile.TemporaryDirectory() as d:
    body = "The gate runs. It scores the text. The score goes in the table."
    open(os.path.join(d, "p.md"), "w").write(body + "\n")
    open(os.path.join(d, "b.md"), "w").write(
        "**The gate runs.** **It scores the text.** **The score goes in the table.**\n")
    a = run([STE, os.path.join(d, "p.md"), "--json"])
    b = run([STE, os.path.join(d, "b.md"), "--json"])
    try:
        na = json.loads(a.stdout)[os.path.join(d, "p.md")]["scanned"]
        nb = json.loads(b.stdout)[os.path.join(d, "b.md")]["scanned"]
    except Exception:
        na, nb = 0, -1
    check("bold sentences split the same as plain", na == nb == 3, "%s vs %s" % (na, nb))

with tempfile.TemporaryDirectory() as d:
    items = ["Read the file", "Score the prompt", "Put the number in the table"]
    open(os.path.join(d, "n.md"), "w").write("\n".join("- " + i for i in items) + "\n")
    r = run([LINT, os.path.join(d, "n.md")])
    check("a bullet list without periods is not one long sentence", r.returncode == 0)

r = run([STE, "--stdin", "--json"], stdin="Do it at 3 a.m. and check e.g. the log.\n")
try: n = json.loads(r.stdout)["<stdin>"]["scanned"]
except Exception: n = -1
check("abbreviations do not split a sentence", n == 1, "scanned=%s" % n)

r = run([STE, "--stdin", "--json"],
        stdin="---\nname: x\ndesc: " + ("word " * 60) + "\n---\n\nThe gate runs. It works.\n")
try: n = json.loads(r.stdout)["<stdin>"]["longest"]
except Exception: n = 99
check("YAML frontmatter is not scored as prose", n < 10, "longest=%s" % n)

# ---------- hostile input ----------
r = run([STE, "/nonexistent/file.md"])
check("a missing file does not traceback", "Traceback" not in r.stderr)
r = run([STE, "--stdin"], stdin="")
check("empty stdin does not crash", r.returncode == 0 and "Traceback" not in r.stderr)

for shape in ("[]", "null", "123", '"str"', '{"tool_name":"Task","tool_input":"p"}',
              '{"tool_name":"Task","tool_input":{"prompt":["a","b"]}}', "not json"):
    r = run([HOOK1], stdin=shape)
    check("hook fails OPEN on %s" % shape[:26], r.returncode == 0)

# ---------- the advisory reaches a channel the model reads ----------
r = run([HOOK1], stdin=json.dumps({"tool_name": "Task",
        "tool_input": {"prompt": " ".join(["word"] * 200) + "."}}))
ok = False
try:
    ok = "additionalContext" in (json.loads(r.stdout).get("hookSpecificOutput") or {})
except Exception:
    pass
check("the advisory uses additionalContext, not permissionDecisionReason", ok)

# ---------- deleted things must stay deleted ----------
r = run([STE, "--stdin", "--json"], stdin="The door is open. Run this script now.\n")
check("the anti-correlated passive metric is GONE", "passive" not in r.stdout)
check("the anti-correlated ambiguity signal is GONE", "ambiguity" not in r.stdout)
check("gate 02's leaking code+hook forms are GONE",
      not os.path.exists(os.path.join(G, "02-retrieval-economy", "hook_corpus_read.py"))
      and os.path.exists(os.path.join(G, "02-retrieval-economy", "DELETED.md")))

bad = [n for n, ok, _ in results if not ok]
print("\n%s  %d/%d" % ("TESTS PASS" if not bad else "TESTS FAIL", len(results) - len(bad), len(results)))
for n in bad:
    print("   failed: %s" % n)
sys.exit(1 if bad else 0)
