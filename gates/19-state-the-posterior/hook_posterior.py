#!/usr/bin/env python3
"""Stop hook, gate 19. A done claim must carry a PER-CRITERION posterior.

WHY THIS EXISTS. Gate 19 recorded four firings in one day and TWO of the four
artifacts are the literal placeholder "below" — the gate reported itself FIRED
with no number recorded. The failure is silence: the turn ends, the work looks
finished, and the claim goes out as "done" with no number against it.

WHY PER-CRITERION, which is the part a single number hides. The ruling of
2026-09-01 is that the posterior is gated by the WORST failure mode, not the
best subsystem. The two honest firings on record both split the number:

    "Archive complete, clean, byte-identical, restorable — 0.95, all four checks
     against the artifact. Durability 0.4 -> 0.8: two machines, but same house,
     and it's a snapshot that won't track tomorrow's changes"
    "The watcher works and cross-verifies — 0.9. That it keeps working — 0.7:
     public RPCs change policy without notice, and I now depend on three of them"

One averaged number would report 0.875 and 0.8 and conceal both risks. Note the
FIRST one: 0.4 -> 0.8 is the prior MOVED. An earlier copy of this docstring
quoted it as a flat 0.4 — the prior reported as the posterior, inside the hook
that exists to demand a posterior. A refuter caught it.

IT DOES NOT READ THE ANSWER. This hook cannot tell a real posterior from a
plausible one, and does not try. It restores the question at the moment the
question is skipped. Gate 18 is what tests whether the number was earned.

Own flag, per the rule in mark_build.py: a shared flag lets whichever Stop hook
draws first silence the rest.
"""
import json, os

FLAG = os.path.join(os.environ.get("TMPDIR", "/tmp"), "coywolf-posterior-owed.flag")

if not os.path.exists(FLAG):
    raise SystemExit(0)
try:
    os.remove(FLAG)
except OSError:
    pass

msg = ("GATE 19 state-the-posterior: this turn changed something. Before any "
       "done / ready / clean / it-works claim, state the posterior PER "
       "CRITERION, not as one averaged number — the claim is gated by the WORST "
       "failure mode, not the best subsystem. Name what each number rests on. "
       "If the prior was never set or was set against a different outcome, the "
       "posterior cannot update it: say BLOCKED rather than inventing a number.")

print(json.dumps({"suppressOutput": True,
                  "hookSpecificOutput": {"hookEventName": "Stop",
                                         "additionalContext": msg}}))
