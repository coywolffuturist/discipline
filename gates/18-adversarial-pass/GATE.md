# Gate 18 — adversarial-pass

    order:  18. VERIFY, last before the posterior. Nothing it finds can be
            priced until it has run.
    forms:  skill · agent · hook (two hooks — see the table)
    where:  hooks register on the PRIMARY WORKSTATION, not the machine this
            repo lives on. A path here resolves per-host; the estate spans two.
    ruled:  the operator, 2026-09-01 — full moon. Money, irreversibility or
            anything outward-facing: a refuter runs, or the work does not ship.

---

## The read

**The author cannot be the only reviewer.** Spawn a reader that does not share
your context and ask it to REFUTE the claim, not to bless it.

The failure that produced this gate is not carelessness. It is that the same
reasoning which produced a thing also certifies it, so the certification
inherits every error the production had. Measured across one day: 34 encounters,
19 fired, **15 blocked** — and every block reads the same, "no independent
refuter ran, unverified whether…".

What the refuters found on the days they did run is the argument:

- a sentinel that had been break-tested and believed sound — **six defects**,
  three of which printed GREEN over a real failure
- a money path already hardened twice — **three high-severity defects**, each
  reopening a daily spend cap that was believed enforced
- a repository hours from going public — its scrubbed history and its remote
  were **disjoint object graphs**, so every fix sat on a machine while the
  unscrubbed tree sat on the server

Each was found after the author had verified the work and believed it correct.

## The intent

Make the claim survive someone who is trying to break it, so a posterior rests
on evidence the author could not have manufactured.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: what to refute, how to brief a refuter, why self-review does not count | before any non-trivial claim |
| **agent** | `refuter` — read-only, no build context, briefed to find the failure and report the lie | money · irreversible · outward-facing |
| **hook** | `hooks/hook_ship_guard.py` — refuses an outward-facing command when no review is in scope | every ship |
| **hook** | `hooks/mark_refuter.py` — records that a review ran. **Install both or neither:** the guard reads a flag only this writes, so the guard alone denies every ship forever with no way to clear it | paired with the guard |

The hook is the ruled half: *runs, or the work does not ship*. Without it the
rule is a resolution, and this gate was blocked 15 times while the resolution
was in force.

## Disproof

**Mechanical, and it points at the hook rather than the reviewer:** this gate is
refuted if any ship command reaches execution with no review in scope. A refuter
demonstrated exactly that on 2026-09-01 — a stale flag licensed an unrefuted push
— which is why the flag now expires and is consumed on use.

The weaker, human half: refuted if a reviewer passes a claim and that claim is
later found false for a reason it had the access and brief to catch. Kept, but it
tests the reviewer's judgement and could never have caught the nine hook defects.

Watchable: refuter verdicts are in the transcript and defects are in the record,
so a pass followed by a defect is a matched pair. **Not yet observed.** Every
refuter that ran on a non-trivial claim so far has found something, which is
evidence the gate works and also means its disproof is untested.

**REVISIT** if refuters become cheap enough to run on every claim rather than on
the ruled three categories, or if a refuter is ever caught passing something the
author then broke.
