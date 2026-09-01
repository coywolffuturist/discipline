# Gate 08 — set-the-prior

    order:  08. DESIGN, immediately before gate 09 registers the refutation.
            You cannot pre-register the refutation of a claim you have not stated.
    forms:  skill · hook
    ruled:  the operator, 2026-09-01 — full moon. A NUMERIC prior is mandatory.

---

## The read

**Before building, state the user-outcome once and put a number on your
confidence in it.** Not a feeling, not "high" — a number you are willing to be
wrong about in public.

The failure that produced this gate is measurable. Across one day this gate
recorded 37 encounters and **never once went N/A**, which is the signature of a
standard too easy to meet. In those 37, an actual number appeared **three
times**. The posterior gate that closes every completion table was therefore
computing an update against a value that mostly did not exist.

A prior nobody wrote down cannot be updated. What follows is not a posterior; it
is a fresh guess wearing the costume of arithmetic.

## The intent

Make the confidence at the end an UPDATE on a recorded starting point, so a
posterior means something and can be checked afterwards.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | state the outcome in one sentence and a numeric prior, before code | every non-trivial build |
| **hook** | `hook_prior.py`, Stop event: when a completion table is owed, demands the numeric prior by name | every turn that changed something |

No code form: whether a stated number is *honest* is not machine-decidable, and
a check that only counts digits would pass `0.99` on anything.

No agent form: an agent without context cannot know what outcome was intended.

## Disproof

This gate is refuted if a completion table carries a numeric prior and a numeric
posterior, and the posterior turns out to be unrelated to the prior — the number
stated at the start playing no part in the number stated at the end.

That observation is watchable in the corpus: every table is harvested with its
gate rows, so prior and posterior can be compared across turns. The check has
not been run. It cannot run until enough tables carry both numbers, which is the
point of the hook.

**REVISIT** if a model can reliably estimate its own calibration, at which point
the number could be produced and audited mechanically rather than asserted.
