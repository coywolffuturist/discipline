# Discipline — the canonical gate repository

> ## THREE REFUTATIONS. SCOPE CUT, NOT REPAIRED AGAIN. 2026-08-22
>
> Three independent refuters attacked these two gates. Each one found the
> previous repair incomplete, AND found the instrument built to verify it false.
>
> **What was DELETED rather than fixed:**
>
> | thing | why |
> |---|---|
> | the passive-voice metric | flagged 7/7 correct sentences, missed 9/10 real passives — anti-correlated |
> | the ambiguity signal | flagged 10/10 CLEAR sentences, missed 12/12 ambiguous ones — anti-correlated, and it had reached the verdict |
> | gate 02's hook + report | leaked a credential verbatim to a mode-0644 file; 12 of 25 commands misclassified, systematically; writer wrote `shape` while reader read `detail`, so every report printed "(no detail recorded)" |
> | `mutate_test.py` | its mutations were derived from its own tests, so "13 of 13 caught" measured nothing. A refuter wrote 24 of its own against the same green suite and **17 escaped** — including the 25-word limit itself |
>
> **The pattern, stated plainly.** Each layer certified the one below using the
> same reasoning that shipped it. A repo written to stop *an eval reporting
> health it does not have* produced a gate that did exactly that, then a test
> suite that did it again, then a mutation harness that did it a third time.
> **Adding a fifth layer would repeat it.** The scope was cut instead.
>
> **What survives, and it is small:** gate 01 scores sentence length. The
> splitter handles list markers, headings, closing marks, abbreviations and
> frontmatter. Unreadable files are RED. A code-only changeset is N/A, not a
> blocked commit. The hook advisory reaches `additionalContext`, a channel the
> model actually reads. 22 tests.
>
> **What is still KNOWN BROKEN and NOT fixed:**
>
> - Blockquoted lists (`> - item`) still flip verdict on punctuation. Finding 4
>   is NOT closed; only the plain-list marker was.
> - `lint_ste.py` reads the WORKTREE while a commit contains the INDEX, so
>   staging bad prose and then editing the file passes GREEN on bytes that were
>   never committed. No adversary required.
> - Extensions `.MD`, `.markdown`, `.mdx` are not matched, and the N/A message
>   claims "no markdown" when there was some.
> - An unreadable DIRECTORY reports N/A and exits 0. Our own rule calls that
>   BLOCKED.
> - The 25-word limit and both lint thresholds have NO test. They can be set to
>   100000 and the suite stays green.
>
> **Neither hook is registered anywhere. The completion table these gates name
> as their enforcement does not exist.** Nothing here is load-bearing, and the
> author does not claim it is.

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
