#!/usr/bin/env python3
"""Stop hook, gate 19. A done claim must carry a PER-CRITERION posterior.

WHY THIS EXISTS. Gate 19 recorded four firings in one day and TWO of the four
artifacts are the literal placeholder "below" — the gate reported itself FIRED
with no number recorded. The failure is silence: the turn ends, the work looks
finished, and the claim goes out as "done" with no number against it.

WHY PER-CRITERION, which is the part a single number hides. The ruling of
2026-09-01 is that the posterior is gated by the WORST failure mode, not the
best subsystem. The two honest firings on record both split the number:

    "Archive complete, clean, byte-identical, restorable — 0.95, all four checks
     against the artifact. Durability 0.4 -> 0.8: two machines, but same house,
     and it's a snapshot that won't track tomorrow's changes"
    "The watcher works and cross-verifies — 0.9. That it keeps working — 0.7:
     public RPCs change policy without notice, and I now depend on three of them"

One averaged number would report 0.875 and 0.8 and conceal both risks. Note the
FIRST one: 0.4 -> 0.8 is the prior MOVED. An earlier copy of this docstring
quoted it as a flat 0.4 — the prior reported as the posterior, inside the hook
that exists to demand a posterior. A refuter caught it.

IT DOES NOT READ THE ANSWER. This hook cannot tell a real posterior from a
plausible one, and does not try. It restores the question at the moment the
question is skipped. Gate 18 is what tests whether the number was earned.

Own flag, per the rule in mark_build.py: a shared flag lets whichever Stop hook
draws first silence the rest.
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


FLAG = _flags.path("posterior-owed", _SID)
# D1 2026-09-20: a legacy shared-path fallback lived here and reintroduced the
# exact cross-session theft this change exists to end -- and not once, but on
# any later turn, in any session. No leftover ever existed. Removed.

if not os.path.exists(FLAG):
    raise SystemExit(0)
try:
    os.remove(FLAG)
except OSError:
    pass

msg = ("GATE 19 state-the-posterior: this turn changed something. Before any "
       "done / ready / clean / it-works claim, state the posterior PER "
       "CRITERION, not as one averaged number — the claim is gated by the WORST "
       "failure mode, not the best subsystem. Name what each number rests on. "
       "If the prior was never set or was set against a different outcome, the "
       "posterior cannot update it: say BLOCKED rather than inventing a number.")

# The floor is READ here, never recalled: posterior.py audit MOVES it when HIGH
# claims come back wrong, and a floor quoted from memory is the exact failure
# gate 19 was split off to prevent. Fail QUIET — a hook must never wedge a turn.
try:
    import importlib.util
    _p = os.path.expanduser("~/.claude/scripts/posterior.py")
    _spec = importlib.util.spec_from_file_location("posterior", _p)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    _f = _m._floors()
    _open = sum(1 for e in _m._entries() if e.get("outcome") == "TBD")
    msg += (" FLOOR NOW: reversible %.2f, one-way-door %.2f (read live, not recalled). "
            "Log the number so it can be scored: posterior.py log <p> <door> <claim>. "
            "%d claim(s) still unsettled." % (_f["reversible"], _f["one-way-door"], _open))
except Exception:
    pass

# 2026-09-22: silent when this turn already carries it -- a nag is shown to him
# and forces another turn (see _flags.turn_text).
# 2026-09-23: the delivered reply is reworded before this hook reads it; "posterior so far 0.90"
# arrived as "My current estimate is 0.90". Both forms count.
if getattr(_flags, "already_said", lambda d, p: False)(_DATA, '(settled (right|wrong)|(posterior|current estimate|estimate is|estimate now)[^\\n]{0,30}\\b0?\\.\\d\\d|(posterior|estimate)[^\\n]{0,40}\\bblocked\\b|\\bblocked\\b[^\\n]{0,40}(posterior|estimate)|\\b19\\b[^\\n]{0,20}(fired|blocked))'):
    _sys.exit(0)
print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
