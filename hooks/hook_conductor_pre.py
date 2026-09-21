#!/usr/bin/env python3
"""PreToolUse[Write|Edit|Bash] — the CONDUCTOR ENTRY gate. Operator ruling 2026-09-21.

WHY THIS EXISTS.
The ruling is that discipline and ka123n are ON BY DEFAULT, not invoked. Before
this hook, "on by default" was attempted three times as PRINTED TEXT and failed
three times:

  - session_gate.sh printed a discipline reminder, but only when $OUT was
    non-empty -- i.e. only when something ELSE was already broken. On a clean
    session it never printed at all.
  - session_gate.sh printed the two MCP levers UNCONDITIONALLY. On 2026-09-20
    that block printed at session start and the session then made ZERO
    mind_grep calls across an entire night, reading files by hand instead.
  - The conductor's own SKILL.md sat in context from the first message and was
    invoked only when a Stop hook nagged.

session_gate.sh line 11 predicted this in writing: "a hook that speaks every
session gets skimmed, and a gate that gets skimmed is a decoration." It was
right, and it was right about itself.

THE ONE THING THAT WORKED. On 2026-09-20 gate 08 was given a PreToolUse form
(hook_prior_pre.py). It is the only gate that changed behaviour that night: the
prior got stated BEFORE the audit, once, the single time all session. A gate
that arrives while the action is still pending is read. The same text at Stop,
or at session start, is skimmed. Form beats vocabulary.

WHY IT IS NOT A DENIAL, AND WHY IT IS ONE-SHOT.
The operator rejected the denying-PreToolUse design explicitly: a hook that
blocks Write/Edit/Bash until gates are satisfied pushes the agent to satisfy
them by READING FILES, which is the expensive door, when the mind answers the
same question for ~400 bytes and zero model calls. A gate that balloons cost is
a gate that gets switched off. So: warn, never deny; once per SESSION, not per
call; no model calls; no file reads; no retry loop.

THE PREDICATE IS IMPORTED, NEVER COPIED. mark_build.py owns "does this command
touch a repo or push a build". It has been narrowed twice by operator ruling. A
second copy here would drift out of agreement with the table hook. See
feedback_private_rule_15.

OWN FLAG. mark_build's comment records why flags are not shared: owe_table.py
CONSUMES the shared build flag, so whichever Stop hook drew second saw nothing
and gate 08 fired on luck for weeks. This hook owns CONDUCTOR_FLAG alone and
never clears it -- the flag IS the once-per-session record.
"""
import json, os, sys

try:
    _HOOKDIR = os.path.dirname(os.path.abspath(__file__))
except NameError:                        # __file__ is undefined under exec()
    _HOOKDIR = os.path.expanduser("~/.claude/hooks")
sys.path.insert(0, _HOOKDIR)

FLAG_NAME = "conductor_entry_shown"


def _fail_open(msg=None):
    """Any internal error must let the tool call proceed. A gate that raises blocks everything (feedback_private_rule_02)."""
    sys.exit(0)


def main():
    try:
        import _flags
    except Exception:
        return _fail_open()

    try:
        data = _flags.payload()
    except Exception:
        return _fail_open()
    if not data:
        return _fail_open()

    tool = data.get("tool_name") or ""
    tin = data.get("tool_input") or {}

    # Bash is gated on the BUILD predicate so read-only shell work stays quiet.
    # Write/Edit always count: they are how canon and code get authored, and
    # the conductor's DESIGN gates are owed before authoring, not after.
    if tool == "Bash":
        cmd = tin.get("command") or ""
        if not cmd:
            return _fail_open()
        try:
            import mark_build
            if not mark_build.is_build_command(cmd):
                sys.exit(0)
        except Exception:
            # Predicate unavailable: stay SILENT rather than warn on every
            # read. A false warning on `ls` is what gets a guard switched off.
            return _fail_open()
    elif tool not in ("Write", "Edit"):
        sys.exit(0)

    try:
        session = _flags.sid(data)
        flag = _flags.path(FLAG_NAME, session)
    except Exception:
        return _fail_open()

    if os.path.exists(flag):             # already shown this session
        sys.exit(0)

    try:
        os.makedirs(os.path.dirname(flag), exist_ok=True)
        with open(flag, "w") as f:
            f.write("shown")
    except Exception:
        return _fail_open()              # cannot record it -> do not nag forever

    sys.stderr.write(
        "\U0001f3bc CONDUCTOR ENTRY (once this session) — discipline + ka123n are ON by default.\n"
        "   This is the first build action of the session.\n"
        "   ka123n SELECT: is this step #1 by EV-per-byte? Show the three-row window,\n"
        "   each row carrying WHY IT IS FIRST. Execute #1 — never offer it.\n"
        "   DESIGN gates 00-09 are owed NOW, while they can still change the work:\n"
        "     08 set-the-prior — the user-outcome in one sentence and a NUMERIC prior\n"
        "     04 no-collision  — is a peer holding this substrate? check before, not after\n"
        "     05 substrate-search — what existing piece is insufficient?\n"
        "     09 disprove-first — name the observation that would REFUTE this, and RUN it\n"
        "   Answer them from THE MIND (mind_grep / mind_check: 0 model calls, ~400 bytes),\n"
        "   never by reading files. A gate satisfied by pouring context costs more than\n"
        "   the gate saves — which is why this warns and never denies.\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        _fail_open()
