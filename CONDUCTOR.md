# CONDUCTOR — the phase-aware gate runner

    role:   CANONICAL. The deployed copy is ~/.claude/skills/discipline/SKILL.md.
            Edit here, install outward, never the reverse (see CONTRACT.md).
    holds:  the gate table, the three legal states, the completion rule.
    holds NO gate reads. A gate's read lives in gates/NN-<name>/GATE.md.

---

## Why this file exists

Until 2026-08-31 the conductor was a DERIVED ARTIFACT WITH NO SOURCE: a single
`SKILL.md` on one machine, unversioned, listing 15 gates in an order the
canonical repo had already superseded with 18. It was loaded every session and
recited from memory, so its drift was invisible.

The cost was measured, not theorised. In one session the agent silently omitted
gates 10, 13 and 16 from completion tables, called `.95` "gate 7", and ran the
six-lever `ask-dont-pour` bundle that gates 02-05 replaced. One table row read
"ask-dont-pour SKIPPED" while four other levers went unreported inside it.

## The outer loop is ka123n

Discipline governs HOW a step is executed. **ka123n decides WHICH step earns the
bits.** Every pass below sits inside one turn of that loop.

- **SELECT** — before any design work: is this step #1 by EV-per-byte? SELECT
  ends by SHOWING the window: three steps, ranked, priced, each with **why it is
  first** — the column that proves a ranking happened rather than a list. A
  window he has not seen has not been selected; it has been assumed.
- **SLIDE** — after VERIFY and commit: re-rank. Never proceed by momentum into
  the old #2. Dropping SLIDE is how a session becomes depth-first on a settled
  question while a live one waits.

## The gates

DESIGN gates fire before building. VERIFY gates fire before claiming done.
A gate that is "not yet broken down" STILL FIRES as a read — the missing
artifact is its automation, not its authority.

| # | gate | phase | fires when | state |
|---|---|---|---|---|
| 01 | ste | DESIGN | you write a prompt, canon page, plan or note | built |
| 02 | retrieval-economy | DESIGN | you are about to read a corpus, grep a repo, brief a subagent, or answer "what exists" | built |
| 03 | price-the-loop | DESIGN | you are about to fire a model in a LOOP — price it in CALLS first | approved |
| 04 | collapse-round-trips | DESIGN | several independent calls or reads could be one | approved |
| 05 | no-collision | DESIGN | you are about to touch substrate a peer may hold | approved |
| 06 | substrate-search | DESIGN | you are proposing NEW substrate — table, module, endpoint, daemon, layer | not yet |
| 07 | compile-it | DESIGN | an LLM step repeats, is mechanical, stable and checkable — write code instead | not yet |
| 08 | think-3x | DESIGN | you are building anything non-trivial | not yet |
| 09 | disprove-first | DESIGN | before code: name the observation that would REFUTE the design | not yet |
| 10 | **the-95-percent-rule** | VERIFY | **ANY claim of done · ready · verified · sure · it works** | not yet |
| 11 | root-cause | VERIFY | you are about to fix a symptom — ask how many distinct faults exist | not yet |
| 12 | karsholto | VERIFY | the change adds substrate or layers — smallest brick that proves the wall | not yet |
| 13 | completer | VERIFY | you are about to write "follow-up / next session / deferred", or claim done-with-residue | not yet |
| 14 | nomess | VERIFY | orphans, dead links, stale gates, doc-vs-runtime drift, missing smoke test | not yet |
| 15 | cold-read | VERIFY | you are shipping or retiring something another agent will read cold | not yet |
| 16 | vizcheck | VERIFY | a UI, CSS or layout change | not yet |
| 17 | chunk-it + write-back | VERIFY | a named move was produced, or a reusable fact derived | not yet — STILL A BUNDLE |
| 18 | adversarial-pass | VERIFY | before accepting any non-trivial claim, fix, or "done" | not yet |

**Efficiency comes from TRIGGERS, not from running fewer gates.** Tiers were
tried and refuted: `cold-read` exists as a skill, an agent AND a hook at once,
and one scalar field cannot say that. A gate whose trigger did not fire is a
one-line **N/A citing that trigger** — cheap to write, and checkable against
this table by anyone. That is why the trigger column lives HERE: filling a
complete table must not require loading eighteen skills.

Gates 02-05 replace the old six-lever `ask-dont-pour`. Lever 4 was DELETED as a
duplicate of gate 17. Do not reinstate the bundle under any name.

**Gate 17 is the last surviving bundle.** `chunk-it` (append the named move to
the ledger) and `write-back` (write the derived fact to memory) are two acts
with two artifacts. On 2026-08-31 write-back ran six times and chunk-it did not
run at all, while a single row would have read FIRED. Splitting it needs a
ruling, because it renumbers 18.

## Gate 10 is a TRIGGER, not a row

`.95` does not wait for a completion table. It fires on every claim of
**done · ready · verified · sure · it works**, including inside a status report
that asserts state. State the posterior AND the evidence, and gate it by the
WORST failure mode, not the best subsystem.

It was dropped three times in one session AFTER being corrected once. A rule
recalled at the right moment fails; a rule compiled into a gate fires. Until
gate 10 has a firing form, treat every "done" as owing a number.

## Three legal states. There is no fourth.

- **FIRED** — name the ARTIFACT, never a checkmark. A checkmark cannot be
  falsified; a named artifact sits above the table and is spot-checkable.
- **N/A** — legal ONLY by citing the gate's own written trigger.
- **BLOCKED** — could not run. State what is UNVERIFIED as a result. A blocked
  gate is a live risk, not a closed row.

**"Skipped because it seemed unnecessary" is not a state, and neither is
omitting the row.** Silent omission is the failure this table exists to stop:
every gate appears in every table, or the table is incomplete.

## Completion

A discipline run is not finished until every row is filled. The value is not
the record. It is the moment of filling it, when a gap that felt like nothing
becomes a blank you cannot leave.

## Where each gate's read currently lives

The conductor holds no reads. Until a gate is broken down into
`gates/NN-<name>/GATE.md`, its read lives in a deployed skill. This table exists
so no gate is unreachable — an unreachable gate is a gate that will be skipped.

| # | gate | read lives in |
|---|---|---|
| 01 | ste | `gates/01-ste/GATE.md` · deployed `skills/ste` |
| 02 | retrieval-economy | `gates/02-retrieval-economy/GATE.md` · deployed `skills/retrieval-economy` |
| 03 | price-the-loop | inside deployed `skills/ask-dont-pour` (lever 2) |
| 04 | collapse-round-trips | inside deployed `skills/ask-dont-pour` (lever 3) |
| 05 | no-collision | inside deployed `skills/ask-dont-pour` (lever 6) |
| 06-08 | substrate-search · compile-it · think-3x | deployed skills of the same name |
| 09 | disprove-first | **NO DEPLOYED READ — GAP.** Its read existed only in the conductor monolith, which had no source. Nearest kin: `skills/adversarial-pass` (its verify-time twin). |
| 10-16 | 95-percent-rule · root-cause · karsholto · completer · nomess · cold-read · vizcheck | deployed skills of the same name |
| 17 | chunk-it + write-back | **NO DEPLOYED SKILL.** Doctrine in memory: `chunking-is-the-rsi-mechanism`; ledger at `reference_coywolf_chunk_ledger.md`. |
| 18 | adversarial-pass | deployed `skills/adversarial-pass` |

`skills/ask-dont-pour` remains deployed as the read-source for gates 03-05 ONLY.
It is the retired bundle. Do not run it as one gate.

## Known debt, recorded rather than hidden

- Gates 03-18 have no `GATE.md`. They fire as reads; they have no automation.
- Gate 09 has no read anywhere. Highest-priority gap in this table.
- Gate 17 is still a bundle; splitting it renumbers 18 and needs a ruling.
- `~/.claude/skills/` is still not a checkout of the discipline repo, so this
  install was manual and drift can recur. The second machine holds one deployed skill.
