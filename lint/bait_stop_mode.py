#!/usr/bin/env python3
"""bait_stop_mode.py — _flags.speak: a Stop hook that finds a miss must SCORE it by default, never force a turn.

His ruling 2026-09-24: 150 of my replies in five days were set off by a Stop hook, not by him. A hook's
additionalContext is shown to him and forces another turn. Default mode "score" logs the miss and prints nothing;
"force" (env STOP_HOOK_MODE, or ~/.claude/stop_hook_mode) restores the old behaviour.
Driven end to end through a real hook (owe_ka123n) with its flag planted, so the hook really fires.
"""
import json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
KA = os.path.join(HERE, "..", "hooks", "owe_ka123n.py")
bad, total = [], 0


def bait(name, ok, note=""):
    global total
    total += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(note)))
    ok or bad.append(name)


def fire(mode, home, flag=True):
    tmp = tempfile.mkdtemp(prefix="stopmode-")
    sid = "sm-" + os.urandom(3).hex()
    if flag:
        open(os.path.join(tmp, "coywolf-ka123n-owed.%s.flag" % sid), "w").write("1")
    env = {k: v for k, v in os.environ.items() if k != "STOP_HOOK_MODE"}
    env.update(TMPDIR=tmp, HOME=home)
    if mode:
        env["STOP_HOOK_MODE"] = mode
    r = subprocess.run([sys.executable, KA], input=json.dumps({"session_id": sid}), capture_output=True, text=True,
                       env=env, timeout=30)
    shutil.rmtree(tmp, ignore_errors=True)
    log = os.path.join(home, ".claude", "state", "stop_hook_misses.jsonl")
    lines = open(log).read().splitlines() if os.path.exists(log) else []
    return r.returncode, r.stdout, lines


home = tempfile.mkdtemp(prefix="stopmode-home-")
# CONTROL: no flag, nothing owed -> silent AND nothing logged (else a hook that always logs passes)
rc, out, lines = fire(None, home, flag=False)
bait("BAIT S1 nothing owed: silent and nothing logged", rc == 0 and out.strip() == "" and lines == [], (out[:60], lines))
rc, out, lines = fire(None, home)
bait("BAIT S2 default mode, a real miss: prints NOTHING", rc == 0 and out.strip() == "", out[:80])
bait("BAIT S3 default mode: the miss is logged once, with the hook's name", len(lines) == 1 and json.loads(lines[0])["hook"] == "owe_ka123n", lines)
rc, out, lines = fire("force", home)
bait("BAIT S4 force mode: the old additionalContext comes back", '"additionalContext"' in out, out[:80])
bait("BAIT S5 force mode logs nothing new", len(lines) == 1, lines)
os.makedirs(os.path.join(home, ".claude"), exist_ok=True)
open(os.path.join(home, ".claude", "stop_hook_mode"), "w").write("force\n")
rc, out, lines = fire(None, home)
bait("BAIT S6 the mode FILE also restores forcing", '"additionalContext"' in out, out[:80])
shutil.rmtree(home, ignore_errors=True)
print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
sys.exit(1 if bad else 0)
