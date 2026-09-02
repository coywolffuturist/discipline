#!/usr/bin/env python3
"""PostToolUse[Agent] hook, gate 18. Records that a refuter ran this turn.

Read by the gate 18 block in ~/.git-hooks/pre-push, which refuses an ordinary
push without this flag. Kept separate from that reader because a flag-setter
that also decides is a flag-setter you cannot test independently.

(It formerly named hook_ship_guard.py, a PreToolUse Bash-text guard RETIRED on
2026-09-01 after three refutations. That file no longer exists.)

WHAT THIS FLAG IS NOT. It is not proof a review happened. A refuter showed on
2026-09-01 that the reader it feeds cannot bind a push that chooses to skip it
— same-privilege enforcement never can. The flag records that a reviewer ran;
it does not certify that one had to.
"""
import json, os, sys

FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-refuter-ran.flag")
try:
    d = json.loads(sys.stdin.read() or "{}")
except Exception:
    raise SystemExit(0)

# The adversarial forms this gate recognises. cold-reader counts: it is
# context-free by construction, which is the property that matters here.
ADVERSARIAL = {"refuter", "cold-reader", "mechanism-auditor"}
sub = ((d.get("tool_input") or {}).get("subagent_type") or "").strip()
if sub in ADVERSARIAL:
    try:
        with open(FLAG, "a") as f:
            f.write(sub + "\n")
    except Exception:
        pass
