#!/usr/bin/env python3
"""Session-scoped flag paths for the conductor's hooks. ONE definition, six users.

WHY. Every flag lived at a FIXED filename under a per-USER TMPDIR, so two
concurrent sessions shared them: session A committed, session B's Stop consumed
A's flags, and A's own Stop found nothing. The table and the prior were LOST on
the turn that actually changed something. Refuted 2026-09-20, reproduced with
the real scripts.

REFUTED AGAIN the same evening. Four defects, all fixed here:

 D4 BLOCKING STDIN. payload() called sys.stdin.read() at module import, and the
    three Stop hooks had NEVER read stdin before. Measured: a pipe held open for
    6s held each hook for 6.1s, against 10-15s timeouts that were previously
    unreachable for them. A hook must never be able to hang a turn. Now guarded
    by select() with a short deadline.

 D5 THE SESSION ID GOES INTO A FILENAME. `a/b`, a 10,000-char id, or anything
    with a separator made the write fail; mark() swallowed it and ALL THREE
    obligations were lost with no signal. Now sanitised to a safe charset and a
    bounded length, so a hostile or odd id degrades to a valid name.

 D2 WAS A SINGLE POINT OF FAILURE. Six hooks did a bare `import _flags` with no
    guard, so a missing/broken/unreadable file gave rc=1 on EVERY hook -- and in
    hook_prior_pre it crashed ABOVE the once-per-turn guard, producing unbounded
    noise, the exact failure that guard exists to prevent. The importers now
    degrade instead of dying; see the try/except in each.

 D1 THE LEGACY FALLBACK reintroduced the theft it was meant to end, and not
    "once" but whenever -- a leftover shared flag fires on some later
    conversation-only turn, in any session. There was never a leftover to
    honour: no coywolf-*.flag exists anywhere. REMOVED.
"""
import json
import os
import re
import select
import sys

_TMP = os.environ.get("TMPDIR", "/tmp")
_SAFE = re.compile(r"[^A-Za-z0-9_-]")
_READ_DEADLINE = 0.5   # seconds; a real payload is already buffered


def payload():
    """The hook's JSON from stdin, or {} -- NEVER a block.

    D4: a hook that waits on an open pipe can burn its whole timeout and take
    the turn's obligations with it. If stdin is a tty, or has nothing ready
    within the deadline, we degrade to {} and the caller falls back to the
    shared scope, which is the pre-2026-09-20 behaviour."""
    try:
        if sys.stdin is None or sys.stdin.closed or sys.stdin.isatty():
            return {}
        r, _, _ = select.select([sys.stdin], [], [], _READ_DEADLINE)
        if not r:
            return {}
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def sid(data):
    """A filename-safe session id. D5: the raw value went straight into a path."""
    raw = str((data or {}).get("session_id") or "").strip()
    if not raw:
        return "nosession"
    clean = _SAFE.sub("_", raw)[:64]
    return clean or "nosession"


def path(name, session):
    """One flag per consumer PER SESSION."""
    return os.path.join(_TMP, "coywolf-%s.%s.flag" % (name, session))
