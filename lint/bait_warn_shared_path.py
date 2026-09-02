#!/usr/bin/env python3
"""bait_warn_shared_path.py — gate 04's hook, seen to fail and seen to pass.

Gate 04's GATE.md once said "baited on twelve shapes" with the baits living
only in a session transcript.
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
    # (command, expect_warning, label)
    # -- writes that MUST warn. Ten of these were silent until 2026-09-02.
    ("rm -rf /Users/u/pack/rendezvous",                          True,  "S1 write verb"),
    ("echo hello > /Users/u/pack/board.txt",                     True,  "S2 redirect"),
    ("printf x >> ~/pack/rendezvous/log",                        True,  "S3 append"),
    ("cat > ~/pack/rendezvous/board.db",                         True,  "S4 cat-with-redirect"),
    ('sqlite3 ~/pack/rendezvous/b.db "insert into m values(1)"', True,  "S5 sqlite"),
    ('ssh den "python3 -c \'open(\\"/Users/u/pack/b\\",\\"w\\").write(1)\'"', True, "S6 -c payload"),
    ("ssh den 'rm ~/pack/x'",                                    True,  "S7 remote verb"),
    ("cp ~/.config/keys/agent.key /tmp",                          True,  "S8 signing key"),
    ("cd /Users/u/pack && rm board.txt",                         True,  "S9 cd-then-relative"),
    ("truncate -s 0 /Users/u/pack/board.txt",                    True,  "S10 truncate"),
    ("touch /Users/u/pack/newfile",                              True,  "S11 touch"),
    ("mkdir -p /Users/u/pack/newdir",                            True,  "S12 mkdir"),
    ("rsync -a /tmp/src/ /Users/u/pack/",                        True,  "S13 rsync"),
    ("curl -o /Users/u/pack/board.txt https://x/y",              True,  "S14 curl -o"),
    ("perl -i -pe 's/a/b/' /Users/u/pack/board.txt",             True,  "S15 perl -i"),
    ("git -C /Users/u/pack rm board.txt",                        True,  "S16 git rm"),
    ("chmod 000 /Users/u/pack/board.txt",                        True,  "S17 chmod"),
    ("echo x | sudo tee /Users/u/pack/board.txt",                True,  "S18 sudo tee"),
    # -- reads that must stay quiet, or the warning becomes noise
    ("cat ~/pack/LIMITS.json",                                   False, "S19 local read"),
    ("ssh den 'cat ~/pack/notes.md'",                            False, "S20 remote read"),
    ("ssh den 'ls ~/pack'",                                      False, "S21 remote listing"),
    ("grep -R foo ~/pack",                                       False, "S22 grep a shared path"),
    ("git -C ~/pack log --oneline",                              False, "S23 read-only git"),
    ("head -20 ~/pack/board.txt",                                False, "S24 head"),
    ("ls -l /tmp",                                               False, "S25 unrelated"),
    ("echo hi > /tmp/scratch",                                   False, "S26 write to UNSHARED"),
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
