# Gate 19 — state-the-posterior

    order:  19. VERIFY, LAST. Every other gate produces evidence; this one
            prices it. Nothing adversarial-pass finds can be priced before it
            has run, so this gate reads what that one returned.
    forms:  skill · hook
    ruled:  the operator, 2026-09-01 — full moon. A hook refuses a done claim
            with no per-criterion posterior. Every other form is inapplicable,
            not deferred.

---

## The read

**Before any done / ready / clean / it-works claim: state the posterior, per
criterion, and name what each number rests on.**

The pair to gate 08. That gate makes you commit to a number before the evidence
exists; this one makes you update it after, against the same outcome. **A
posterior is not a feeling and it is not a second opinion — it is the prior,
moved by what the cycles actually returned.**

**Per criterion, and that is the whole ruling.** The number is gated by the
WORST failure mode, not the best subsystem. One average conceals exactly the
thing worth reporting. Both honest firings on record split it:

> Archive complete, clean, byte-identical, restorable — **0.95**, all four
> checks against the artifact. Durability **0.4 → 0.8**: two machines, but same
> house, and it's a snapshot that won't track tomorrow's changes

> the watcher works and cross-verifies — **0.9**. That it keeps working —
> **0.7**: public RPCs change policy without notice, and I now depend on three.

Read the first one closely: **0.4 → 0.8** is the prior MOVED, which is what a
posterior is. An earlier version of this file quoted that as a flat 0.4 — it
reported the prior as the posterior, in the gate whose whole read is that the
two differ. A refuter caught it. `lint/quotes.py` now fails the build when a
quote drops a number its source row carries.

Averaged, these report 0.875 and 0.8 — numbers that sound like health and hide a
snapshot going stale and three dependencies outside my control.

**The .95 is an assertion gate, not an allocation gate.** It governs what may be
stated to the operator as fact. It never governs how much to commit to a bet;
sizing follows payoff, and reading it as permission to act was corrected on the
record.

**The failure this gate actually has is silence, and the record proves it.**
Four firings, all FIRED — and **two of the four artifacts are the literal
placeholder `below`**. The gate reported itself fired, twice, with no number
recorded at all. Half its evidence is a promise that the number appears
somewhere else.

The second failure is a number that cannot move. A prior set against a
different outcome than the one the evidence answers updates on nothing, and the
row must go BLOCKED rather than carry an invented posterior. That is worse than
no prior: it looks like rigour.

## The intent

Make every claim of doneness carry a price the operator can argue with, and put
the worst subsystem in front of him rather than behind an average.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: prior → evidence → posterior, per criterion, gated by the worst failure mode | before any done claim |
| **hook** | `hooks/hook_posterior.py`, `Stop` — a turn that changed something ends with the question restored | every build turn |

**The hook restores the question; it cannot check the answer.** No pattern tells
a real posterior from a plausible one, and the hook does not try. **Gate 18 is
what tests whether the number was earned** — that is the division of labour, not
a gap in this gate.

**Its own flag, and that is load-bearing.** `mark_build.py` writes one flag per
consumer because a cold reader proved that `owe_table.py` CONSUMES the shared
build flag, so whichever `Stop` hook drew second saw nothing and had been firing
on luck. Adding a consumer means adding a flag.

**No tool, no code, no agent.** A number that summarises evidence a machine did
not gather cannot be computed by that machine, and an agent without the build
context has nothing to price. Those forms are inapplicable, not deferred.

## Disproof

Refuted if this gate reports FIRED with a number, and the claim it priced turns
out false for a reason the number should have covered.

**Watchable, and the record already refutes the easy reading.** Two of four
firings recorded `below` instead of a number, which means a FIRED row here is
not yet evidence that a posterior was stated. Until an artifact is required to
CONTAIN a number, this gate's own firing record cannot be trusted at face value
— and saying so is the gate working on itself.

The N/A trigger is checkable against this file: **nothing is being claimed done.**
On a turn that ends in a done claim, N/A is visibly false.

**REVISIT** if firings begin carrying one number instead of a per-criterion
split — that is the average returning, and it is the failure the ruling names.
