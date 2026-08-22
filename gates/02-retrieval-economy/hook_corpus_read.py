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
# Readers may appear anywhere: after cd, inside -exec, after xargs, in a loop.
READER = re.compile(r"\b(cat|sed|head|tail|grep|rg|awk|less|more|bat|nl|cut|wc)\b")
# A door counts when it LEADS the pipeline. Leading env assignments and wrappers
# (time, env, nice) are skipped, so `time corpus grep x` and `MIND_DB=y corpus grep x`
# both count. Piping a door into head/grep is STILL a door — the fix for the old
# inversion introduced a new one in the opposite direction.
CHEAP = re.compile(r"^\s*(?:[A-Z_]+=\S+\s+)*(?:time\s+|env\s+|nice\s+)*"
                   r"(?:python3?\s+\S*\s+)?(?:\S*/)?"
                   r"(mind|codebase-memory)\s+"
                   r"(grep|check|page|rulings|consult|recall|search_code|trace_path)\b")

# NEVER WRITE THE RAW COMMAND. It used to store cmd[:160] verbatim in plaintext
# and door_report.py reprinted it, so a `grep -rn sk-ant-... config.py` put a
# live credential on disk AND on screen. That breaks the standing rule: never
# leave a secret on screen. Only a shape is kept now — the reader verb and the
# path's last two segments, with anything token-like removed.
SECRETISH = re.compile(r"[A-Za-z0-9_\-]{20,}")

def shape(cmd):
    """A loggable shape. No arguments, no values, no secrets."""
    verb = (READER.search(cmd) or CHEAP.search(cmd))
    verb = verb.group(0).strip(" ;&|") if verb else "?"
    paths = re.findall(r"[\w./~-]*/[\w.-]+\.(?:py|js|ts|md|sh|json)", cmd)
    tail = "/".join(paths[0].split("/")[-2:]) if paths else ""
    tail = SECRETISH.sub("<redacted>", tail)
    return (verb + " " + tail).strip()[:80]

def log(kind, detail):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps({"ts": int(time.time()), "kind": kind,
                                "shape": shape(detail)}) + "\n")
    except Exception:
        pass

def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    # A list, a string, a number and null are all VALID json and all crashed
    # this hook. The contract says any error allows the call, so the type check
    # comes before the first .get().
    if not isinstance(data, dict):
        sys.exit(0)
    tool = data.get("tool_name") or ""
    # THE DOMINANT CHANNEL. Read and Grep are how an agent usually opens a file,
    # and they produced NO event at all — so the printed cheap-% was not a floor
    # as the report claimed, it could be an overstatement. Counted now.
    if tool in ("Read", "Grep", "Glob"):
        if (data.get("hook_event_name") or "") == "PostToolUse":
            log("hand_read", tool.lower() + " " + str(
                (data.get("tool_input") or {}).get("file_path")
                or (data.get("tool_input") or {}).get("pattern") or ""))
        sys.exit(0)
    if tool != "Bash":
        sys.exit(0)
    # Register this file on BOTH events. PreToolUse warns but must NOT log — a
    # command that is then denied never ran, and counting it corrupts the ratio.
    # PostToolUse logs, because by then the command has actually executed.
    event = data.get("hook_event_name") or "PreToolUse"
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        sys.exit(0)
    cmd = ti.get("command") or ""
    if not isinstance(cmd, str):
        sys.exit(0)
    is_door = bool(CHEAP.match(cmd))
    # A door that LEADS the line is a door, even piped into head or grep.
    # Otherwise a reader touching a corpus path is a hand-read, even when the
    # command text happens to contain a door's name as an argument.
    is_read = (not is_door) and bool(READER.search(cmd) and CORPUS.search(cmd))
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
