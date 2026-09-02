#!/usr/bin/env python3
"""bait_mark_refuter.py — hooks/mark_refuter.py, seen to write and seen to stay quiet.

Gate 18's flag writer. It appends one of three words when an Agent call with an
adversarial subagent_type returns, and must write NOTHING for any other agent,
or every Explore call would mint a push licence.

KNOWN AND NOT BAITED AWAY: the fourth review (2026-09-02) showed the harness
returns for a BACKGROUND agent at launch, so the flag is minted before a verdict
exists. That is a property of the event, not of this file; the bait records
what the file does with the event it is given.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "mark_refuter.py")
FLAG = "coywolf-refuter-ran.flag"

bad = []
total = 0


def fire(payload, d=None):
    own = d is None
    d = d or tempfile.mkdtemp(prefix="mark-refuter-bait-")
    r = subprocess.run([sys.executable, HOOK], input=payload, capture_output=True, text=True,
                       env=dict(os.environ, TMPDIR=d), timeout=30)
    p = os.path.join(d, FLAG)
    body = open(p).read() if os.path.exists(p) else None
    if own:
        shutil.rmtree(d, ignore_errors=True)
    return r.returncode, body


def agent(sub):
    return json.dumps({"tool_name": "Agent", "tool_input": {"subagent_type": sub, "prompt": "x"}})


def bait(label, payload, want_body):
    global total
    total += 1
    rc, body = fire(payload)
    ok = rc == 0 and body == want_body
    print("  %s %-62s %s" % ("ok " if ok else "XX ", label, "wrote" if body else "quiet"))
    if not ok:
        bad.append(label)
        print("      rc=%s body=%r wanted %r" % (rc, body, want_body))


bait("BAIT F1 refuter writes its word", agent("refuter"), "refuter\n")
bait("BAIT F2 cold-reader writes its word", agent("cold-reader"), "cold-reader\n")
bait("BAIT F3 mechanism-auditor writes its word", agent("mechanism-auditor"), "mechanism-auditor\n")
bait("BAIT F4 general-purpose writes nothing", agent("general-purpose"), None)
bait("BAIT F5 Explore writes nothing", agent("Explore"), None)
bait("BAIT F6 'refuter ' with trailing space is stripped, still counts", agent("refuter "), "refuter\n")
bait("BAIT F7 'Refuter' capitalised is not one of the three", agent("Refuter"), None)
bait("BAIT F8 an Agent call with no subagent_type writes nothing",
     json.dumps({"tool_name": "Agent", "tool_input": {"prompt": "x"}}), None)
bait("BAIT F9 malformed stdin exits 0 and writes nothing", "{nope", None)

d = tempfile.mkdtemp(prefix="mark-refuter-bait-")
fire(agent("refuter"), d)
rc, body = fire(agent("cold-reader"), d)
total += 1
ok = body == "refuter\ncold-reader\n"
print("  %s %-62s %s" % ("ok " if ok else "XX ", "BAIT F10 a second review APPENDS; the record keeps both", "wrote"))
if not ok:
    bad.append("F10")
shutil.rmtree(d, ignore_errors=True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
