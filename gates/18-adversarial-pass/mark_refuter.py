#!/usr/bin/env python3
"""PostToolUse[Agent] hook, gate 18. Records that a refuter ran this turn.

Paired with hook_ship_guard.py, which refuses to ship without this flag. Kept
separate from the guard because a flag-setter that also decides is a flag-setter
you cannot test independently.
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
