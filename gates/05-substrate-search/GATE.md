# Gate 05 — substrate-search

    order:  05. DESIGN, before anything is built. After it exists, the honest
            question is no longer "should this exist" but "how do we retire it".
    forms:  skill · code (adopted)
    ruled:  the operator, 2026-09-01 — full moon. Anything that SURVIVES THE
            SESSION is substrate. A scratchpad file is not.
    where:  the code form is the estate `commit-msg` hook on the primary
            workstation, registered by `core.hooksPath`. Shared with gate 11,
            which reads a different thing from it — see below.

---

## The read

**Before proposing anything new, answer in writing: what existing piece is
insufficient, and why?** Not "is there something similar" — name the piece, and
name the gap.

The trigger was ambiguous until it was ruled. Across one day this gate went N/A
**15 times in 38** — 39% — and the same artifact was ruled both ways on
consecutive days: a scratchpad script called N/A, then the same thing built
properly and called FIRED. The ruling settles it: **anything that survives the
session is substrate.** A scratchpad file is not — but writing one twice is
gate 06's trigger, so the two gates hand off rather than both going N/A.

The cost of skipping it is not a wasted afternoon. It is a second mechanism that
must now be kept in sync with the first, by hand, forever. That is how one suite
came to live in three repositories with a manual step between them, two of which
froze for three months without erroring.

## The intent

Reuse a validated piece, or state the gap that makes a new one necessary — so
every mechanism in the estate can answer why it exists.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: name the existing piece, name the gap, in writing before building | every proposal |
| **code** | ADOPTED — the estate `commit-msg` hook refuses a commit that adds a new file in a load-bearing directory, or a new table, without a `Justified-against:` line answering exactly this question | every commit |

**ADOPTED, NOT BUILT — and this gate is the guard's proper owner.** The ruled
form was "a hook on file creation demands the written justification". That hook
already existed, and its prompt is this gate's question verbatim: *what existing
piece already does this, and why is it insufficient for this case?*

The guard is shared with gate 11, which reads the **count** of new substrate from
it. Two gates, one mechanism, different readings — that is not a bundle, because
each gate reports its own row and neither can hide inside the other's.

**What adoption found.** The guard's question named four projects that are
archived or retired, so it asked about substrate that no longer exists. The
question now names the live estate. This is the same class as a gate file naming
a path without its host: a prompt whose referents have moved is worse than no
prompt, because it looks answered.

No hook beyond the commit-msg guard, no agent, no tool. Whether a gap is real is
a judgement about the estate, not a pattern; and the commit boundary is the last
honest moment to demand the answer, because after that the thing exists.

## Disproof

Refuted if new substrate lands with a `Justified-against:` line and a later
reader finds the named existing piece was in fact sufficient.

Directly watchable: every such commit carries its justification in the message,
so the claim and the substrate are in the same record and can be re-read together.

**One near-miss already, and it argues the gate works.** Building gate 11's code
form, this gate fired and found the guard already existed — a second one was not
built. Building gate 18's, it fired again and found the answer written in the
header of the file being replaced. Both times the existing piece was sufficient
and the search is what surfaced it.

**REVISIT** if the load-bearing directory list grows stale again — it named none
of this repo's directories until 2026-09-01, so the guard was inert in the repo
whose subject is gates.
