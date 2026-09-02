#!/usr/bin/env python3
"""bait_repeats.py — repeats.py, seen to go red and seen to count.

Shared by gates 03 and 06 (and installed as hooks/repeats.py, byte-identical).
Two contracts: `log` reduces a command to its SHAPE and appends it; `report`
reads the log two ways and must say UNVERIFIED — rc 2 — when the log is absent
or empty, because an absent log means the logger never ran, not "no repeats".
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FORM = os.path.join(HERE, "repeats.py")
LOG = "coywolf-cmd-shapes.log"

bad = []
total = 0


def run(args, d, stdin=""):
    r = subprocess.run([sys.executable, FORM] + list(args), input=stdin, capture_output=True,
                       text=True, env=dict(os.environ, TMPDIR=d), timeout=30)
    return r.returncode, r.stdout + r.stderr


def log(d, cmd):
    return run([], d, json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}))


def lines(d):
    p = os.path.join(d, LOG)
    return open(p).read().splitlines() if os.path.exists(p) else None


def bait(label, cond, detail=""):
    global total
    total += 1
    print("  %s %-62s %s" % ("ok " if cond else "XX ", label, detail[:44]))
    if not cond:
        bad.append(label)


d = tempfile.mkdtemp(prefix="repeats-bait-")
rc, out = run(["report"], d)
bait("BAIT P1 report with NO log is rc 2 UNVERIFIED, not a pass", rc == 2 and "UNVERIFIED" in out, out)
open(os.path.join(d, LOG), "w").write("")
rc, out = run(["report"], d)
bait("BAIT P2 report with an EMPTY log is rc 2 UNVERIFIED", rc == 2 and "UNVERIFIED" in out, out)

log(d, "ls -la /tmp/a")
log(d, "ls /var/log")
log(d, "ls   /etc")
rows = lines(d)
bait("BAIT P3 three commands of one shape log three identical rows",
     rows is not None and len(rows) == 3 and len(set(rows)) == 1, repr(rows))
rc, out = run(["report"], d)
bait("BAIT P4 gate 06 reports the shape at x3", rc == 0 and "x3" in out and "1 shape(s) repeated 3+" in out, out)
bait("BAIT P5 gate 03 reports two back-to-back repeats", "2 call(s) issued back-to-back" in out, out)

log(d, 'grep "rm -rf /" notes.txt')
log(d, 'grep "hello" notes.txt')
rows = lines(d)
bait("BAIT P6 quoted text is DATA: two greps with different quotes share a shape",
     rows[-1] == rows[-2] and "rm" not in rows[-1], repr(rows[-2:]))

before = len(lines(d))
log(d, "")
bait("BAIT P7 an empty command logs nothing", len(lines(d)) == before)
rc, _ = run([], d, "{nope")
bait("BAIT P8 malformed stdin exits 0 and logs nothing", rc == 0 and len(lines(d)) == before)
log(d, "python3 -c 'x'")
bait("BAIT P9 flags are dropped from the shape", not lines(d)[-1].startswith("python3 -c"), lines(d)[-1])
shutil.rmtree(d, ignore_errors=True)

# Threshold, normalisation and width — each was mutated on 2026-09-02 with
# every bait above staying green.
d = tempfile.mkdtemp(prefix="repeats-bait-")
log(d, "sleep 1"); log(d, "sleep 2")
rows = lines(d)
bait("BAIT P10 numbers are normalised: `sleep 1` and `sleep 2` share a shape", rows[0] == rows[1], repr(rows))
rc, out = run(["report"], d)
bait("BAIT P11 two of a shape is NOT the crystallize threshold", "0 shape(s) repeated 3+" in out, out)
log(d, "sleep 3")
rc, out = run(["report"], d)
bait("BAIT P12 the third is", "1 shape(s) repeated 3+" in out, out)
log(d, "git log a b c"); log(d, "git log x y z")
rows = lines(d)
bait("BAIT P13 the shape keeps FOUR tokens, so `git log a b` and `git log x y` differ", rows[-1] != rows[-2], repr(rows[-2:]))
shutil.rmtree(d, ignore_errors=True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
