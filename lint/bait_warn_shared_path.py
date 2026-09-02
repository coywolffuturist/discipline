#!/usr/bin/env python3
"""bait_warn_shared_path.py — gate 04's hook, seen to fail and seen to pass.

Gate 04's GATE.md said "baited on twelve shapes, both directions, zero wrong".
A reviewer pointed out that the baits existed only in a session transcript: the
claim was unfalsifiable by any reader, which is the property gate 09 forbids.
These are those shapes, runnable.

Two of them are the defects reviewers actually found: a redirect write that
passed silently, and `ssh host "python3 -c ...write..."` classified as a read.
"""
import json, os, subprocess, sys

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "hooks", "warn_shared_path.py")

CASES = [
    # (command, expect_warning, why this shape is here)
    ("rm -rf /Users/u/pack/rendezvous",              True,  "S1 plain write verb"),
    ("echo hello > /Users/u/pack/board.txt",         True,  "S2 REDIRECT — passed silently before"),
    ("printf x >> ~/pack/rendezvous/log",            True,  "S3 append redirect"),
    ("cat > ~/pack/rendezvous/board.db",             True,  "S4 cat-with-redirect, was EXEMPTED"),
    ('sqlite3 ~/pack/rendezvous/b.db "insert into m values(1)"', True, "S5 sqlite write"),
    ('ssh den "python3 -c \'open(\\"/Users/u/pack/b\\",\\"w\\").write(1)\'"', True,
                                                             "S6 -c payload, was read-classified"),
    ("ssh den 'rm ~/pack/x'",                        True,  "S7 remote write verb"),
    ("cp ~/.coywolf/keys/emi.key /tmp",              True,  "S8 signing key"),
    ("cat ~/pack/LIMITS.json",                       False, "S9 local read"),
    ("ssh den 'cat ~/pack/notes.md'",                False, "S10 remote read"),
    ("ssh den 'ls ~/pack'",                          False, "S11 remote listing"),
    ("grep -R rendezvous ~/notes",                   False, "S12 read of an unshared path"),
    ("ls -l /tmp",                                   False, "S13 unrelated"),
    ("echo hi > /tmp/scratch",                       False, "S14 write to an UNSHARED path"),
]

bad = []
for cmd, want, why in CASES:
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_input": {"command": cmd}}),
                       text=True, capture_output=True)
    got = bool(r.stdout.strip())
    ok = got == want
    print("  %s %-6s %-46s %s" % ("ok " if ok else "XX ", why.split()[0], cmd[:46],
                                  "WARN" if got else "silent"))
    if not ok:
        bad.append(why)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", len(CASES) - len(bad), len(CASES)))
sys.exit(1 if bad else 0)
