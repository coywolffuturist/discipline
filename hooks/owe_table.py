#!/usr/bin/env python3
"""Stop hook. If this turn CHANGED anything, the completion table is owed.

WHY THIS EXISTS. The conductor is a document. On 2026-08-31 gates were omitted
from completion tables three times in one session AFTER a correction, because
nothing forced them. A rule recalled at the right moment fails; a rule compiled
into a gate fires every time. This is that compilation.

Fires ONCE per turn: the flag is removed before the message is emitted, so it
cannot loop.
"""
import json, os

FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-build-turn.flag")

if not os.path.exists(FLAG):
    raise SystemExit(0)
try:
    n = sum(1 for _ in open(FLAG))
except Exception:
    n = "?"
try:
    os.remove(FLAG)
except Exception:
    pass

# SHORT, and it POINTS at the conductor instead of restating it. Two reasons.
# The operator asked on 2026-08-31 why he was shown this wall of text every
# build turn: hook feedback renders in HIS terminal, and a gate that clutters a
# reader it does not address gets switched off. And a restatement is a second
# copy of canon; second copies drift, as this one did three times in three turns
# (stale gate count, missing forbidden words, false turn attribution).
msg = (
    "DISCIPLINE: completion table owed. %s change(s) since the last check; the "
    "credit can land one turn late, so if THIS turn changed nothing the table "
    "was owed by the previous one. Render all 19 gates per "
    "~/.claude/skills/discipline/SKILL.md, which holds the three legal states, "
    "the forbidden words, and gate 19. If already rendered, say so in one line "
    "and stop."
) % n

print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
