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


def turn_text(data):
    """Everything I wrote since HIS last message, or "" -- never raises.

    2026-09-22, his screenshot: "Do you think it's appropriate to post multiple
    Ka123ns per pass? Do you think I need to see all the hooks?" A Stop hook's
    additionalContext is SHOWN to him and forces another turn. Each nag produced
    a re-render; three windows in a row, hook text on his screen. So a nag must
    first check whether its element is ALREADY in this turn. HIS message = a
    user entry whose text is not a harness tag (<task-notification>,
    <system-reminder>) and not a tool result."""
    try:
        path = (data or {}).get("transcript_path") or ""
        if not path or not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 400_000))
            lines = f.read().decode("utf-8", "replace").splitlines()
        out = []
        for ln in lines:
            try:
                e = json.loads(ln)
            except Exception:
                continue
            msg = e.get("message") or {}
            c = msg.get("content")
            if e.get("type") == "user":
                texts = [c] if isinstance(c, str) else [b.get("text", "") for b in (c or [])
                                                        if isinstance(b, dict) and b.get("type") == "text"]
                # Claude Code marks HIS messages origin.kind == "human"; injected ones carry
                # isMeta. The tag test is the fallback for transcripts without the marker.
                kind = (e.get("origin") or {}).get("kind")
                if kind is not None:
                    human = kind == "human" and not e.get("isMeta")
                else:
                    human = not e.get("isMeta") and any(t.strip() and not t.lstrip().startswith("<") for t in texts)
                if human:
                    out = []          # his message: the turn starts here
            elif e.get("type") == "assistant" and isinstance(c, list):
                out += [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(out)
    except Exception:
        return ""


def _last_message(data):
    """The payload's last_assistant_message as text. The transcript is written LATE:
    live 2026-09-22 it held 115 chars of a finished turn, so all three nags fired
    on a reply that carried the window and the posterior. The payload does not lag."""
    m = (data or {}).get("last_assistant_message")
    if isinstance(m, str):
        return m
    if isinstance(m, dict):
        m = m.get("content", m.get("text", ""))
    if isinstance(m, list):
        return "\n".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in m)
    return str(m or "")


def already_said(data, pattern):
    """True when this turn's text already carries the element -- the nag stays silent."""
    try:
        text = turn_text(data) + "\n" + _last_message(data)
        hit = re.search(pattern, text, re.I | re.M) is not None
        try:   # one line per decision, so "did the nag stay silent, and on what?" is checkable
            import time
            with open(os.path.join(_TMP, "coywolf-hook-silence.log"), "a") as f:
                f.write("%s %s chars=%d keys=%s %s\n" % (time.strftime("%H:%M:%S"), "SILENT" if hit else "NAG",
                        len(text), ",".join(sorted((data or {}).keys())), pattern[:24]))
        except Exception:
            pass
        return hit
    except Exception:
        return False


STOP_MODE_FILE = os.path.expanduser("~/.claude/stop_hook_mode")
MISS_LOG = os.path.expanduser("~/.claude/state/stop_hook_misses.jsonl")


def stop_mode():
    """"score" (default) or "force". His ruling 2026-09-24, after the logs showed 150 of my replies in five days were
    set off by a Stop hook and not by him (63 on 09-21 alone), and three written rules had not stopped it: a Stop hook's
    additionalContext is SHOWN to him and FORCES another turn, so every miss became an unasked reply. In "score" mode a
    miss is appended to MISS_LOG and nothing is printed. STOP_HOOK_MODE (env) wins, then ~/.claude/stop_hook_mode."""
    m = os.environ.get("STOP_HOOK_MODE", "").strip().lower()
    if not m:
        try:
            m = open(STOP_MODE_FILE).read().strip().lower()
        except Exception:
            m = ""
    return "force" if m == "force" else "score"


def speak(hook, msg, data=None):
    """The ONLY way a Stop hook reports a miss."""
    if stop_mode() == "force":
        print(json.dumps({"suppressOutput": True,
                          "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": msg}}))
        return
    try:
        os.makedirs(os.path.dirname(MISS_LOG), exist_ok=True)
        import time as _t
        with open(MISS_LOG, "a") as f:
            f.write(json.dumps({"at": _t.strftime("%Y-%m-%dT%H:%M:%S"), "hook": hook,
                                "session": ((data or {}).get("session_id") or "")[:36], "miss": msg[:240]}) + "\n")
    except Exception:
        pass          # a scorer that throws must never force a turn
