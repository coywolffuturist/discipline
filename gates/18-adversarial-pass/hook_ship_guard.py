#!/usr/bin/env python3
"""PreToolUse[Bash] hook, gate 18. Outward-facing work does not ship unrefuted.

THE RULING, 2026-09-01: money, irreversibility, or anything outward-facing — a
reviewer runs, or the work does not ship.

v2, after a refuter found nine defects in v1. The four that mattered:

  D1 CRITICAL  "this turn" did not exist. Nothing ever cleared the flag, so one
               review licensed every ship on the machine for days. The gate was
               not leaky; it was OFF. The flag now carries a TIMESTAMP, EXPIRES,
               and is CONSUMED when it permits a ship: one review, one ship.
  D2 CRITICAL  a lookahead scanned the whole line, so a flag string appearing in
               any free-text argument disarmed the money rule. The signer had
               already fixed this identical bug in itself — "provenance, not a
               free-text string" — and this guard reintroduced it. Quoted text is
               now STRIPPED before any flag is read.
  D5 HIGH      it denied plain reads: a grep for a ship command, a cat of a log,
               a --help. It even denied the write of THIS FILE, because the file
               mentions ship commands. That is the training signal for switching
               a guard off, and a guard that is off guards nothing. Matching is
               now by COMMAND POSITION, never by substring anywhere in the line.
  D8 MEDIUM    v1 crashed to ALLOW on a malformed payload. Wrong polarity for a
               gate whose subject is irreversibility. It now fails CLOSED.

HONEST LIMIT, not fixed and not fixable here: the flag lives under the same uid
as the agent, so it can be forged in one unguarded call, and a reviewer spawned
with a trivial prompt sets it exactly like a real one. This is detection, not a
cage — the same limit the signer states about itself.
"""
import json, os, re, sys, time

FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-refuter-ran.flag")
TTL = 1800  # 30 min. A review older than this is not about the thing being shipped.

QUOTED = re.compile(r"""'[^']*'|"[^"]*\"""", re.S)
SPLIT = re.compile(r"[;\n]|&&|\|\||\|")
ENVASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PRE = ("env", "sudo", "time", "nohup", "command", "exec")


def segments(cmd):
    """Yield command-position tokens per segment, with quoted text removed.

    Stripping quotes first is what stops a free-text argument carrying a flag,
    and stops a search pattern from looking like a ship."""
    for seg in SPLIT.split(QUOTED.sub(" ", cmd)):
        toks = seg.split()
        while toks and (ENVASSIGN.match(toks[0]) or toks[0] in PRE):
            toks.pop(0)
        if toks:
            yield toks


def is_ship(toks):
    """Return why this segment ships, or None."""
    name = os.path.basename(toks[0])
    rest = toks[1:]
    flags = set(rest)
    if "--help" in flags or "-h" in flags:
        return None                       # asking how is not doing
    if "--dry-run" in flags:
        return None                       # a rehearsal is not a ship

    def has(*w):
        return any(x in rest for x in w)

    if name == "git" and has("push"):
        return "a push reaching a remote"
    if name == "gh":
        pair = rest[:2]
        if pair in (["repo", "edit"], ["repo", "delete"], ["repo", "create"]):
            return "a repository change"
        if pair in (["pr", "create"], ["release", "create"],
                    ["release", "upload"], ["workflow", "run"]):
            return "a publish"
        if rest[:1] == ["api"] and (has("-X", "--method")
                                    or has("POST", "PATCH", "PUT", "DELETE")):
            return "a writing api call"
    if name in ("wrangler", "npx") and has("deploy", "publish"):
        return "a deploy reaching a live surface"
    if name in ("netlify", "vercel") and (has("deploy") or "--prod" in flags):
        return "a deploy reaching a live surface"
    if name.startswith("deploy"):
        return "a deploy script"
    if name in ("bash", "sh", "zsh") and rest and os.path.basename(rest[0]).startswith("deploy"):
        return "a deploy script"
    if any(t.endswith("signer.py") for t in toks) and has("transfer"):
        return "a value transfer"
    if any(t.endswith("rendezvous.py") for t in toks):
        # OUTBOUND first. v1 guarded the INBOUND verb and its own comment claimed
        # the opposite of what the code did.
        if has("howl", "sign", "invite"):
            return "a signed record leaving for another agent"
        if has("anchor"):
            return "an on-chain anchor"
        if has("ingest"):
            return "a signed record being applied"
    return None


def flag_valid_and_consume():
    """One review licenses ONE ship, and only for a bounded time."""
    try:
        age = time.time() - os.path.getmtime(FLAG)
    except OSError:
        return False
    if age > TTL:
        try:
            os.remove(FLAG)
        except OSError:
            pass
        return False
    try:
        os.remove(FLAG)               # consume: the next ship needs its own review
    except OSError:
        pass
    return True


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason}}))
    sys.exit(0)


def main():
    raw = sys.stdin.read()
    try:
        d = json.loads(raw or "{}")
        cmd = (d.get("tool_input") or {}).get("command", "") or ""
        if not isinstance(cmd, str):
            raise TypeError("command is not a string")
    except Exception as e:
        deny("GATE 18: the ship guard could not read this command (%s), so it "
             "cannot tell whether it ships. Refusing rather than permitting."
             % type(e).__name__)
    why = None
    for toks in segments(cmd):
        why = is_ship(toks)
        if why:
            break
    if not why:
        return
    if flag_valid_and_consume():
        return
    deny(
        "GATE 18 adversarial-pass: this is %s, and no adversarial reviewer ran "
        "for it. The ruling of 2026-09-01 is that a reviewer runs or the work "
        "does not ship.\n\n"
        "Spawn a refuter, cold-reader or mechanism-auditor against the claim this "
        "ship depends on, then ship. One review licenses ONE ship and expires in "
        "30 minutes. If you judge a review genuinely unnecessary here, say so to "
        "the operator and let him decide — do not route around this." % why)


main()
