# Gate 18 — adversarial-pass

    order:  18. VERIFY, last before the posterior. Nothing it finds can be
            priced until it has run.
    forms:  skill · agent · code (adopted)
    ruled:  the operator, 2026-09-01 — full moon. Money, irreversibility or
            anything outward-facing: a reviewer runs, or the work does not ship.
    where:  the code form is the estate `pre-push` hook on the primary
            workstation, registered by `core.hooksPath`, opt-in per repo via a
            `.gate18-guarded` marker in the repo root.

---

## The read

**The author cannot be the only reviewer.** Spawn a reader that does not share
your context and brief it to REFUTE the claim, not to bless it.

The failure is not carelessness. It is that the reasoning which produced a thing
also certifies it, so the certification inherits every error the production had.
Measured across one day: 34 encounters, 19 fired, **15 blocked**, every block
reading "no independent reviewer ran".

What reviewers found on the days they did run, each time on work the author had
already verified and believed correct:

- a sentinel, break-tested and believed sound — **six defects**, three of which
  printed GREEN over a real failure
- a money path already hardened twice — **three high-severity defects**, each
  reopening a cap believed enforced
- a repository hours from publication — its scrubbed history and its remote were
  **disjoint object graphs**

## The intent

Make a claim survive someone trying to break it, so a posterior rests on evidence
the author could not have manufactured.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: what to refute, how to brief a reviewer, why self-review is not this gate | before any non-trivial claim |
| **agent** | `refuter` — read-only, no build context, briefed to find the failure | money · irreversible · outward-facing |
| **code** | ADOPTED — the estate `pre-push` hook refuses a push with no review in scope, consumes the review, and expires it at 30 minutes | every push from a guarded repo |
| **hook** | `mark_refuter.py`, `PostToolUse[Agent]` — records that a reviewer ran. **Install with the code form or neither:** pre-push reads a flag only this writes | paired |

## Why the code form is at the action point, and not in the command text

**Three versions of a `PreToolUse[Bash]` guard were built and all three were
refuted.** Each tried to decide "is this a ship?" by parsing the command string.
Each was defeated by a shape it had not imagined: a flag word inside a quoted
argument; an `ssh` payload stripped along with the quotes; then `cd X && ssh`,
an unquoted remote command, `caffeinate -i`, `timeout`, base64 through a pipe.
The third version simultaneously **allowed** the ordinary shape of a remote push
and **denied** a plain `grep` of a guarded file — the worst of both errors, and
the second is what gets a guard switched off.

Shell has unbounded ways to express one action. That arms race cannot be won by
a denylist of shapes, and each version's fix opened a hole wider than the bug.

This hook's own header, written 2026-07-13 and unread by me until the third
refutation, already stated the answer:

> *pre-push is the one choke point every route to a remote must cross.*

git runs it however the push is invoked — alias, wrapper, ssh, chained,
unquoted. **There is no command shape to evade, because the command is not what
is examined.** The Bash-text guard is retired; it is not narrowed, because its
coverage was illusory and its false denials were real.

## What is still unguarded, named rather than implied

The push path is covered. These are not, and each needs a check at ITS action
point rather than in a command parser:

- **deploy** — inside the deploy script
- **value transfer** — inside the signer, which already owns a leash
- **a signed record leaving for another agent** — inside the rendezvous tool

They were never guarded; the retired hook only appeared to guard them.

## Disproof

**Mechanical, and it points at the enforcement rather than the reviewer:**
refuted if a push from a guarded repo completes with no review in scope.

That is directly testable and was tested — the hook was baited in four states:
no review (refused), fresh review (allowed), a second push on the same review
(refused, because the review is consumed), and an undeletable flag (refused,
rather than licensing an unbounded number of pushes, which is how the first
version failed).

**One bait that mattered more than the others:** the block was first appended
after an `exit 0` and was dead code. It produced no output in any state and
looked like a silent pass. Baiting caught it; reading would not have.

The weaker human half is kept: refuted if a reviewer passes a claim later found
false for a reason it had the access and brief to catch. It tests judgement and
could never have caught any of the twelve hook defects.

**REVISIT** when the three unguarded action points above have checks, or if a
push is ever found to complete without a review in scope.
