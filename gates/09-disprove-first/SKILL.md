---
name: disprove-first
description: Before building, name the observation that would prove the design wrong — then produce it and watch the check go RED before trusting it green. A design that forbids no observation explains nothing; a test that cannot fail certifies nothing. Applies to instruments as much as to work: if you build a CHECK, break what it detects first. Registered-but-unrun is BLOCKED, not fired.
---

# Disprove first

**Name the observation that would refute the design, then confirm that
observation can actually occur.**

The operational form is one sentence, written before code:

> *If X happens, this design is refuted.*

Then produce X deliberately and watch the check go **RED**, before anyone trusts
it going green.

## The rule that separates this from a habit

**Registering the refutation is not firing it.** If the test has not been RUN
and seen to fail, the row is BLOCKED — not FIRED. A registered test nobody ran
is a promise, and this gate does not accept promises.

## Where it comes from

Two lineages solving different problems.

**Falsifiability.** A theory earns standing by forbidding observations, not by
accumulating confirmations. A good explanation is *hard to vary* — change any
part and it stops explaining. A claim you can rescue from any evidence by
adjusting it was never load-bearing.

**Pre-registration.** Medicine and psychology arrived at the same instrument
from the other direction: not to grade theories, but to stop the hypothesis
being invented after the data is seen.

Software has the same shape in test-driven development. Red before green is not
workflow decoration — it is the only proof the test is wired to the thing it
claims to test.

## The part that matters most here: break your own instruments

Apply it to the **instruments**, not only to the work.

> **If you build a CHECK, break what it detects and watch it go red before you
> trust it.**

The failure this guards against is not a wrong answer. It is **a gate that
reports health it does not have** — and that failure is silent, because a green
check and a broken check look identical.

Recorded, repeatedly: a guard whose flag was never cleared, so the gate was OFF
in every state and said nothing. A block appended after `exit 0`, dead code,
silent in all four states. A sweep that read symbolic links instead of their
targets and called a class clean while two live jobs were down. A gate that
threw on a missing import and therefore "caught" everything. **None was found by
reading. Every one was found by baiting.**

## The move

1. Write the refutation sentence before the code.
2. Produce the damage the check should catch.
3. Watch it go RED. If it does not, the check is not wired — fix that first.
4. Restore, and watch it go GREEN.
5. If a check ships, its bait ships with it. A check with no bait that was seen
   to fail is an assertion, not evidence.

**A bait must also be unable to exempt itself.** If the rule is "every check has
a bait", then that rule needs a bait too: a new unbaited check must fail, and
deleting the baseline must not reset the ratchet.

## When it is N/A

Nothing is being built or checked. Authoring prose, reading, answering a
question — there is no design to refute. N/A is legal only by that trigger, and
on a turn that shipped a check it is visibly false.
