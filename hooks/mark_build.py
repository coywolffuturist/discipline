#!/usr/bin/env python3
"""PostToolUse hook. Flags that THIS TURN changed something.

A form of the CONDUCTOR, not of any single gate: it is what makes the completion
table fire without being remembered.

WHY BASH IS INCLUDED. On 2026-08-31 a full day of estate work ran through Bash
and ssh, not Write/Edit. A flag keyed only on file-edit tools would have scored
that day as conversational and asked for nothing.

Read-only shells must stay quiet, or the reminder becomes noise and gets ignored
— which is the failure it exists to prevent.
"""
import json, os, re, sys

FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-build-turn.flag")
PRIOR_FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-prior-owed.flag")
# The verb may sit INSIDE a quoted remote command: `ssh den "rm -f /tmp/x"`.
# Anchoring to a command boundary missed that, which is the dominant shape of
# this estate's work. So the boundary includes quotes and plain whitespace, and
# the check FAILS TOWARD FLAGGING: a spurious reminder costs one line, a missed
# one costs the whole table.
MUT = re.compile(
    r"(^|[;&|(\s'\"])(rm|mv|cp|mkdir|touch|chmod|chown|ln|install|tee|dd)\s"
    r"|\bsed -i\b|\bgit (commit|push|add|checkout|reset|merge|rebase)\b"
    r"|\blaunchctl (load|unload|bootstrap|bootout|kickstart)\b"
    r"|\bpip install\b|\bnpm install\b"
    r"|>>?\s*[^|&\s]", re.M)

def main():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    tool = d.get("tool_name", "")
    if tool in ("Write", "Edit", "NotebookEdit"):
        return mark(tool)
    if tool != "Bash":
        return
    cmd = (d.get("tool_input") or {}).get("command", "") or ""
    # SCRATCH REDIRECTS ARE NOT CHANGES. Caught on this hook's second real turn:
    # a read-only monitoring pass flagged as a build because `>/dev/null` and a
    # `>/tmp/nv.txt` exit-code buffer both matched the redirect shape. Those
    # appear in nearly every probe, so the reminder would have fired on every
    # monitoring turn and been trained into noise - the precise failure this
    # hook exists to prevent. Strip null sinks and temp buffers before matching.
    scrubbed = re.sub(r">>?\s*(/dev/null|/dev/stderr|&\d)", " ", cmd)
    scrubbed = re.sub(r">>?\s*(/tmp|/private/tmp|\$TMPDIR)[^\s;&|]*", " ", scrubbed)
    if MUT.search(scrubbed):
        mark("Bash")

def mark(what):
    # TWO flags, one per consumer. A cold reader proved on 2026-09-01 that
    # owe_table.py CONSUMES the build flag, so whichever Stop hook draws
    # second sees nothing. Gate 08 had been firing on luck. Each consumer
    # now owns its own flag and cannot silence the other.
    for p in (FLAG, PRIOR_FLAG):
        try:
            with open(p, "a") as f:
                f.write(what + "\n")
        except Exception:
            pass

main()
