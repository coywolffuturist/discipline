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

# ---------- FINDING 4: the punctuation flip ----------
with tempfile.TemporaryDirectory() as d:
    items = ["Read the file", "Score the prompt", "Put the number in the table",
             "Stop when the gate is red", "Tell the operator what you found"]
    open(os.path.join(d, "noperiod.md"), "w").write("\n".join("- " + i for i in items) + "\n")
    open(os.path.join(d, "period.md"), "w").write("\n".join("- " + i + "." for i in items) + "\n")
    a = run([LINT, os.path.join(d, "noperiod.md")])
    b = run([LINT, os.path.join(d, "period.md")])
    check("F4: a bullet list scores the SAME with and without periods",
          a.returncode == b.returncode == 0)

r = run([STE, "--stdin", "--json"], stdin="Do it at 3 a.m. and check e.g. the log.\n")
try:
    n = json.loads(r.stdout)["<stdin>"]["scanned"]
except Exception:
    n = -1
check("F4: abbreviations do not split a sentence", n == 1, "scanned=%s" % n)

# ---------- FINDING 5: ambiguity is measured and reaches the verdict ----------
r = run([STE, "--stdin", "--json"],
        stdin="It broke it. Fix it before it runs again. Handle this as needed.\n")
try:
    sig = json.loads(r.stdout)["<stdin>"]["ambiguity_signals"]
except Exception:
    sig = 0
check("F5: unresolvable pronouns raise ambiguity signals", sig >= 3, "signals=%s" % sig)

with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "amb.md"), "w").write(
        "It broke it. Fix this as needed. Do that if necessary. They know.\n")
    r = run([LINT, os.path.join(d, "amb.md")])
    check("F5: dense ambiguity makes the VERDICT red", r.returncode == 1 and "ambiguity" in r.stdout)

with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "clear.md"), "w").write(
        "The parser dropped 28 claims. The gate scores each prompt. "
        "The operator reads the table.\n")
    r = run([LINT, os.path.join(d, "clear.md")])
    check("F5: clear prose is NOT flagged (no false red)", r.returncode == 0)

# ---------- FINDING 6: the ratio must not invert ----------
def classify(cmd):
    env2 = os.environ.copy(); env2["HOME"] = tempfile.mkdtemp()
    run([HOOK2], stdin=json.dumps({"tool_name": "Bash", "hook_event_name": "PostToolUse",
                                   "tool_input": {"command": cmd}}), env=env2)
    log = os.path.join(env2["HOME"], ".coywolf/state/door_use.jsonl")
    if not os.path.exists(log):
        return "none"
    return json.loads(open(log).read().strip().split("\n")[-1])["kind"]

check("F6: a hand-read MENTIONING search_code counts as a hand-read",
      classify("grep -rn search_code ~/coywolf/repos/<corpus>/organs/x.py") == "hand_read")
check("F6: `cd repo && cat file` is counted at all",
      classify("cd ~/repos/<project> && cat model.py") == "hand_read")
check("F6: a real cheap door counts as a cheap door",
      classify("corpus grep ruling") == "cheap_door")

env3 = os.environ.copy(); env3["HOME"] = tempfile.mkdtemp()
r = run([HOOK2], stdin=json.dumps({"tool_name": "Bash", "hook_event_name": "PreToolUse",
        "tool_input": {"command": "cat ~/coywolf/repos/x/y.md"}}), env=env3)
logged = os.path.exists(os.path.join(env3["HOME"], ".coywolf/state/door_use.jsonl"))
check("F6: PreToolUse warns but does NOT log (a denied command never ran)",
      "additionalContext" in r.stdout and not logged)

# ---------- FINDING 9: no unfalsifiable novelty claims survive ----------
for g in ("01-ste", "02-retrieval-economy"):
    txt = open(os.path.join(G, g, "GATE.md"), encoding="utf-8").read()
    check("F9: %s claims nothing 'wholly ours'" % g, "wholly ours" not in txt.lower())

bad = [n for n, ok, _ in results if not ok]
print("\n%s  %d/%d" % ("TESTS PASS" if not bad else "TESTS FAIL", len(results) - len(bad), len(results)))
for n in bad:
    print("   failed: %s" % n)
sys.exit(1 if bad else 0)
