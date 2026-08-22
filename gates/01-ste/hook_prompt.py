#!/usr/bin/env python3
# FORM: hook. PreToolUse[Agent/Task]. WARNS, NEVER BLOCKS — operator ruling
# 2026-08-22: "warn + score in completion table".
"""hook_prompt.py — score a subagent prompt BEFORE the subagent spawns.

WHY HERE AND NOT ANYWHERE ELSE. The industry checks finished manuals. This
checks the instruction while it can still be rewritten. On 2026-08-22 seven
long, nested agent prompts were written; two agents misread their scope and one
reported success on partial work. That is the exact failure ASD-STE100 was
invented to prevent, in a domain the standard has never been applied to.

WHY IT DOES NOT BLOCK. A gate that refuses a 26-word sentence is the ritual the
suite forbids, and it would fight the operator's own exception: use the exact
technical term where precision needs it. The completion table is the
enforcement. This hook is only the measurement.

FAIL-OPEN. Any error allows the call. A style hook must never be able to stop
work.
"""
import json, os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
STE = os.path.join(HERE, "ste.py")
# a prompt over this many words per sentence, or with this share over the limit,
# is worth saying out loud. Deliberately loose: this warns, it does not police.
MEDIAN_WARN = 22
OVER_PCT_WARN = 40

def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    if (data.get("tool_name") or "") not in ("Agent", "Task"):
        sys.exit(0)
    prompt = (data.get("tool_input") or {}).get("prompt") or ""
    if not isinstance(prompt, str):
        sys.exit(0)                      # fail-open: the contract says never stop work
    if len(prompt.split()) < 40:
        sys.exit(0)                      # short prompts are the goal, not a finding
    try:
        r = subprocess.run([sys.executable, STE, "--stdin", "--json"],
                           input=prompt, capture_output=True, text=True, timeout=10)
        s = json.loads(r.stdout)["<stdin>"]
    except Exception:
        sys.exit(0)                      # fail-open
    if s.get("scanned", 0) == 0:
        sys.exit(0)
    notes = []
    if s["median_words"] >= MEDIAN_WARN:
        notes.append("median %dw/sentence" % s["median_words"])
    if s["over_limit_pct"] >= OVER_PCT_WARN:
        notes.append("%d%% of sentences over 25w" % s["over_limit_pct"])
    if s.get("stacked_clauses", 0) >= 3:
        notes.append("%d stacked-clause sentences" % s["stacked_clauses"])
    if not notes:
        sys.exit(0)
    # additionalContext, NOT permissionDecisionReason. The reason field is
    # discarded on "allow" and renders only in the deny/ask UI. Using it here
    # produced a hook that fired, logged, and reached nobody.
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext":
            "STE (gate 01, advisory — not blocking): " + " · ".join(notes) +
            ". An agent cannot cheaply ask what you meant. Shorter sentences, one "
            "instruction each. Record the score in the completion table."
    }}))
    sys.exit(0)

if __name__ == "__main__":
    main()
