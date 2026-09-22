#!/usr/bin/env python3
"""Stop hook. If this turn CHANGED anything, the completion table is owed.

WHY THIS EXISTS. The conductor is a document. On 2026-08-31 gates were omitted
from completion tables three times in one session AFTER a correction, because
nothing forced them. A rule recalled at the right moment fails; a rule compiled
into a gate fires every time. This is that compilation.

Fires ONCE per turn: the flag is removed before the message is emitted, so it
cannot loop.

THE SUITE IS DECLARED, NOT ASSUMED (2026-09-02). Another setup adopts the
gates it chooses. It writes them, one per line, to ~/.claude/discipline-suite
(or the file DISCIPLINE_SUITE names). This hook then asks for THOSE rows and
only those. With no file, the suite is every gate on disk (counted, not typed). Gates 12 (completer) and 19
(state-the-posterior) are always owed, because a suite without its two closers
cannot be run to completion; the hook adds them and says so.
"""
import json, os, re
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


FLAG = _flags.path("build-turn", _SID)
# D1 2026-09-20: a legacy shared-path fallback lived here and reintroduced the
# exact cross-session theft this change exists to end -- and not once, but on
# any later turn, in any session. No leftover ever existed. Removed.
SUITE = os.environ.get("DISCIPLINE_SUITE") or os.path.expanduser("~/.claude/discipline-suite")
CLOSERS = ("12", "19")


def gate_count():
    """COUNT THE DIRECTORIES. Never type this number.

    It was hardcoded "19" and went stale the day gate 00 regime-routing shipped
    (2026-09-07), so every table this hook asked for was 19 of 20 gates and the
    agent repeated the wrong count back for a whole session. The comment further
    down already records this same value drifting three times in three turns. A
    restatement of canon is a second copy, and second copies drift -- so derive it.

    Returns None rather than raising: a gate that raises blocks everything, and
    a missing gates directory must not break every Stop hook on the machine.
    """
    import glob
    for root in (os.path.expanduser("~/.claude/skills/discipline/gates"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gates")):
        try:
            n = len([d for d in glob.glob(os.path.join(root, "[0-9][0-9]-*"))
                     if os.path.isdir(d)])
            if n:
                return n
        except OSError:
            continue
    return None


def suite():
    """Gate numbers declared, two digits each, or None for the whole suite."""
    try:
        # utf-8-sig, so a byte-order mark cannot hide the first gate. A reviewer
        # showed a BOM'd "19" reading as "no suite" and a BOM'd "05" vanishing.
        # An unreadable path (a directory, a permission) is "no file": every gate.
        text = open(SUITE, encoding="utf-8-sig").read()
    except (OSError, ValueError):
        return None
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    nums = []
    for l in lines:
        m = re.match(r"(\d{1,2})\b", l)
        # 01-19 only. "0", "20" and "99" were accepted and rendered as gates.
        if m and 1 <= int(m.group(1)) <= 19:
            nums.append("%02d" % int(m.group(1)))
    if not nums:
        return None
    added = [c for c in CLOSERS if c not in nums]
    return sorted(set(nums) | set(CLOSERS)), added


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
s = suite()
if s is None:
    # NOT `n` -- that is the change count set above and printed below. Naming
    # this one `n` clobbered it, so the hook reported the GATE count as the
    # number of changes. Caught by bait O2, which asserts both in one row.
    gates_n = gate_count()
    scope = ("Render all %d gates" % gates_n) if gates_n else "Render every gate in the suite"
else:
    nums, added = s
    scope = "Render the %d gates of your declared suite (%s)" % (len(nums), " ".join(nums))
    if added:
        scope += " — %s added: a suite is not run to completion without its closers" % " and ".join(added)
msg = (
    "DISCIPLINE: completion table owed. %s change(s) since the last check; the "
    "credit can land one turn late, so if THIS turn changed nothing the table "
    "was owed by the previous one. %s per the discipline skill (SKILL.md), which "
    "holds the three legal states, the forbidden words, and gate 19. If already "
    "rendered, say so in one line and stop."
) % (n, scope)

# 2026-09-22: silent when this turn already carries it -- a nag is shown to him
# and forces another turn (see _flags.turn_text).
if getattr(_flags, "already_said", lambda d, p: False)(_DATA, '\\bgates?\\b[^\\n]{0,40}\\b(fired|blocked|n/a)\\b'):
    _sys.exit(0)
print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
