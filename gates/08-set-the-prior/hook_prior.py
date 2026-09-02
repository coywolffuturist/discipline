#!/usr/bin/env python3
"""Stop hook, gate 08. The completion table must carry a NUMERIC prior.

WHY THIS EXISTS. Gate 08 recorded 37 encounters in one day and never once went
N/A, while an actual number appeared three times. After the operator ruled the
number mandatory on 2026-09-01, the very next four completion tables still had
none — the gate fires BEFORE building and I kept reaching it AFTER.

That is not a memory failure to promise away. It is a gate with no form. This is
the form.

It rides the same flag as the table reminder and stays separate from it, because
no gate may bundle: one row, one reason, so a silent one cannot hide inside
another's message.
"""
import json, os

FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-prior-owed.flag")

# OWN FLAG, not the table hook's. A cold reader proved on 2026-09-01 that
# owe_table.py deletes the build flag and is listed FIRST, so this hook was
# silenced whenever that draw order held. "Read, do not consume" does not help
# when the other hook is the consumer. Consume this one: it is ours alone.
if not os.path.exists(FLAG):
    raise SystemExit(0)
try:
    os.remove(FLAG)
except OSError:
    pass

msg = ("GATE 08 set-the-prior: this turn changed something, so a prior was owed "
       "BEFORE it. State the user-outcome in one sentence and a NUMERIC prior on "
       "it. If you did not set one, the row is BLOCKED — say so rather than "
       "writing a posterior against a number that was never recorded.")

print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
