#!/usr/bin/env python3
"""Stop hook, gate 12. Deferral language in the turn's output must be classified.

THE GATE IS A CLASSIFICATION, NOT A BAN. Residue is legitimate when the blocker
is outside your reach. All four BLOCKED rows on record are the gate working:
each says "Unverified: <what>" and names what remains. What is NOT legitimate is
"it's big" or "end of session" wearing the same words.

So this reads the turn's own output for the words that carry a deferral, and
asks which of the two it was. It cannot tell them apart — that is the judgement,
and it is the gate.

It reads the tail of the transcript only. A Stop hook that parses a long session
on every turn would be a tax on every turn.
"""
import json, os, re, sys

PHRASES = re.compile(
    r"follow[- ]up|next session|separate pass|deferred?\b|later pass|for now|"
    r"TODO|revisit later|leave (?:that|this|it) for|out of scope for (?:now|today)",
    re.I)

try:
    d = json.loads(sys.stdin.read() or "{}")
except Exception:
    raise SystemExit(0)

path = d.get("transcript_path") or ""
if not path or not os.path.exists(path):
    raise SystemExit(0)

# Tail only. Read the last ~200KB rather than the whole file.
try:
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - 200_000))
        tail = f.read().decode("utf-8", "replace")
except OSError:
    raise SystemExit(0)

# Last assistant text only: the phrases appear constantly in tool output and in
# the user's own words, and flagging those would train the reminder into noise.
texts = []
for line in tail.splitlines():
    if '"assistant"' not in line:
        continue
    try:
        m = json.loads(line).get("message", {})
    except Exception:
        continue
    for c in m.get("content", []) or []:
        if isinstance(c, dict) and c.get("type") == "text":
            texts.append(c.get("text", ""))

if not texts:
    raise SystemExit(0)
found = sorted({m.group(0).lower() for m in PHRASES.finditer(texts[-1])})
if not found:
    raise SystemExit(0)

print(json.dumps({"suppressOutput": True, "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext":
        "GATE 12 completer: this turn's output used deferral language (%s). "
        "Classify it, do not just repeat it. A GENUINE blocker is data, a "
        "decision or access you lack, or a distinct NEW build — name it AND "
        "what would unblock it. \"It's big\" or \"end of session\" is stopping "
        "short: finish it now. The user outcome is the whole job."
        % ", ".join(repr(f) for f in found[:4])}}))
