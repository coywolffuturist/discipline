---
name: adversarial-pass
description: Before claiming any non-trivial work done, run an INDEPENDENT adversarial pass — the author can't be the only reviewer, because self-grading is structurally blind to the failures where the builder's own mental model is wrong. Live-fire the user-outcome path adversarially (repeatedly for nondeterministic surfaces), reading for the failure you'd least expect; for high-stakes work, spawn the `refuter` agent to REFUTE, not bless. This is how you EARN the .95 posterior, not assert it. Fires in VERIFY after .95 + nomess. Shorthand "adversarial-pass" / "refute it".
---

# /adversarial-pass — the author can't be the only reviewer

Every confidence claim you produce is the builder grading the builder.
That passes most of the time and hides exactly the failures that
matter: the ones where the builder's mental model is itself wrong, so
the same reasoning that shipped the bug also certifies it clean.
Self-review is the blind spot; an independent pass closes it.

## When it fires

VERIFY phase, after `.95` + `nomess`, before claiming done on
non-trivial or high-stakes work. (Routine edits: a live-fire
self-adversary is enough — see scaling below.)

## The pass

1. **Live-fire against reality, adversarially.** Not "the diff looks
   right" — execute the user-outcome path itself, multiple times for
   nondeterministic surfaces (LLM calls, races, ordering), and READ
   the output for the failure you'd least expect. Live-fire is the
   cheapest adversary.
2. **Independent reviewer for high-stakes work.** Spawn the `refuter`
   agent — a fresh context that did not build the thing — handing it
   the claim plus artifacts and an explicit instruction to REFUTE.
   Never assume a spawned agent infers the adversarial role; the role
   comes from the spawn, not from inheritance. A *different model* than
   the builder strengthens the independence further.
3. **The reviewer hunts the lie, not blesses the work.** Prompt it to
   assume the change is subtly broken and find how. A reviewer asked
   "does this look right?" will say yes; ask "where is this wrong?"
4. **Break the gate.** If this work produced a CHECK — a test, a
   verifier, a health gate, a lint, a monitor — then reintroduce the
   failure it exists to catch and confirm it goes RED. Refutation
   argues against a claim; this falsifies by experiment, and it is the
   only thing that separates a gate from a decoration. A gate that has
   never failed is not a gate. Where practical, record the two numbers
   (healthy vs broken) so the threshold is evidenced rather than
   guessed.

## Scale to stakes

- Money / security / irreversible / load-bearing → always an
  independent refuter.
- Routine UI / docs / mechanical edits → live-fire self-adversary
  suffices; don't spawn an agent to check a typo fix.

## Self-check

- Did the same reasoning that built this also certify it? Then it's
  unreviewed.
- Did I run the real user-outcome path, or inspect the code that
  should produce it?
- For a nondeterministic surface, did I run it enough times to see the
  bad draw?
- Was the reviewer asked to refute, or to bless?
- If I built a check, have I ever SEEN it fail? If not, I have no
  evidence it can. A checker that passes vacuously is worse than none:
  it converts an unknown into a false assurance.

## One-line summary

**Self-grading is structurally blind. Live-fire it adversarially, and
for anything that matters, have different reasoning try to REFUTE it —
that's how the .95 posterior is earned, not asserted.**

## Cross-references

- `95-percent-rule` — this is how you EARN the posterior, not assert it.
- `refuter` agent — the independent reviewer step 2 spawns.
- `discipline` — the VERIFY-phase gate this completes.
