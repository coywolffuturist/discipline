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
POST_FLAG  = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-posterior-owed.flag")
# The verb may sit INSIDE a quoted remote command: `ssh den "rm -f /tmp/x"`.
# Anchoring to a command boundary missed that, which is the dominant shape of
# this estate's work. So the boundary includes quotes and plain whitespace, and
# the check FAILS TOWARD FLAGGING: a spurious reminder costs one line, a missed
# one costs the whole table.
# 2026-09-01, operator: "fix the hook so it stops firing every turn."
#
# ROOT CAUSE. The old pattern matched command TEXT, so a mutating verb appearing
# as DATA flagged a build: `grep "rm " file`, a test payload containing
# `git commit`, a heredoc body mentioning a path. And the bare-redirect rule
# `>>?\s*[^|&\s]` matched every heredoc and every `> file`, which is most
# diagnostic pipelines. The result was a reminder on nearly every turn, which is
# how a guard gets trained into noise — the failure it exists to prevent.
#
# THE DISCRIMINATOR THAT SURVIVED. Write/Edit is a reliable build signal; Bash is
# not. So Bash now flags only on verbs that are UNAMBIGUOUS and ANCHORED at the
# start of a command or right after a separator (; && || | newline). A verb
# inside quotes is data, not an action, and no longer counts.
#
# Deliberately dropped: the bare-redirect rule. Writing a file through `>` is
# real, but it fired on every heredoc and diagnostic buffer, and Write/Edit
# already covers authored files.
MUT = re.compile(
    r"(?:^|[;&|\n]\s*)\s*(?:sudo\s+)?"
    r"(?:rm|mv|chmod|chown|ln|dd"
    r"|git\s+(?:commit|push|add|checkout|reset|merge|rebase)"
    r"|launchctl\s+(?:load|unload|bootstrap|bootout|kickstart)"
    r"|pip\s+install|npm\s+install|brew\s+install"
    r"|scp|rsync)"
    r"\b"
)

# NOTES ARE NOT BUILDS. Operator ruling 2026-09-01: appending to canon or memory
# is the behaviour the conductor WANTS, and charging it a 19-gate table taxes the
# right action. A notes path only escapes when the command is PURELY notes work —
# a git or launchctl call in the same command is still a build.
NOTES = re.compile(
    r"coo/taxes/CONTEXT\.md|/memory/|MEMORY\.md|\.claude/projects/.*\.md", re.I)
STILL_A_BUILD = re.compile(r"\bgit\s|launchctl", re.I)


def is_notes(text):
    return bool(text) and bool(NOTES.search(text)) and not STILL_A_BUILD.search(text)


def main():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    tool = d.get("tool_name", "")
    if tool in ("Write", "Edit", "NotebookEdit"):
        # same carve-out as Bash: editing a notes/canon file is not a build
        path = (d.get("tool_input") or {}).get("file_path", "") or ""
        if is_notes(path):
            return
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
    if is_notes(cmd):
        return
    if MUT.search(scrubbed):
        mark("Bash")

def mark(what):
    # ONE FLAG PER CONSUMER, and this is why. A cold reader proved on
    # 2026-09-01 that owe_table.py CONSUMES the build flag, so whichever Stop
    # hook draws second sees nothing. Gate 08 had been firing on luck. Each
    # consumer now owns its own flag and cannot silence the other. Adding a
    # consumer means adding a flag here — a shared one reintroduces the bug.
    for p in (FLAG, PRIOR_FLAG, POST_FLAG):
        try:
            with open(p, "a") as f:
                f.write(what + "\n")
        except Exception:
            pass

main()
