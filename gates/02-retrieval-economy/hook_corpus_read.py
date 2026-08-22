#!/usr/bin/env python3
# FORM: hook. PreToolUse[Bash]. WARNS, NEVER BLOCKS.
"""hook_corpus_read.py — name the cheaper door when a corpus is read by hand.

WHY. On 2026-08-22 the author read repositories with grep, sed and cat for a
full session, then called codebase-memory once. It immediately found substrate
the hand-reading had missed. The rule was in context the whole time.

WHY IT DOES NOT BLOCK. Reading files by hand is often correct — you need exact
bytes, or the index is stale, or the query door already answered. A blocker
would be wrong most of the times it fired. The completion table is the
enforcement; this is the measurement, and it logs every event for the reporter.

FAIL-OPEN. Any error allows the call.
"""
import json, os, re, sys, time

LOG = os.path.expanduser("~/.coywolf/state/door_use.jsonl")
# FINDING 6, closed 2026-08-22. The old classifier tested CHEAP against the
# WHOLE command before READER, so `grep -rn search_code somefile` — a hand-read —
# logged as a cheap door. And CORPUS demanded a contiguous repos/<name>/<path>,
# so the commonest idiom `cd repo && cat file` logged NOTHING. The numerator
# inflated and the denominator deflated, both toward the flattering number: a
# true 0% would have reported as a 7x improvement on the baseline.
#
# Now: a command counts as a cheap door only when the DOOR IS THE COMMAND BEING
# RUN, never when its name appears as an argument or inside a string.
CORPUS = re.compile(r"(<corpus>/corpus|beacons/NOTES-|\.claude/(skills|agents)/"
                    r"|repos/[\w-]+/|\.(py|js|ts|md|sh)\b)")
READER = re.compile(r"(?:^|[;&|]\s*)\s*(?:sudo\s+)?(cat|sed|head|tail|grep|rg|awk|less|more)\b")
# the door must be in COMMAND POSITION: start of line, or after ; && || |
CHEAP = re.compile(r"(?:^|[;&|]\s*)\s*(?:python3?\s+\S*)?(?:\S*/)?"
                   r"(mind|codebase-memory)\b\s+(grep|check|page|rulings|consult|recall|search_code|trace_path)")

def log(kind, detail):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps({"ts": int(time.time()), "kind": kind,
                                "detail": detail[:160]}) + "\n")
    except Exception:
        pass

def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    if (data.get("tool_name") or "") != "Bash":
        sys.exit(0)
    # Register this file on BOTH events. PreToolUse warns but must NOT log — a
    # command that is then denied never ran, and counting it corrupts the ratio.
    # PostToolUse logs, because by then the command has actually executed.
    event = data.get("hook_event_name") or "PreToolUse"
    cmd = (data.get("tool_input") or {}).get("command") or ""
    is_read = bool(READER.search(cmd) and CORPUS.search(cmd))
    is_door = bool(CHEAP.search(cmd))
    # ORDER MATTERS: a hand-read that merely MENTIONS a door is a hand-read.
    if event == "PostToolUse":
        if is_read:
            log("hand_read", cmd)
        elif is_door:
            log("cheap_door", cmd)
        sys.exit(0)                      # PostToolUse never warns; it only counts
    if not is_read:
        sys.exit(0)                      # PreToolUse warns on hand-reads only
    # additionalContext, NOT permissionDecisionReason — see gate 01's hook.
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext":
            "GATE 02 retrieval-economy (advisory — not blocking): this reads a "
            "corpus or repo by hand. Cheaper doors first — `corpus grep` is 400 "
            "bytes and 0 model calls; `codebase-memory search_code` answers "
            "structural questions for ~1% of the tokens. Proceed if you need "
            "the exact bytes. The ratio goes in the completion table."
    }}))
    sys.exit(0)

if __name__ == "__main__":
    main()
