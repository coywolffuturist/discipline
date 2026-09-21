#!/usr/bin/env python3
"""PreToolUse[Bash] hook, gate 08. Ask for the prior BEFORE the build, not after.

WHY THIS EXISTS, AND WHY THE OLD FORM COULD NOT WORK.
`hook_prior.py` is a STOP hook. Gate 08's whole definition is "state the
user-outcome and a NUMERIC prior BEFORE building". A DESIGN gate wired to an END
event can only ever report the miss it exists to prevent — every message it has
ever sent literally reads "a prior was owed BEFORE it". The operator had to say
"you're not using /discipline" twice before the cause was looked at, on
2026-09-20. It was never forgetfulness; it was a gate with the wrong form.

This one fires before the mutating command runs, while the prior can still be
stated.

IT WARNS. IT DOES NOT DENY. Three denying Bash-text guards were built in this
estate and all three were refuted; a false denial is what gets a guard switched
off. Gate 08 is a thinking obligation, not a permission.

THE PREDICATE IS IMPORTED, NEVER COPIED. `mark_build.py` owns "does this command
touch a repo or push a build". That predicate has been narrowed twice by
operator ruling — 2026-09-02 dropped Write/Edit entirely ("editing a file is not
touching a repo until it is committed") and 2026-09-19 added remote writes. A
second copy here would drift out of agreement with the table hook, so the two
would disagree about whether a turn was a build. We exec mark_build's module
body UP TO `def main():`, which gives us MUT, REMOTE_WRITE and is_notes without
running its PostToolUse main().

ONE FLAG PER CONSUMER. mark_build's own comment records why: owe_table.py
CONSUMES the shared build flag, so whichever Stop hook drew second saw nothing
and gate 08 fired on luck for weeks. This hook owns PRE_FLAG alone. It is
cleared by hook_prior.py at Stop, so exactly one warning is issued per turn.
"""
import json, os, re, sys, time
# __file__ IS NOT DEFINED UNDER exec(). hook_prior_pre loads this module by
# exec-ing its source, so an __file__-based path here broke the predicate
# import outright (2026-09-20) and dropped the PreToolUse form into its
# fail-open branch, warning on plain reads. Caught by the hook itself.
try:
    _HOOKDIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HOOKDIR = os.path.expanduser("~/.claude/hooks")
sys.path.insert(0, _HOOKDIR)
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

TMP = os.environ.get("TMPDIR", "/tmp")
# PRE_FLAG is resolved per session inside main(), where the payload exists.
MARK = os.path.expanduser("~/.claude/hooks/mark_build.py")


def load_predicate():
    """mark_build's classifier, without its PostToolUse main(). Returns
    (is_build_fn, None) or (None, reason) — a failure is SAID OUT LOUD, never
    swallowed, because a silently mis-predicating gate is worse than none."""
    try:
        src = open(MARK, encoding="utf-8").read()
        cut = src.index("def main():")
    except Exception as e:
        return None, "could not read mark_build.py (%s)" % e
    ns = {}
    try:
        exec(compile(src[:cut], MARK, "exec"), ns)
        # ONE entry point, not three regexes reassembled here. mark_build owns the
        # question "is this a build"; a second assembly in this file would drift the
        # moment that predicate is tuned again, and it has been tuned three times.
        return ns["is_build_command"], None
    except Exception as e:
        return None, "mark_build.py's predicate did not load (%s)" % e


def say(msg):
    print(json.dumps({"suppressOutput": True,
                      "hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "additionalContext": msg}}))


def main():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    if d.get("tool_name") != "Bash":
        return
    PRE_FLAG = _flags.path("prior-pre-fired", _flags.sid(d))
    cmd = (d.get("tool_input") or {}).get("command", "") or ""
    if not cmd:
        return
    # D3 2026-09-20: this flag is cleared ONLY by hook_prior.py at Stop. If that
    # never runs -- its own 10s timeout, a crash, an interrupt -- the flag is
    # session-scoped, so NOTHING else can clear it and gate 08's pre-warning goes
    # silent for the rest of the session with no signal. Under the old shared flag
    # any session's Stop re-armed it; scoping traded stolen for permanently muted.
    # A turn does not last 30 minutes: an older flag is stale, not "already asked".
    if os.path.exists(PRE_FLAG):
        try:
            fresh = (time.time() - os.path.getmtime(PRE_FLAG)) < 1800
        except OSError:
            fresh = False
        if fresh:
            return

    is_build, why = load_predicate()
    if is_build is None:
        # 2026-09-20 REFUTED: this branch said its piece and returned WITHOUT
        # setting PRE_FLAG, so it warned on every Bash call, unbounded -- 6 of 6
        # read-only commands warned in the refuter's run. That is the "trained
        # into noise" failure this design names as fatal three times, and it
        # fires hardest while mark_build.py is mid-edit, which is exactly when
        # the estate is working on it. Set the flag first: one warning per turn.
        try:
            open(PRE_FLAG, "w").write("predicate-unavailable")
        except Exception:
            pass
        say("GATE 08 set-the-prior: %s. The gate cannot tell whether this is a "
            "build, so decide yourself: if you are about to change something you "
            "will later call done, state the user-outcome and a NUMERIC prior "
            "first." % why)
        return
    if not is_build(cmd):
        return

    try:
        open(PRE_FLAG, "w").write(cmd[:200])
    except Exception:
        pass
    say("GATE 08 set-the-prior — FIRING BEFORE THE BUILD, which is the point. "
        "This command touches a repo or pushes a build. Before it runs: state "
        "the user-outcome in ONE sentence and a NUMERIC prior on it. Not 'high' "
        "— a number. You cannot update a posterior you never set, and a "
        "posterior with no prior is a first impression wearing a decimal. "
        "If a prior for this outcome is already stated in this turn, proceed.")


main()
