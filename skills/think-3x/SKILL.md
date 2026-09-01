---
name: think-3x
description: Design discipline before building anything non-trivial. THREE thinks then build — Think 1 best idea, Think 2 red-team it (as the auditor paid to kill it), Think 3 synthesize into something better than either; build the SYNTHESIS, not Think 1. Show all three thinks in plain text before code. For a mechanism others interact with, Think 2 MUST invoke adversarial-inverse. Supersedes think-twice-build-once; feeds .95 (design ≠ verification). Trigger: about to build something non-trivial, or "think 3x" / "3x" / "think three times".
---

# Think 3x Then Build

Never build the first idea. Build the synthesis of the first idea and
its strongest refutation.

## The three thinks

**Think 1 — Best idea.** The strongest design you can propose for the
goal. Commit to it fully; don't strawman it so the red-team is easy.

**Think 2 — Red-team it.** Attack Think 1 as the external auditor paid
to kill it:
- **Artifact** — does the benefit come from the design, or from a
  measurement / setup / sampling quirk?
- **Won't generalize** — would it survive a fresh case, different
  inputs, out-of-sample? A small sample?
- **Over-engineering** — is there a simpler fix that gets 80%? Does
  the complexity add a failure surface?
- **Cost / efficiency** — what doesn't scale: fees, overhead, fixed
  allocations that dilute?
- **Beat baseline?** — state the honest marginal gain over doing
  nothing / the incumbent.

**Think 3 — Synthesize.** Combine Think 1 with what the red-team
exposed into a design better than either alone. The red-team usually
relocates the real root cause; Think 3 attacks *that*, and often
reuses an already-validated component the naive idea ignored.

**Then build the synthesis** — not Think 1.

## Rules

- **Show all three thinks in plain text before writing code.** The
  reasoning must be auditable — no silent collapse to "I'll just build it."
- **Scale to the task.** Trivial mechanical edits skip it; new
  strategy / substrate / architecture / non-obvious refactor don't.
- **The synthesis is still subject to everything else.** Run it,
  verify it, name the residue. Think-3x replaces *how you design*, not
  *how you confirm*.

## Composition

- **substrate-search** — whenever Think 1 or Think 3 proposes new
  substrate, answer first "what existing piece is insufficient?" The
  strongest synthesis usually REUSES a validated component; new
  substrate is a Think-3 last resort, not a default.
- **karsholto** — the red-team's over-engineering lens and the
  synthesis both bend toward the smallest correct brick. Think-3x is
  not a license to build bigger.
- **adversarial-inverse** — *related to Think 2 but not the same; not
  redundant.* Think 2 targets DESIGN failure (artifact, won't-
  generalize, over-engineering, beat-baseline) for any build.
  adversarial-inverse targets PARTICIPANT EXPLOITATION (an adversary
  gaming the mechanism for +EV harm) and is mandatory ONLY for
  cooperative-economic mechanisms (treasuries, fees, slashing, jury
  triggers, eligibility). When the thing built is a mechanism others
  interact with, Think 2 MUST invoke adversarial-inverse as a required
  lens; otherwise Think 2 runs the design-failure lenses above.
- **root-cause** — Think 2 frequently reveals the stated problem was a
  symptom. Think 3 must target the root, not the symptom. With .95 +
  karsholto this is the verify-phase triad.
- **95-percent-rule** — after building the synthesis, the posterior
  gate still applies. Design discipline feeds verification discipline;
  they are NOT substitutes. A well-synthesized design with an
  unverified user-outcome is still unverified.

## The one-line summary

**Best idea → red-team → synthesis → build the synthesis. The first
idea is never the thing you build.**
