#!/usr/bin/env python3
"""PreToolUse[Bash] hook, gate 04. Warn before touching substrate a peer holds.

IT WARNS. IT DOES NOT DENY. Three versions of a denying Bash-text guard were
built here and all three were refuted, and the third simultaneously allowed the
thing it targeted and denied a plain `grep`. A false denial is what gets a guard
switched off. This one raises the question and gets out of the way.

WHY IT IS NEEDED. Coordinating costs one message; a clobber costs an afternoon
and is found late. The gate fired 28 times in one day and its N/A rows all cite
the same trigger — "no peer-held substrate" — which means the judgement is real
and the miss is silent: nothing tells you a peer is holding something.

WHAT IT CANNOT DO. It does not know whether a peer is ACTUALLY holding the path
right now. That is what the lock tool is for. This only notices that the path is
shared, which is the fact I forget.
"""
import json, os, re, sys

# Substrate a second agent can hold. Each entry earned its place: these are the
# paths where two writers have actually met, or would.
SHARED = [
    (r"~?/?pack/|/Users/[^/\s]+/pack/",       "the pack tree — a peer agent writes here"),
    (r"rendezvous",                            "the Rendezvous board — a peer posts to it"),
    (r"\bssh\s+\S*den|coywolfden",             "the second machine — a peer runs there"),
    (r"gui-browser-lock|Chrome|chrome_js",     "the shared browser — take the lock first"),
    (r"\.coywolf/keys/",                        "signing keys — split custody, never both sides"),
]

try:
    d = json.loads(sys.stdin.read() or "{}")
except Exception:
    raise SystemExit(0)

cmd = ((d.get("tool_input") or {}).get("command") or "")

# A WRITE is a write verb OR a redirection. The first version checked verbs only
# and was refuted on 2026-09-01: `echo x > ~/pack/board.txt`, `printf x >> log`
# and `sqlite3 board.db "insert..."` all passed SILENTLY, and `cat > board.db`
# was ACTIVELY EXEMPTED by the read-shape early-exit below. The paths matched
# fine every time — the VERB list was the hole, which is why a hand-maintained
# list of shapes is the wrong instrument for "is this a write".
REDIRECT = re.compile(r">>?\s*[^|&\s>]")          # > path  or  >> path
VERB = re.compile(r"(^|[;&|]\s*)(rm|mv|cp|tee|dd|install|ln|sed\s+-i|sqlite3|"
                  r"git\s+(push|commit|checkout|reset)|python3?\s|bash\s|\bssh\b)")
has_redirect = bool(REDIRECT.search(cmd))
if not (has_redirect or VERB.search(cmd)):
    raise SystemExit(0)

# The read-shape exit applies ONLY with no redirection. `cat file` is a read;
# `cat > file` is a write, and treating them alike is what exempted the board.
if not has_redirect and re.match(r"^\s*(cat|ls|grep|rg|head|tail|wc|find|stat|file|diff)\b", cmd):
    raise SystemExit(0)

# `ssh host 'cat ...'` is a READ on the second machine. The old version warned on
# every ssh, which is noise, and noise is how a warning gets ignored.
if re.match(r"^\s*ssh\b", cmd) and not has_redirect and \
        re.search(r"""['"]\s*(cat|ls|grep|head|tail|wc|find|stat|pgrep|echo|date|python3?\s+-c)\b""", cmd) and \
        not VERB.search(re.sub(r"^\s*ssh\s+\S+\s*", "", cmd)):
    raise SystemExit(0)

hits = [why for pat, why in SHARED if re.search(pat, cmd)]
if not hits:
    raise SystemExit(0)

msg = ("GATE 04 no-collision: this command touches " + hits[0] + ". "
       "Check for a live peer before writing (ListAgents, or the lock tool "
       "`gui-browser-lock who` on the second machine). Coordinating costs one "
       "message; a clobber costs an afternoon and is found late. Proceeding is "
       "fine — this is a question, not a refusal.")
print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "PreToolUse",
                                         "permissionDecision": "allow",
                                         "permissionDecisionReason": msg}}))
