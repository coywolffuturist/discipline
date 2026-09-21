#!/usr/bin/env python3
"""Stop hook, gate 08. The completion table must carry a NUMERIC prior.

WHY THIS EXISTS. Gate 08 recorded 35 firings in one day and never once went
N/A, while an actual number appeared four times. After the operator ruled the
number mandatory on 2026-09-01, the very next four completion tables still had
none — the gate fires BEFORE building and I kept reaching it AFTER.

That is not a memory failure to promise away. It is a gate with no form. This is
the form.

It rides the same flag as the table reminder and stays separate from it, because
no gate may bundle: one row, one reason, so a silent one cannot hide inside
another's message.
"""
import json, os
import sys as _sys
try:
    _HOOKDIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HOOKDIR = os.path.expanduser("~/.claude/hooks")
for _d in (_HOOKDIR, os.path.expanduser("~/.claude/hooks")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)
try:
    import _flags
except Exception:                     # D2: six hooks share this file. A missing or
    class _flags:                     # half-saved copy must not rc=1 every hook, and
        @staticmethod                 # must never crash ABOVE a once-per-turn guard.
        def payload():
            return {}
        @staticmethod
        def sid(_d):
            return "nosession"
        @staticmethod
        def path(name, session):
            return os.path.join(os.environ.get("TMPDIR", "/tmp"),
                                "coywolf-%s.%s.flag" % (name, session))
_DATA = _flags.payload()
_SID = _flags.sid(_DATA)


FLAG = _flags.path("prior-owed", _SID)
# D1 2026-09-20: a legacy shared-path fallback lived here and reintroduced the
# exact cross-session theft this change exists to end -- and not once, but on
# any later turn, in any session. No leftover ever existed. Removed.
# The PreToolUse form (hook_prior_pre.py) asks BEFORE the build and sets its own
# flag so it asks once per turn. Clearing it here re-arms it for the next turn.
# It is cleared unconditionally, even when this hook exits early, or a turn that
# changed nothing would leave the pre-form muted for the turn that follows.
PRE_FLAG = _flags.path("prior-pre-fired", _SID)
try:
    os.remove(PRE_FLAG)
except OSError:
    pass

# OWN FLAG, not the table hook's. A cold reader proved on 2026-09-01 that
# owe_table.py deletes the build flag and is listed FIRST, so this hook was
# silenced whenever that draw order held. "Read, do not consume" does not help
# when the other hook is the consumer. Consume this one: it is ours alone.
if not os.path.exists(FLAG):
    raise SystemExit(0)
try:
    os.remove(FLAG)
except OSError:
    pass

msg = ("GATE 08 set-the-prior: this turn changed something, so a prior was owed "
       "BEFORE it. State the user-outcome in one sentence and a NUMERIC prior on "
       "it. If you did not set one, the row is BLOCKED — say so rather than "
       "writing a posterior against a number that was never recorded.")

print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
