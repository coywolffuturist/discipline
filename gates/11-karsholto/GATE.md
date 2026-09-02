# Gate 11 — karsholto

    order:  11. VERIFY, after root-cause and before completer. Count what the
            change added once the change exists.
    forms:  skill · code
    ruled:  the operator, 2026-09-01 — full moon. Count what a READER MUST HOLD,
            not what is on disk.
    where:  the code form is a git `commit-msg` hook on the primary workstation,
            registered by `core.hooksPath`. It is shared estate-wide, not owned
            by this repo — see ADOPTED below.

---

## The read

**Build the smallest brick that proves the wall, and make new substrate justify
itself.** No layer ahead of its evidence.

The unit is not files. Ruled 2026-09-01: **count what a reader must hold in their
head.** The expensive thing found that day was not file count — it was three
repositories holding one suite with a manual sync step between them. Two of the
three froze for three months and neither errored. By file count that was tidy;
by reader-load it was the worst structure in the estate.

## The intent

Keep the number of things a newcomer must understand as small as the work allows,
so the suite stays learnable as it grows.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: smallest brick, no layer ahead of its evidence, count reader-load | every build |
| **code** | ADOPTED — the estate's `commit-msg` YAGNI guard. New files in load-bearing dirs, or a new table, require a `Justified-against:` line in the commit body | every commit |

**ADOPTED, NOT BUILT, AND SHARED.** The ruled form said "code counts new
substrate in a changeset". That guard already existed estate-wide and had
already stopped a commit of mine that day; building a second would have been
this gate failing on itself.

It is shared with **gate 05 substrate-search**, which is its proper owner: the
guard's prompt asks gate 05's question verbatim — what existing piece already
does this, and why is it insufficient. This gate reads only the COUNT of new
substrate from it. Two gates, one mechanism, different readings. Not a bundle:
each reports its own row and neither can hide inside the other's.

**What adoption required.** The guard's load-bearing directory list named
`scripts/lucid/`, `neumann/router/`, `brain/skills/` and others — and **none of
this repo's directories.** Adding a new tool under `gates/` did not trigger it.
The gate whose subject is unjustified substrate was inert in the repo whose
subject is gates. `gates/`, `hooks/`, `lint/` and `scripts/` were added to that
list, and the guard was baited both ways: it now refuses a new file under
`gates/` without a justification and accepts it with one.

No hook beyond that, no tool, no agent: the judgement "is this brick the smallest
that proves the wall" is not decidable by a pattern, and a green check standing in
for it would be the ritual this suite forbids.

## Disproof

Refuted if a change adds substrate, passes this gate, and a later reader has to
hold materially more than the work required — the three-repos-one-suite shape,
arriving again.

Watchable, and it has fired: that shape existed on 2026-09-01 and was found by a
reader, not by this gate. The gate counts what a *commit* adds; it cannot see
structure that accumulates across repositories over months. **That is a known
blind spot, not a solved problem.**

**REVISIT** when something can measure reader-load across repositories rather
than per-commit. Until then the code form catches new primitives and the skill
form has to catch the rest.
