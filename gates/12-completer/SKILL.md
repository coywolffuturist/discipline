---
name: completer
description: Before declaring done — or writing "follow-up" / "next session" / "separate pass" / "out of scope for now" / "deferred" — check whether the remaining work is a GENUINE blocker (data/decision/access you actually lack, or a distinct new build) or you're just stopping at a convenient slice. "It's big" / "end of session" / "deserves its own session" are cop-outs, NOT blockers. The user outcome is the WHOLE job; finish it, or name the real blocker explicitly. Fires in VERIFY, paired with .95. Shorthand "completer" / "finish the job".
---

# completer — finish the whole job, not a convenient slice

The user outcome is the entire task. The failure this catches: declaring a
slice done and logging "a follow-up" for the rest — a cop-out dressed as
scoping.

## When it fires

VERIFY phase, the moment you're about to:
- claim "done / shipped / handled" while leaving residue, OR
- write "follow-up", "next session", "separate pass", "out of scope for
  now", "deferred", "TODO later", "deserves its own session".

Pairs with .95: .95 asks whether the outcome is verified — completer asks
whether this is the WHOLE outcome, or a slice you quietly scoped down to.

## The test — genuine blocker, or stopping short?

Classify each piece of remaining work.

**Genuine blocker (deferring is honest):**
- Data, a decision, or access you actually lack — a feed that doesn't
  exist, a choice only the user can make, a credential you don't have.
- A distinct NEW build or design — not cleanup of what you started, but a
  separate effort. (Extracting a component = finish now; building the new
  system it becomes = legitimately separate.)
→ Name it explicitly, plus what unblocks it. Never "a follow-up."

**Stopping short (a cop-out — finish it):**
- "It's big" / "it's a lot" — size is not a blocker.
- "End of session" / "we've done enough" — time is not a blocker.
- "Deserves its own pass" / "I'll log a follow-up" — convenience.
- A bounded, completable task you just don't want to push through.
→ Finish it now.

## Rule

Cleanup, extraction, de-tangling, wiring, migration = finish in this pass.
A genuinely new build or design = separate, but say so honestly with the
real blocker named — never as a dodge. If you can't name a genuine blocker,
the job isn't done.

## One-line summary

completer = the user outcome is the whole job; finish it, or name the real
blocker — "it's big" is not a blocker.
