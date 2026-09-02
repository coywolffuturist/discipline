# Gate 06 — compile-it

    order:  06. DESIGN, after substrate-search and before think-3x. Decide
            whether a model is needed at all before designing what it does.
    forms:  skill · code
    ruled:  the operator, 2026-09-01 — full moon. Code counts derivations across
            the transcript and flags the second. Hook, tool and agent are
            inapplicable, not deferred.

---

## The read

**Before designing an LLM step, ask whether it should be deterministic CODE.**
If it repeats, is mechanical, is stable and is checkable — write the hard code.
Agents think; code does.

**Crystallize on the second or third repeat, not the first.** A one-off is not a
script waiting to be written, and the recorded N/A rows say exactly that: *a
one-shot correction* · *a one-shot verification* · *a repeating mechanical LLM
step, but a one-off archive*. **16 FIRED, 14 N/A** — a 47% N/A rate, and that is
the gate working rather than failing. Compiling a one-off is the unjustified
substrate gate 05 refuses.

(An earlier version called this "the highest N/A rate in the VERIFY-adjacent
set". That set was defined nowhere, and the claim was false besides: vizcheck
sits at 12 of 15, or 80%.)

**The trigger fired on me while I was building this suite, and nothing caught
it.** The two-step *copy CONDUCTOR.md outward, then regenerate the derived
bundle* was typed by hand three times in one session, and the build went red
after each edit because one half was forgotten. The third repeat produced
`scripts/install.sh`. I noticed on the third by accident. That is precisely
what the code form now counts.

The strongest firings on record replace a judgement, not just typing:

> All three are deterministic code. The probe replaces a judgement I was making
> by eye every watch — and getting wrong.

> `den-doctor` now uses jq and shell — the interpreter that could prompt is
> gone, not merely reconfigured.

## The intent

Stop paying a model to redo a mechanical thing it has already worked out, and
remove the judgement calls that were being made by eye and got wrong.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: repeats · mechanical · stable · checkable, and crystallize on the second or third | before designing an LLM step |
| **code** | `gates/06-compile-it/repeats.py report` — shapes repeated three or more times in the shared (boot-scoped) log | when the table is filled |

**Shared with gate 03 collapse-round-trips, and separate rows.** Both count a
repeat. Gate 03 reads **back-to-back** and batches; this reads **three in the shared
log** and compiles. One mechanism, two readings.

**The log is not turn-scoped, and not session-scoped either.** It carries no
timestamp, session id or pid, and `$TMPDIR` is per-user-per-boot and shared by
every concurrent process — a reviewer measured 533 lines across two live
sessions. It is a BOOT-scoped, CROSS-PROCESS reading. A shape reaching three
across six hours and two agents is weak evidence for compiling; three in one
turn by one agent is strong. The counter cannot tell you which you have.

**The count is evidence, not a verdict.** A shape can legitimately recur —
running the build after each of three edits is not a script waiting to be
written. `repeats.py` says so in its own output rather than presenting a number
as a finding.

**No hook of its own** — it shares gate 03's logger, because a second
`PostToolUse[Bash]` hook writing a second log would be the duplicate substrate
this gate exists to prevent. **No tool, no agent:** whether a repeat is
mechanical and stable enough to compile is a judgement about the work.

## Disproof

Refuted if this gate reports FIRED, a step is compiled, and the code then needs a
model in the loop anyway — which means the step was not stable and the
crystallization was premature.

**Watchable both ways, and it has fired in both.** `install.sh` and `capture.py`
were real crystallizations on the third repeat. Against them: the counter itself
must not become the trigger. **An absent or empty log reports UNVERIFIED, not
zero** — a counter that reads a missing log as "nothing repeated" reports health
it does not have, which is the failure an eval already committed here once.

**REVISIT** if compiled steps start needing repair more often than the manual
ones did — that is premature crystallization, and the remedy is a higher
threshold, not more code.
