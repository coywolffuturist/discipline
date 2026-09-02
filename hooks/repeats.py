#!/usr/bin/env python3
"""repeats — count command SHAPES, and read the count two ways.

Shared code form for gate 03 (collapse-round-trips) and gate 06 (compile-it).
Two gates, one mechanism, separate readings — the same arrangement capture.py
has with gates 16 and 17. Neither gate may hide inside the other's row.

WHY ONE MECHANISM. Both gates are about a repeat. They differ only in the window
and in the remedy:

    gate 03  the SAME shape twice in a row, right now      -> batch them
    gate 06  the SAME shape a third time, across the turn  -> write the script

WHY IT EXISTS AT ALL. Gate 06's own trigger fired on me while I was building the
suite: the two-step `cp CONDUCTOR.md outward; regenerate the bundle` was typed
by hand three times in one session, and the build went red after each edit
because one half was forgotten. The third repeat produced scripts/install.sh.
Nothing counted those three; I noticed by accident on the third. This counts.

WHAT IT DOES NOT DO. It does not decide that a repeat SHOULD be collapsed or
compiled. A shape can legitimately recur — a build run after each of three
edits is not a script waiting to be written. The count is evidence; the
judgement is the gate.

  install:  PostToolUse[Bash] -> repeats.py            (logs one line per call)
  read:     repeats.py report                          (both readings)
"""
import json, os, re, sys, collections

LOG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-cmd-shapes.log")

# Quoted text is DATA, not action. mark_build.py learned this the expensive way:
# matching command TEXT made `grep "rm " file` look like a deletion, and the
# guard fired on nearly every turn until it was anchored instead.
_QUOTED = re.compile(r"""'[^']*'|"[^"]*"|<<'?[A-Z]+'?.*""", re.S)
_NUM    = re.compile(r"\b\d+\b")
_PATH   = re.compile(r"(?:~|\.{0,2}/)[\w./~-]+")


def shape(cmd):
    """Reduce a command to what makes it the SAME action as another."""
    c = _QUOTED.sub(" S ", cmd)
    c = _PATH.sub(" P ", c)
    c = _NUM.sub("N", c)
    parts = [t for t in c.split() if t and not t.startswith("-")]
    return " ".join(parts[:4]) or "?"


def log():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    cmd = ((d.get("tool_input") or {}).get("command") or "").strip()
    if not cmd:
        return
    try:
        with open(LOG, "a") as f:
            f.write(shape(cmd) + "\n")
    except Exception:
        pass


def report():
    if not os.path.exists(LOG):
        # An absent log is NOT "no repeats". It means the hook never ran, which
        # is a different answer and must not read as a pass.
        print("UNVERIFIED: %s does not exist — the logger never ran." % LOG)
        return 2
    rows = [l.strip() for l in open(LOG) if l.strip()]
    if not rows:
        print("UNVERIFIED: the log is empty — the logger ran but recorded nothing.")
        return 2

    back_to_back = [a for a, b in zip(rows, rows[1:]) if a == b]
    counts = collections.Counter(rows)
    thrice = [(s, n) for s, n in counts.most_common() if n >= 3]

    print("gate 03 collapse-round-trips — %d call(s) issued back-to-back in the same shape:" % len(back_to_back))
    for s in collections.Counter(back_to_back).most_common(5):
        print("    %-52s x%d" % (s[0][:52], s[1] + 1))
    if not back_to_back:
        print("    none — no shape was issued twice in a row")

    print("gate 06 compile-it — %d shape(s) repeated 3+ times, the crystallize threshold:" % len(thrice))
    for s, n in thrice[:5]:
        print("    %-52s x%d" % (s[:52], n))
    if not thrice:
        print("    none — no shape reached three")
    print("\n%d call(s) logged. A count is evidence, not a verdict: judge whether"
          "\neach repeat was one action split up, or genuinely separate work." % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(report() if len(sys.argv) > 1 and sys.argv[1] == "report" else (log() or 0))
