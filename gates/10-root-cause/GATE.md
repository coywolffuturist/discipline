# Gate 10 — root-cause

    order:  10. VERIFY, after disprove-first closes DESIGN and before karsholto.
            You cannot count what a fix adds until you know how many fixes there
            are. NOT "after the posterior" — that is gate 19 and it runs LAST.
            An earlier version of this line said so; it was a stale artifact of
            the pre-renumber deck, where this gate was 11 and the posterior 20.
    forms:  skill
    ruled:  the operator, 2026-09-01 — full moon. Skill only: the fault count
            cannot be machine-decided. Every other form is inapplicable, not
            deferred.

---

## The read

**Something failed. Before fixing anything, ask how many distinct faults there
actually are.**

The count is the gate. Not "what is the cause of this symptom" — that question
still lets you fix each symptom in turn and call each fix a root-cause fix. The
question is how many faults produced all of them, asked before the first repair.

The record says the answer is almost never the symptom count:

- six symptoms, one cause — failure, ignorance and health collapsed into two
  states. Fixing the collapse fixed all six
- two symptoms, one cause — a lying doctor and a broken open, both an inverted
  predicate
- ten scripts, one cause — adhoc-signed interpreters estate-wide, not ten bad
  scripts
- five files red, one cause — an interpreter swap, not a sentinel-design fault

Every one of those, taken symptom-first, would have produced the wrong number of
fixes. That is the cost: not a missed bug, but **N wrong repairs that each
appear to work**, and a class left live behind them.

**The cause is usually one level up from where it hurts.** A money cap reopened
three times because every hostile number was validated on the way in as an
*amount* while the *accumulator* was left unguarded — the log was treated as
output when it was also input. Frequency misleads the same way: which interpreter
failed most often decided the ORDER of repair, never the cause.

**And a cause can be a claim, not a line of code.** One failure's cause was that
a freshness claim inside a howl is self-falsifying — posting it makes it false.
No code was wrong. Twenty-one defects in one hook resolved to a single fault of
this kind: same-privilege enforcement cannot bind the process it runs inside.
That is not a bug to patch; it is a property that invalidates the design.

## The intent

Fix the fault, once, so the class stops — instead of repairing each place the
class surfaced and leaving it live everywhere else.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: count the faults before fixing any, look one level up, and treat frequency as ordering rather than cause | every repair |

**Skill only, and this is a ruling rather than a gap.** How many distinct faults
underlie a set of symptoms is a judgement about a specific system. No pattern
decides it, no count of failing tests reveals it, and an agent without the
context cannot make it. A green check standing in for that judgement would be
the ritual this suite forbids, and inventing a mechanical form to make the gate
look better-equipped is exactly the unjustified substrate gate 05 refuses.

The nearest mechanical neighbour already exists elsewhere: **gate 14 cold-read**
sweeps the whole CLASS once a cause is named. This gate finds the cause; that one
makes sure the fix is not applied only to the instance you tripped over.

## Disproof

Refuted if this gate reports FIRED, a cause is named and fixed, and the same
class of failure recurs.

**Watchable — and the honest state is that this gate has not yet watched it.**
The lesson *a hardcoded list needs a checker, not a more careful author* was
recorded, and the list it described was wrong two further times afterwards.
Those later instances are attested by the code, NOT by the firing corpus: that
lesson is the corpus's final row, so nothing in it follows. An earlier version
of this file claimed the record showed the recurrence. It does not.

The narrower claim survives, and it is the one that matters: the cause was named
correctly, the named mechanism was never built, and the class stayed live.
Naming a cause is necessary and is not sufficient.

The N/A trigger is checkable against this file: **nothing failed.** All three
N/A firings open with the same phrase — *"trigger is fixing a symptom"* — then
give the reason: one says *authoring, not repair*; the other two say *nothing
was broken*. On a turn that fixed something, N/A is visibly false.

**REVISIT** if the record shows firings that name a cause without ever stating
the fault COUNT — that would mean the gate has decayed back into "what caused
this symptom", which is the question it was written to replace.
