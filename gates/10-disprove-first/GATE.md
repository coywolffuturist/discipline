# Gate 10 — disprove-first

    order:  10. LAST in DESIGN, immediately before code, and immediately after
            gate 09 sets the prior. You cannot pre-register the refutation of a
            claim you have not stated.
    forms:  skill · code   (no hook: the artifact is a red test, not a warning)
    ruled:  DRAFT 2026-08-31. Not yet approved.

---

## The read

### What it is

**Before you build, name the observation that would prove the design wrong —
and confirm that observation can actually occur.** A design that forbids no
observation explains nothing. A test that cannot fail certifies nothing.

The operational form is one sentence written down before code: *"If X happens,
this design is refuted."* Then X is produced deliberately, and the check is
watched going RED, before anyone trusts it going green.

### Where it came from

Two lineages, and they solve different problems.

**Falsifiability.** Popper argued that a theory earns scientific standing by
forbidding observations, not by accumulating confirmations. Deutsch sharpened it
in *The Beginning of Infinity*: a good explanation is **hard to vary** — change
any part and it stops explaining. A claim you can rescue from any evidence by
adjusting it was never load-bearing.

**Pre-registration.** Medicine and psychology arrived at the same instrument
from the opposite direction: not to grade theories, but to stop researchers
inventing the hypothesis after seeing the data. Trial registration became an
ICMJE publication condition in 2005; Registered Reports followed in psychology
around 2013, reviewing the method before results exist.

Software has the same shape in **test-driven development**: write the failing
test first. Red before green is not workflow decoration. It is the only proof
the test is wired to the thing it claims to test.

### How the world uses it

Science registers a hypothesis to prevent post-hoc storytelling. Engineering
writes a failing test to prevent a green suite that asserts nothing. Both are
about the AUTHOR'S honesty toward a future reader.

### How we use it — the cutting-edge part

We apply it to **the instruments themselves**, not only to the work. The rule:
**if you build a CHECK, break what it detects and watch it go red before you
trust it.**

That is a different failure from the one science registers against. Ours is a
gate that reports health it does not have. The evidence is local and repeated,
all of it from 2026-08-31:

* An STE break test read 6 of 6 caught. A missing `import re` made the gate
  throw on every input, so it was refusing everything. Only the ACCEPT cases
  exposed it — the reject cases looked identical to a working gate.
* A census check compared against a stored baseline and treated an ABSENT
  baseline as "no change", so a brand-new log full of errors was invisible.
  Four of five break tests passed; the fifth found the hole.
* A build-detection hook scored read-only monitoring turns as builds, because
  `>/dev/null` matched its redirect pattern.
* Earlier in this repo, a mutation harness derived its mutations from its own
  tests, so "13 of 13 caught" measured nothing. A refuter wrote 24 of its own
  and 17 escaped.

Every one of those was found by producing the damage on purpose. None would
have been found by reading the code.

### Where we deliberately differ

Science pre-registers to bind the AUTHOR before the data arrives. We
pre-register to bind the INSTRUMENT before it is trusted. And we add a rule the
scientific version has no need for: **scanning nothing is not a pass.** A check
that runs against an empty set must report RED, because "I found no problems"
and "I looked at nothing" are otherwise the same sentence.

## The intent

No check is trusted until it has been observed failing on the damage it claims
to detect. The artifact is not a passing suite. It is a RED run, named in the
completion table, that turned green when the fault was removed.

## The forms

| form | what it enforces | what it does not |
|---|---|---|
| skill | the read above, and the sentence written before code | nothing mechanical; it is a habit prompt |
| code | the break-test itself: produce the damage, assert RED, restore, assert GREEN | it cannot know whether the damage you chose is the damage that matters |

No hook form. A warning cannot substitute for a red test, and a hook that merely
reminds would be the fifth layer this repo already refused to add.

## Disproof — registered before the forms are built

**This gate is refuted if break-testing never catches a defect that ordinary
verification would have missed.** If, over a month of use, every fault found by
a deliberate break test would also have been found by reading the code or by
the normal test suite, then this gate is ceremony and should be deleted rather
than repaired.

Counter-evidence to date: four defects on 2026-08-31 alone, none of which
inspection had found — including two in gates written by the same author who
then declared them working.
