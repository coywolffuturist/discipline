#!/usr/bin/env python3
"""test_gates.py — every script must be SEEN to go red, and to survive garbage.

WHY THIS EXISTS. A refuter's sharpest finding, 2026-08-22: a repository whose
whole thesis is "four of seven gates returned exit 0 while scanning nothing"
shipped five scripts with NO test that any of them can fail. Every defect it
found was reachable on the first hostile input tried.

Two things are tested for each script:
  RED PATH    — it fails when it should. A gate never seen to fail is not a gate.
  HOSTILE     — it does not crash on garbage. Four of five crashed before this.

Run: python3 test_gates.py     exit 0 = all pass
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(ROOT, "gates")
STE = os.path.join(G, "01-ste", "ste.py")
LINT = os.path.join(G, "01-ste", "lint_ste.py")
HOOK1 = os.path.join(G, "01-ste", "hook_prompt.py")
HOOK2 = os.path.join(G, "02-retrieval-economy", "hook_corpus_read.py")
REPORT = os.path.join(G, "02-retrieval-economy", "door_report.py")

results = []

def run(args, stdin=None, env=None):
    return subprocess.run([sys.executable] + args, input=stdin, capture_output=True,
                          text=True, timeout=30, env=env or os.environ.copy())

def check(name, cond, detail=""):
    results.append((name, cond, detail))
    print("%s  %-58s %s" % ("OK " if cond else "XX ", name, detail[:60]))

# ---------- RED PATHS ----------
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "noprose.md"), "w").write("# T\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    r = run([LINT, d])
    check("lint: a no-prose file is RED, not 'GREEN — 0 files'",
          r.returncode == 1 and "NOTHING WAS SCORED" in r.stdout)

with tempfile.TemporaryDirectory() as d:
    r = run([LINT, d])
    check("lint: an empty directory is RED", r.returncode == 1)

r = run([LINT])
check("lint: no argument is RED", r.returncode == 1)

with tempfile.TemporaryDirectory() as d:
    long = " ".join(["word"] * 60) + "."
    open(os.path.join(d, "long.md"), "w").write(long + "\n")
    r = run([LINT, d])
    check("lint: a 60-word sentence is RED", r.returncode == 1 and "RED" in r.stdout)

env = os.environ.copy()
env["HOME"] = tempfile.mkdtemp()
r = run([REPORT], env=env)
check("report: a missing door log is RED (hook unregistered)",
      r.returncode == 1 and "not registered" in r.stdout)

# ---------- GREEN PATH, so RED is not trivially always ----------
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "ok.md"), "w").write("The gate runs. It scores the text. The score goes in the table.\n")
    r = run([LINT, d])
    check("lint: real short prose is GREEN (red is not unconditional)",
          r.returncode == 0 and "GREEN" in r.stdout)

# ---------- HOSTILE INPUT: nothing may crash ----------
r = run([STE, "/nonexistent/file.md"])
check("ste: a missing file does not traceback",
      "Traceback" not in r.stderr, r.stderr.strip().split("\n")[-1][:40])

r = run([STE, "--stdin"], stdin="")
check("ste: empty stdin does not crash", r.returncode == 0 and "Traceback" not in r.stderr)

for name, hook in (("hook01", HOOK1), ("hook02", HOOK2)):
    r = run([hook], stdin="not json at all")
    check("%s: non-JSON input fails OPEN" % name, r.returncode == 0)
    r = run([hook], stdin=json.dumps({"tool_name": "Task", "tool_input": {"prompt": ["a", "b"]}}))
    check("%s: a non-string prompt fails OPEN (contract)" % name,
          r.returncode == 0 and "Traceback" not in r.stderr)

r = run([REPORT, "--since-hours"])
check("report: a flag with no value does not traceback", "Traceback" not in r.stderr)
r = run([REPORT, "--since-hours", "abc"])
check("report: a non-numeric value does not traceback", "Traceback" not in r.stderr)

# ---------- the advisory must reach a channel the model reads ----------
r = run([HOOK1], stdin=json.dumps({"tool_name": "Task",
        "tool_input": {"prompt": " ".join(["word"] * 200) + "."}}))
ok = False
try:
    ok = "additionalContext" in (json.loads(r.stdout).get("hookSpecificOutput") or {})
except Exception:
    pass
check("hook01: advisory uses additionalContext, NOT permissionDecisionReason", ok)

r = run([HOOK2], stdin=json.dumps({"tool_name": "Bash",
        "tool_input": {"command": "cat ~/coywolf/repos/<corpus>/corpus/x/y.md"}}))
ok = False
try:
    ok = "additionalContext" in (json.loads(r.stdout).get("hookSpecificOutput") or {})
except Exception:
    pass
check("hook02: advisory uses additionalContext", ok)

# ---------- the deleted metric must stay deleted ----------
r = run([STE, "--stdin", "--json"], stdin="The door is open. There are ten items.")
check("ste: the anti-correlated passive metric is GONE",
      "passive" not in r.stdout)

bad = [n for n, ok, _ in results if not ok]
print("\n%s  %d/%d" % ("TESTS PASS" if not bad else "TESTS FAIL", len(results) - len(bad), len(results)))
for n in bad:
    print("   failed: %s" % n)
sys.exit(1 if bad else 0)
