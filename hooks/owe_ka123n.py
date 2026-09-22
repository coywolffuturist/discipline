#!/usr/bin/env python3
"""Stop hook — the ka123n window is owed, and it is owed LAST.

WHY THIS EXISTS. His standing order: every message ends with the ka123n window.
He has now corrected it TWICE -- 2026-09-20 ("Remember that you're supposed to
do Ka123n at the end of every message") and again on 2026-09-21. Twice is not
forgetfulness, it is a missing mechanism.

Four Stop hooks already fire: owe_table, hook_prior, hook_posterior,
hook_completer. Between them they demand the completion table, the prior and
the posterior. NONE of them mentions ka123n. So the one obligation he has
repeated was the one thing held only in memory, while three others were
compiled into code. A rule recalled at the right moment fails; a rule wired to
an event fires. That is the same finding that produced hook_prior_pre.py.

IT ASKS FOR POSITION, NOT JUST PRESENCE. The window is the SELECT step of the
outer loop: it shows him the three ranked steps so he can steer before work
begins. A window buried above a wall of gate rows has been shown but not
surfaced. He asked for it LAST, so the hook says LAST.

IT DOES NOT FIRE ON EVERY TURN. A pure question, a null result, a one-line
acknowledgement -- these end a turn without a window being useful, and a hook
that speaks every single time gets skimmed, which is the failure the whole
estate keeps recording. It fires when the turn DID something: the build flag
that owe_table consumes is the same signal, so this hook reads its own copy.

ONE FLAG PER CONSUMER. mark_build's comment records why: owe_table CONSUMES the
shared build flag, so whichever Stop hook drew second saw nothing and gate 08
fired on luck for weeks. This hook owns KA_FLAG alone.
"""
import json
import os
import sys

try:
    _HOOKDIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HOOKDIR = os.path.expanduser("~/.claude/hooks")
sys.path.insert(0, _HOOKDIR)

try:
    import _flags
except Exception:
    sys.exit(0)                      # a gate that raises blocks everything

try:
    _DATA = _flags.payload()
    _SID = _flags.sid(_DATA)
except Exception:
    sys.exit(0)

# Its OWN flag, written by mark_build alongside the others.
FLAG = _flags.path("ka123n-owed", _SID)

if not os.path.exists(FLAG):
    sys.exit(0)

try:
    os.remove(FLAG)
except Exception:
    pass

MSG = (
    "KA123N — the window is owed, and it goes LAST.\n"
    "His standing order, corrected twice: every message ends with the three-row "
    "window. Not a backlog, not a status list — exactly THREE next steps, RANKED "
    "by EV per bit, each priced where cost matters, each carrying WHY IT IS FIRST.\n"
    "Rules that make it real:\n"
    "  - SHOW it before #1 executes. An invisible ranking cannot be steered, and "
    "steering is the whole point.\n"
    "  - EXECUTE #1. Never offer it, never ask permission for the step you already "
    "ranked first.\n"
    "  - A discovered failure OUTRANKS planned progress. A refuted claim or a "
    "broken gate takes #1 until repaired.\n"
    "  - A step blocked on him is named as blocked; it does not sit at #1 pretending.\n"
    "  - SLIDE after the work: re-rank on what execution revealed, never proceed by "
    "momentum into the old #2.\n"
    "POSITION IS PART OF THE ORDER: the window is the LAST thing in the message, "
    "after the gates, after the posteriors, after the prose. A window buried above "
    "a wall of rows has been shown but not surfaced."
)

print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": MSG}}))
sys.exit(0)
