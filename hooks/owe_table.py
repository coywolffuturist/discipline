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

msg = (
    "DISCIPLINE - COMPLETION TABLE OWED.\n"
    "%s change(s) have happened SINCE THE LAST CHECK, so a build is outstanding.\n"
    "Not necessarily in this turn: the final tool call of a turn can write its\n"
    "flag after that turn's Stop hook already ran, so the credit lands one turn\n"
    "late. If THIS turn made no changes, the table was owed by the previous one --\n"
    "say so in one line and stop.\n\n"
    "Render the completion table from ~/.claude/skills/discipline/SKILL.md. "
    "All 20 gates get a row. Three legal states and no fourth: FIRED (name the "
    "ARTIFACT, never a checkmark), N/A (legal only by citing that gate's own "
    "written trigger, listed in the conductor table), BLOCKED (state what is now "
    "UNVERIFIED). Silently omitting a row is not a state.\n"
    "DO NOT WRITE: PARTIAL, FAILED, NOT FIRED, SKIPPED. None is a state. "
    "PARTIAL and FAILED are FIRED with an artifact that names what was and was "
    "not produced. NOT FIRED and SKIPPED, when the trigger DID fire, are "
    "BLOCKED plus what is now UNVERIFIED.\n\n"
    "GATE 20 state-the-posterior is a TRIGGER, not only a row: any claim of done, "
    "ready, verified or sure "
    "owes a posterior AND its evidence, gated by the WORST failure mode rather "
    "than the best subsystem.\n\n"
    "If you already rendered the table this turn, say so in one line and stop.\n"
    "If this reminder names a gate count or number that disagrees with the "
    "conductor, the HOOK is stale: fix it, because it teaches the wrong canon "
    "every turn."
) % n
print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
