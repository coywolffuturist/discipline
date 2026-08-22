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
CORPUS = re.compile(r"(<corpus>/corpus|/beacons/NOTES-|repos/\w[\w-]*/(?!\.git)\S+\.(py|js|ts|md)\b)")
READER = re.compile(r"\b(cat|sed\s+-n|head|tail|grep|rg|awk)\b")
CHEAP = re.compile(r"\b(mind\s+(grep|check|page|rulings|consult|recall)|search_code|trace_path)\b")

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
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if CHEAP.search(cmd):
        log("cheap_door", cmd)
        sys.exit(0)
    if not (READER.search(cmd) and CORPUS.search(cmd)):
        sys.exit(0)
    log("hand_read", cmd)
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
