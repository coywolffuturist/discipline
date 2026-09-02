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
> **CORRECTED 2026-09-01.** This banner used to read "Neither hook is registered
> anywhere. The completion table these gates name as their enforcement does not
> exist." That was true when written and is now false, and it stayed false long
> enough for a reader to conclude this repo buys reads rather than enforcement.
>
> All 9 hooks in `hooks/` ARE registered on the primary workstation, and the
> completion table fires unprompted, dozens of times a day.
>
> **They are NOT registered on the second machine.** Measured 2026-09-01, that
> machine holds ONE deployed skill (`the-screen`) and FIVE hooks of its own —
> `cold-read-check.py`, `howl.py`, `poison-screen.py`, `spend_reflex.py`,
> `tripwire.sh` — with six registrations. None of them is from this suite. An
> earlier version of this paragraph said that machine had "no hooks", which was
> false: it had five, and a reader would have concluded the suite was the only
> thing running there.
>
> This suite spans two machines and its claims resolve differently on each. Check
> which one you are reading from, and do not assume the other mirrors it.
>
> What remains honestly weak is below this banner, and it is about gates 01-02
> specifically, not about the conductor.

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

**No gate may bundle.** The operator's ruling, 2026-08-22, after `the triad` was
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

```
CONDUCTOR.md     the 19-gate conductor — which gate fires at which phase
CONTRACT.md      what is canonical here and what is derived from it
gates/NN-<name>/
    GATE.md      the read · the intent · the forms   (required)
    <form files> one per form the gate actually has
skills/          GENERATED deployed forms + the reviewer agents  (derived)
hooks/           the 9 hooks that make the table fire unprompted. 5 are symlinks
                 into their gate directory, so those cannot drift; 4 live only
                 here, because their gate has no other form file.
lint/            the gates' own checks — `lint/all.sh`
scripts/         standalone guards, usable without the rest
```

`gates/` is canonical and hand-reviewed. `skills/` is generated from the private
masters by `skill_share.sh` and is overwritten on every run — see
`skills/README.md`. Every gate in the table below is built: each has a reviewed
`GATE.md` source and its ruled forms. An earlier version of this paragraph said
most were "not yet" — it was written before the gates were built and never
updated, one screen above a table that said the opposite.

### If you only want the skills

Copy `skills/` into your agent's skills directory and `skills/agents/` into its
agents directory. They cross-reference each other, so take the whole bundle. The
conductor (`skills/discipline/`) is the entry point; everything else is a gate it
fires.

**What a clone can and cannot check.** `bash lint/all.sh` runs on any machine,
but two steps need private estate state — the firing corpus and the deployed
hooks' breadcrumb stream. Without them those steps print **SKIP**, loudly, and
the summary refuses to call the run a full pass. An earlier version of this line
said "nothing here calls home", which was false: a reviewer ran the build under
a fresh HOME and got three red checks for owning a different machine.

All 19 gates were ruled on 2026-09-01 by moon cast: 20 cards, 20 full moons, gate 03 price-the-loop retired into gate 02 as a lever and the table renumbered. All 19 have a GATE.md and their ruled forms.

This repository supersedes two earlier bundles that held the same suite — one
framed for coding, one renamed for knowledge work. Both are archived and remain
private, so there is nothing else to go and read; everything they held is here,
regenerated from current sources. Three surfaces holding one suite, with a manual
step between them, is exactly the drift this repo's CONTRACT exists to prevent.
Two of the three froze on the same day in June and neither errored.

## Status

| # | gate | forms | state |
|---|---|---|---|
| 01 | ste | skill · tool · hook · code | **built** |
| 02 | retrieval-economy | tool · skill | **built** (hook + code DELETED) |
| 03 | collapse-round-trips | skill · hook · code | **built** |
| 04 | no-collision | skill · tool · hook | **built** |
| 05 | substrate-search | skill · code | **built** (code adopted) |
| 06 | compile-it | skill · code | **built** |
| 07 | think-3x | skill | **built** |
| 08 | set-the-prior | skill · hook | **built** |
| 09 | disprove-first | skill · code | **built** |
| 10 | root-cause | skill | **built** |
| 11 | karsholto | skill · code | **built** (code adopted) |
| 12 | completer | skill · hook | **built** |
| 13 | nomess | skill · tool · code | **built** |
| 14 | cold-read | skill · agent | **built** |
| 15 | vizcheck | skill · tool · agent | **built** |
| 16 | chunk-it | code | **built** |
| 17 | write-back | code | **built** (shared tool) |
| 18 | adversarial-pass | skill · agent · hook | **built** |
| 19 | state-the-posterior | skill · hook | **built** |

The CONDUCTOR (`CONDUCTOR.md`) holds this table with each gate's TRIGGER, the
three legal states and the completion rule. It is installed to
`~/.claude/skills/discipline/SKILL.md`.

### The split that produced 08 and 19

`.95` was ONE gate, first in VERIFY. That let the number be quoted before the
gates producing its evidence had run. Measured on 2026-08-31: the signer's
enforcement was called 0.97, and the refuter at gate 19 then found seven
defects. The repaired version was called sound. A second refuter broke six of
the seven fixes. Both numbers were stated before gate 19 ran.

Two acts at two moments, so it was split. **Gate 08 set-the-prior** states the
outcome and the prior BEFORE building; you cannot update a posterior you never
set. **Gate 19 state-the-posterior** is DEAD LAST, after the refuter.

Approved 2026-08-31.

### The split that produced 16 and 17

`chunk-it + write-back` was the last surviving bundle. They are two acts with
two artifacts: the ledger entry and the memory page. On 2026-08-31 write-back
ran six times and chunk-it ran zero, while a single row would have read FIRED.

Approved 2026-08-31.

### The split that produced 02-05

The old `ask-dont-pour` skill held SIX levers under one name. The operator's
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
