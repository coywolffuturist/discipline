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

**ADOPTED, NOT BUILT — and this gate is the guard's proper owner.** The ruled form asked for a hook on file creation that demands the written
justification. (Described, not quoted: the ruling text lives in the cast record
on another machine and cannot be verified from this repo, so presenting it as a
verbatim quotation would be a citation no reader here can check.) That hook
already existed, and its prompt is this gate's question verbatim: *What existing
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

## Molt — the mirror, before a REPAIR

    ruled:  the operator, 2026-09-23: the standing rule "if there is a current best practice that should
            replace a previous approach, raise it" gets a name and fires as part of this gate. Source rule:
            past rulings and architectures are inputs, not fences.

The gate above stops a NEW piece when an old one suffices. Molt stops the opposite waste: **mending an old piece
when current practice would replace it.** A coywolf sheds its coat when a better one has grown in; before you
mend the old coat, ask whether it is time to shed it.

**Fires when** you are about to repair, harden or extend substrate that already exists — above all when a
refuter, an audit or a failure hands you a defect in it. A defect is the moment the old approach is under the
lamp; patching it at the level it arrived is how a keyword tripwire got four fixes in one day (2026-09-23) while
the real answer — a policy-enforcing signer, a sandbox — was never raised.

**The read, in writing, before the patch:**
1. **Name the approach** being repaired and when it was chosen (and by whom: his ruling, or an agent's choice).
2. **Find the current best practice** for that job: the mind first (`mind_grep`, `mind_check`), then a web check.
3. **If the new approach is better,** stop patching. Bring it to the operator as a departure: old vs new, cost, what it
   retires, a recommendation — one question per turn. Patch only what is needed to stay safe meanwhile.
4. **Else** patch, and write one line of why the old approach still wins.

**Record.** A departure raised is recorded where the operator rules on it: an OPEN row (or a ruling) in the spec it
changes, tagged `Molt`. The weekly gate audit (A4) counts them — no separate log.

**States.** FIRED names the approach and the verdict ("Molt: home-grown spend window -> policy signer, raised
as OPEN-8"). N/A only when nothing existing is being repaired.

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
