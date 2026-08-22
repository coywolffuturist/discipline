# Discipline — the canonical gate repository

> ## ⚠ REFUTED 2026-08-22 — DO NOT BUILD ON GATES 01 AND 02 YET
>
> An independent refuter broke both gates on nine points. the operator ordered this
> banner before any repair. The structure survived; the instruments did not.
>
> **Every measurement these gates produce is wrong toward green, and every
> warning they produce reaches nobody.**
>
> | # | failure | status |
> |---|---|---|
> | 1 | `lint_ste.py` prints GREEN and exits 0 on files it never scanned — the repo's own founding rule | OPEN |
> | 2 | Both hooks write their advisory to `permissionDecisionReason`, a permission field with no model reader. Proven live 3x: hook fired, model saw nothing | OPEN |
> | 3 | The passive metric is anti-correlated: 7/7 false positives ("open", "ten", "broken"), 9/10 false negatives | OPEN |
> | 4 | A bullet list without trailing periods scores as one 35-word sentence and goes RED. Add periods, same list goes GREEN | OPEN |
> | 5 | Blind to ambiguity — six unresolvable pronouns score perfect, and ambiguity is the failure the gate exists for | OPEN |
> | 6 | `door_report.py` inverts its own ratio; a hand-read containing "search_code" logs as a cheap door | OPEN |
> | 7 | Ladder numbers unreproducible: `corpus grep` measured 1,567 B not 400; corpus 5.4 MB not 4.3 MB | OPEN |
> | 8 | **The tombstone-graph door does not exist.** `SKILL.md` instructs agents to call a command that is not there | OPEN |
> | 9 | All five "wholly ours" claims broke, one self-refuting two paragraphs above itself | OPEN |
>
> **No tests ship with any script**, and **the completion table these gates name
> as their enforcement has never been built**. So the chain today is: a
> measurement nobody reads, feeding a table nobody writes.
>
> **The meta-finding, which is the one to keep:** the same reasoning that shipped
> these gates would certify them clean. This is the scar already on record — *an
> eval can report health it does not have* — reproduced by the repo written to
> prevent it.
>
> **What survived the attack:** forms-not-tiers, gate atomicity, and the
> declared-blind-spot discipline. Those could not be broken as ideas.
>
> Repair order, ruled by the operator: (1) empty-scan, (2) hook channel, (3) delete
> the passive metric, (4) re-measure the ladder with query and date recorded,
> (5) one red-path test per script.


    status: CANONICAL. Every gate lives here, one directory each.
    origin: the operator's ruling, 2026-08-22 — "make a new one that becomes
            canonical, structured on the breakdown you just did."

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
