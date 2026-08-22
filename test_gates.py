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
    # CHANGED 2026-08-22, deliberately. A directory with no markdown is the
    # gate's own trigger not firing, which our three-state rule calls N/A.
    # RED here blocked every code-only commit within an hour of registration.
    # N/A is NOT a silent pass: it prints why, and it never prints GREEN.
    check("lint: a directory with no markdown is N/A and SAYS so",
          r.returncode == 0 and "N/A" in r.stdout and "GREEN" not in r.stdout)

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
    # CHANGED 2026-08-22, deliberately. A refuter showed the signal RED-ed clear
    # writing and GREEN-ed genuinely ambiguous writing — anti-correlated, the
    # same class that got the passive metric deleted. It is counted and shown;
    # it does not judge until it is proven.
    check("F5: ambiguity is COUNTED but does not decide the verdict",
          r.returncode == 0 and "NOT judged" in r.stdout)

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

# ---------- round 2: every behaviour a refuter deleted without the suite noticing ----------

# secrets must never reach disk
env4 = os.environ.copy(); env4["HOME"] = tempfile.mkdtemp()
# The fixture is ASSEMBLED AT RUNTIME so no secret-shaped literal is ever
# committed. The estate's own pre-commit scanner caught the literal version of
# this line — correctly, since it cannot know a fixture from a live key.
FAKE_KEY = "sk-" + "ant-" + "api03-" + "SYNTHETICFIXTURE" + "9" * 8
run([HOOK2], stdin=json.dumps({"tool_name": "Bash", "hook_event_name": "PostToolUse",
    "tool_input": {"command": "grep -rn %s ~/coywolf/repos/x/config.py" % FAKE_KEY}}),
    env=env4)
logtxt = ""
lp = os.path.join(env4["HOME"], ".coywolf/state/door_use.jsonl")
if os.path.exists(lp):
    logtxt = open(lp).read()
check("SEC: a credential in a command NEVER reaches the log",
      "SYNTHETICFIXTURE" not in logtxt and "hand_read" in logtxt)

# hooks fail OPEN on every hostile JSON shape
for shape in ("[]", "null", "123", '"str"', '{"tool_name":"Bash","tool_input":"cat x"}',
              '{"tool_name":"Bash","tool_input":{"command":["cat","/x/repos/a/b.md"]}}'):
    a = run([HOOK1], stdin=shape); b = run([HOOK2], stdin=shape)
    check("OPEN: both hooks survive %s" % shape[:28], a.returncode == 0 and b.returncode == 0)

# an unreadable file is RED, never counted as scored
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "real.md"), "w").write("The gate runs. It scores text.\n")
    os.symlink("/nowhere/gone.md", os.path.join(d, "broken.md"))
    r = run([LINT, d])
    check("SCAN: a broken symlink is RED, not silently 'scored'",
          r.returncode == 1 and "UNREADABLE" in r.stdout)

# determiner vs pronoun
r = run([STE, "--stdin", "--json"],
        stdin="This parser rejects big files. That limit is in config. These limits apply.\n")
try: sig = json.loads(r.stdout)["<stdin>"]["ambiguity_signals"]
except Exception: sig = 99
check("AMB: determiners are NOT flagged as open references", sig == 0, "signals=%s" % sig)
r = run([STE, "--stdin", "--json"], stdin="It broke it. They know. This is wrong.\n")
try: sig = json.loads(r.stdout)["<stdin>"]["ambiguity_signals"]
except Exception: sig = 0
check("AMB: real pronouns ARE still flagged", sig >= 2, "signals=%s" % sig)

# ambiguity must NOT decide the verdict
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "a.md"), "w").write("It broke it. They know. It failed. It ran.\n")
    r = run([LINT, os.path.join(d, "a.md")])
    check("AMB: the signal is reported, NOT judged", r.returncode == 0 and "NOT judged" in r.stdout)

# closing marks
with tempfile.TemporaryDirectory() as d:
    body = "The gate runs. It scores the text. The score goes in the table. The operator reads it. Nothing else happens."
    open(os.path.join(d, "plain.md"), "w").write(body + "\n")
    open(os.path.join(d, "bold.md"), "w").write(
        " ".join("**%s.**" % x for x in body.split(". ")).replace("..", ".") + "\n")
    a = run([LINT, os.path.join(d, "plain.md")]); b = run([LINT, os.path.join(d, "bold.md")])
    check("SPLIT: bold sentences score the same as plain", a.returncode == b.returncode == 0)

# frontmatter is metadata, not prose
r = run([STE, "--stdin", "--json"],
        stdin="---\nname: x\ndescription: " + ("word " * 60) + "\n---\n\nThe gate runs. It works.\n")
try: n = json.loads(r.stdout)["<stdin>"]["longest"]
except Exception: n = 99
check("SPLIT: YAML frontmatter is not scored as prose", n < 10, "longest=%s" % n)

# classifier, both directions
check("DOOR: a door piped into head is still a door",
      classify("corpus page decision_x | head -40") == "cheap_door")
check("DOOR: `time corpus grep` counts", classify("time corpus grep ruling") == "cheap_door")
check("DOOR: xargs cat counts as a hand-read",
      classify("xargs cat < ~/repos/<project>/list.txt") == "hand_read")

def classify_tool(tool, ti):
    env5 = os.environ.copy(); env5["HOME"] = tempfile.mkdtemp()
    run([HOOK2], stdin=json.dumps({"tool_name": tool, "hook_event_name": "PostToolUse",
                                   "tool_input": ti}), env=env5)
    lp = os.path.join(env5["HOME"], ".coywolf/state/door_use.jsonl")
    if not os.path.exists(lp):
        return "none"
    return json.loads(open(lp).read().strip().split("\n")[-1])["kind"]

check("DOOR: the Read tool — the dominant channel — is counted",
      classify_tool("Read", {"file_path": "/x/repos/<project>/model.py"}) == "hand_read")

# the load-bearing case
r = run([LINT, "app.py"])
check("LOAD: a code-only changeset is N/A, not a blocked commit",
      r.returncode == 0 and "N/A" in r.stdout)

# ---------- holes found by mutate_test.py, 2026-08-22 ----------

# The log EXISTS but holds no events in the window. This is the state the day
# after registration, and it was the one branch of gate 02's empty-scan rule
# with no test — so the rule could be deleted and the suite stayed green.
env6 = os.environ.copy(); env6["HOME"] = tempfile.mkdtemp()
lp6 = os.path.join(env6["HOME"], ".coywolf/state")
os.makedirs(lp6, exist_ok=True)
open(os.path.join(lp6, "door_use.jsonl"), "w").write(
    json.dumps({"ts": 1, "kind": "hand_read", "shape": "cat old.md"}) + "\n")
r = run([REPORT, "--since-hours", "1"], env=env6)
check("SCAN: a log with ZERO events in the window is RED",
      r.returncode == 1 and "not a pass" in r.stdout)

# the vague-scope detector had no test at all
r = run([STE, "--stdin", "--json"],
        stdin="Handle the queue as needed. Update the files where relevant, etc.\n")
try: v = json.loads(r.stdout)["<stdin>"]["vague_scope"]
except Exception: v = 0
check("AMB: vague scope ('as needed', 'etc') is counted", v >= 2, "vague=%s" % v)

bad = [n for n, ok, _ in results if not ok]
print("\n%s  %d/%d" % ("TESTS PASS" if not bad else "TESTS FAIL", len(results) - len(bad), len(results)))
for n in bad:
    print("   failed: %s" % n)
sys.exit(1 if bad else 0)
