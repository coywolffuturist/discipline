#!/usr/bin/env python3
"""Stop hook, gate 19. A done claim must carry a PER-CRITERION posterior.

WHY THIS EXISTS. Gate 19 recorded four firings in one day and every one of them
was a real number, so the gate works when it is reached. The failure is that it
is reached rarely: the turn ends, the work looks finished, and the claim goes
out as "done" with no number against it at all.

WHY PER-CRITERION, which is the part a single number hides. The ruling of
2026-09-01 is that the posterior is gated by the WORST failure mode, not the
best subsystem. The two honest firings on record both split the number:

    "the archive is complete and restorable — 0.95. That it stays current — 0.4:
     it is a snapshot that will not track tomorrow's changes."
    "the watcher works and cross-verifies — 0.9. That it keeps working — 0.7:
     public RPCs change policy without notice, and I depend on three."

One averaged number would have reported 0.7 and 0.8 and concealed both risks.

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
