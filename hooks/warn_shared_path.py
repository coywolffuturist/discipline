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
    (r"~?/?pack(/|\b)|/Users/[^/\s]+/pack(/|\b)", "the pack tree — a peer agent writes here"),
    (r"rendezvous",                            "the Rendezvous board — a peer posts to it"),
    (r"\bssh\s+\S+",                            "another machine — a peer may run there"),
    (r"gui-browser-lock|Chrome|chrome_js",     "the shared browser — take the lock first"),
    (r"/keys?/|\.pem\b|\.key\b",                "signing keys — split custody, never both sides"),
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
# INVERTED, AND THIS IS THE THIRD DESIGN. The first matched write VERBS and
# missed every redirect. The second added redirects and still missed ten shapes
# a reviewer found in one pass: `cd <shared> && rm f`, truncate, touch, mkdir,
# rsync, `curl -o`, `perl -i`, `git -C <shared> rm`, chmod, `| sudo tee`.
#
# Both a verb list and a path pattern are ENUMERATIONS OF THINGS I THOUGHT OF,
# which is the failure this gate's own file already names. A longer list loses
# the same way — so the question is inverted.
#
# THE RULE NOW: if a command mentions a shared path at all, WARN — unless it is
# recognisably read-only. This form WARNS and never denies, so a spurious
# warning costs one line and a silent miss costs an afternoon. The asymmetry
# decides the direction of the default.
READ_ONLY = re.compile(
    r"""^\s*(?:ssh\s+\S+\s+)?['"]?\s*"""
    r"""(cat|bat|less|more|head|tail|wc|grep|rg|ag|find|ls|stat|file|diff|"""
    r"""du|md5|shasum|sha256sum|awk|sed(?!\s+-i)|cut|sort|uniq|jq|column|"""
    r"""git(\s+-[A-Za-z]\s+\S+)*\s+(log|show|diff|status|blame|ls-files|for-each-ref|cat-file|rev-parse|describe))\b""",
    re.X)
REDIRECT = re.compile(r">>?\s*[^|&\s>]")

hits = [why for pat, why in SHARED if re.search(pat, cmd)]
if not hits:
    raise SystemExit(0)

# Recognisably read-only AND no redirection anywhere: not a collision.
if READ_ONLY.match(cmd) and not REDIRECT.search(cmd):
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
