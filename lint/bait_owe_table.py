#!/usr/bin/env python3
"""bait_owe_table.py — hooks/owe_table.py, seen to ask and seen to stay quiet.

The completion-table Stop hook. It must be quiet on a turn that changed
nothing, ask once on a turn that did, and ask for the DECLARED suite — with
the two closers added when a suite leaves them out.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "owe_table.py")

bad = []
total = 0


def run(d, suite_text=None, flag=True):
    env = dict(os.environ, TMPDIR=d)
    sp = os.path.join(d, "suite")
    if suite_text is None:
        env["DISCIPLINE_SUITE"] = os.path.join(d, "no-such-file")
    else:
        open(sp, "w").write(suite_text)
        env["DISCIPLINE_SUITE"] = sp
    if flag:
        open(os.path.join(d, "coywolf-build-turn.flag"), "w").write("Bash\nWrite\n")
    r = subprocess.run([sys.executable, HOOK], input="{}", capture_output=True, text=True, env=env, timeout=30)
    ctx = ""
    if r.stdout.strip():
        out = json.loads(r.stdout)
        if out.get("hookSpecificOutput", {}).get("hookEventName") != "Stop" or out.get("suppressOutput") is not True:
            return r.returncode, "WRONG ENVELOPE"
        ctx = out["hookSpecificOutput"]["additionalContext"]
    return r.returncode, ctx


def bait(label, cond, detail=""):
    global total
    total += 1
    print("  %s %-64s %s" % ("ok " if cond else "XX ", label, detail[:36]))
    if not cond:
        bad.append(label)


d = tempfile.mkdtemp(prefix="owe-table-bait-")
rc, ctx = run(d, flag=False)
bait("BAIT O1 no build flag: quiet", rc == 0 and ctx == "")
rc, ctx = run(d)
bait("BAIT O2 build flag: the table is owed, all 19 with no suite declared",
     rc == 0 and "all 19 gates" in ctx and "2 change(s)" in ctx, ctx[:36])
bait("BAIT O3 the flag was consumed", not os.path.exists(os.path.join(d, "coywolf-build-turn.flag")))
rc, ctx = run(d, flag=False)
bait("BAIT O4 a second Stop is quiet", ctx == "")
rc, ctx = run(d, "01 ste\n07 think-3x\n12 completer\n19 state-the-posterior\n")
bait("BAIT O5 a declared suite is asked for by number", "4 gates of your declared suite (01 07 12 19)" in ctx, ctx[:36])
bait("BAIT O6 ...and 'all 19' is not", "all 19" not in ctx)
rc, ctx = run(d, "# my suite\n7\n11\n")
bait("BAIT O7 a suite without its closers gets 12 and 19 added, and is told",
     "(07 11 12 19)" in ctx and "12 and 19 added" in ctx, ctx[:36])
rc, ctx = run(d, "# nothing declared\n\n")
bait("BAIT O8 an empty suite file means the whole suite", "all 19 gates" in ctx)
rc, ctx = run(d, "gate five\n")
bait("BAIT O9 a line with no number is ignored, not a crash", rc == 0 and "all 19 gates" in ctx)
rc, ctx = run(d, "0\n20\n99\n07\n")
bait("BAIT O10 numbers outside 01-19 are not gates", "(07 12 19)" in ctx and "20" not in ctx.split("suite")[1][:30], ctx[:36])
rc, ctx = run(d, "﻿05\n07\n")
bait("BAIT O11 a byte-order mark does not swallow the first gate", "(05 07 12 19)" in ctx, ctx[:36])
rc, ctx = run(d, "05\r\n07\r\n")
bait("BAIT O12 CRLF line endings parse", "(05 07 12 19)" in ctx, ctx[:36])
env_dir = tempfile.mkdtemp(prefix="owe-suite-dir-")
open(os.path.join(d, "coywolf-build-turn.flag"), "w").write("Bash\n")
r = subprocess.run([sys.executable, HOOK], input="{}", capture_output=True, text=True,
                   env=dict(os.environ, TMPDIR=d, DISCIPLINE_SUITE=env_dir), timeout=30)
bait("BAIT O13 DISCIPLINE_SUITE naming a directory means all 19, not a crash",
     r.returncode == 0 and "all 19 gates" in r.stdout)
shutil.rmtree(env_dir, ignore_errors=True)
shutil.rmtree(d, ignore_errors=True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
