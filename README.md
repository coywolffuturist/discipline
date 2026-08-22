# Discipline — the canonical gate repository

> ## REPAIRED 2026-08-22 — 5 of 9 findings closed, 4 open
>
> An independent refuter broke gates 01 and 02 on nine points. the operator ruled the
> repair order. **The banner stays until every row reads CLOSED.**
>
> | # | failure | status |
> |---|---|---|
> | 1 | `lint_ste.py` printed GREEN and exited 0 on files it never scanned — the repo's own founding rule | **CLOSED** · RED on zero scored, baited both ways |
> | 2 | Both hooks wrote their advisory to `permissionDecisionReason`, which is discarded on "allow". Proven live 3x: hook fired, model saw nothing | **CLOSED** · moved to `additionalContext`, confirmed and tested |
> | 3 | The passive metric was anti-correlated: 7/7 false positives, 9/10 false negatives | **CLOSED** · DELETED, not repaired |
> | 7 | Ladder numbers unreproducible | **CLOSED** · re-measured with query, date and host; ~3,400x survives |
> | 8 | The tombstone-graph door did not exist, and the skill told agents to call it | **CLOSED** · deleted everywhere, frontmatter included |
> | 4 | A bullet list without trailing periods scores as one long sentence and goes RED; add periods and it goes GREEN | **OPEN** |
> | 5 | Blind to ambiguity — six unresolvable pronouns score perfect, and ambiguity is the failure the gate exists for | **OPEN** |
> | 6 | `door_report.py` inverts its own ratio; a hand-read containing "search_code" logs as a cheap door | **OPEN** |
> | 9 | All five "wholly ours" claims broke, one self-refuting two paragraphs above itself | **OPEN** |
>
> **Also closed: no tests existed.** `test_gates.py` ships 17. On its first run
> it caught three crash paths this repair had missed.
>
> **Still true and still unbuilt:** the completion table these gates name as
> their enforcement does not exist, and neither hook is registered anywhere. So
> the chain today is a measurement nobody reads, feeding a table nobody writes.
>
> **The meta-finding, which is the one to keep:** the same reasoning that
> shipped these gates would have certified them clean. That is the scar already
> on record — *an eval can report health it does not have* — reproduced by the
> repo written to prevent it.

## What this repo is

A **gate** is one check that fires at one moment and produces one artifact.
This repo holds every gate we run, and for each one it answers three questions
in the same order every time:

| section | answers |
|---|---|
| **The read** | What is this thing? Where did it come from? How does the world use it, how do we use it differently, and what part is wholly ours? |
| **The intent** | What outcome are we trying to cause? |
| **The forms** | Does it exist as an agent, code, a hook, a skill, a tool — or more than one? |

The section names come from the rulings deck, which uses the same three beats.
That is deliberate: a gate is a course of action, and it earns its place the
same way a journey does.

## Why forms, not tiers

An earlier design sorted gates into four tiers and gave each gate one tier.
A refuter broke it in one move: `cold-read` exists as a skill, an agent AND a
hook at the same time, with different scope in each. One scalar field cannot
say that. Worse, choosing a tier would either hide the strongest enforcement
or claim a green result from a text match.

**So a gate has FORMS, plural.** Each form says what it enforces and what it
does not. A form that enforces nothing says so.

## Why gates are atomic

**No gate may bundle.** the operator's ruling, 2026-08-22, after `the triad` was
found to hold three separate checks under one name. A single table row then
reported the whole bundle as fired when only one of the three had produced any
evidence. The two silent checks were invisible **inside their own row**.

A bundled gate is a gate that can hide. This holds at every level here.

## Order is information

Gate directories are numbered. A language rule read at position 12 fires after
every prompt in the run has already been written badly. The number is part of
the design, not filing.

## The completion table

A discipline run is not finished until every gate has a row, and every row is
filled. Three legal states and no fourth:

- **FIRED** — name the ARTIFACT, never a checkmark. A checkmark cannot be
  falsified; a named artifact can be spot-checked against the transcript.
- **N/A** — legal ONLY by citing that gate's own written trigger.
- **BLOCKED** — the gate could not run. State what is now UNVERIFIED.

"Skipped because it seemed unnecessary" is not a state.

**A generated row is not automatically honest.** Four of seven gates tested on
2026-08-22 returned exit 0 while scanning nothing, including the estate's
secret scanner, which exits 0 by contract even when it is broken. So every gate
here must report **what it scanned**, and scanning nothing must be RED.

## Layout

    gates/NN-<name>/
        GATE.md      the read · the intent · the forms   (required)
        <form files> one per form the gate actually has

## Status

| # | gate | forms | state |
|---|---|---|---|
| 01 | ste | skill · tool · hook · code | **built** |
| 02 | retrieval-economy | tool · skill · hook · code | **built** |
| 03 | price-the-loop | — | approved, not broken down |
| 04 | collapse-round-trips | — | approved, not broken down |
| 05 | no-collision | — | approved, not broken down |
| 06 | substrate-search | — | not yet |
| 07 | compile-it | — | not yet |
| 08 | think-3x | — | not yet |
| 09 | disprove-first | — | not yet |
| 10 | the-95-percent-rule | — | not yet |
| 11 | root-cause | — | not yet |
| 12 | karsholto | — | not yet |
| 13 | completer | — | not yet |
| 14 | nomess | — | not yet |
| 15 | cold-read | — | not yet |
| 16 | vizcheck | — | not yet |
| 17 | chunk-it + write-back | — | not yet |
| 18 | adversarial-pass | — | not yet |

### The split that produced 02–05

The old `ask-dont-pour` skill held SIX levers under one name. the operator's
atomicity ruling forbids that, and the bundle had already hidden work: a
completion-table row reading "ask-dont-pour FAILED" carried evidence for lever
1 only, while four other levers went unreported inside the same row.

Levers 1 and 5 merged into gate 02 — lever 5 is lever 1 refined. Levers 2, 3
and 6 became gates 03, 04 and 05. **Lever 4 was DELETED**: it duplicated gate
17, chunk-it, under a second name.

Approved 2026-08-22.

Gates are broken down ONE AT A TIME, presented to the operator, and committed only
after he approves. That pace is deliberate: the previous architecture was
written in one pass and refuted on all five of its claims.
