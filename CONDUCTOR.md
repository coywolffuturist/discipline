# CONDUCTOR — the phase-aware gate runner

    role:   CANONICAL. The deployed copy is ~/.claude/skills/discipline/SKILL.md.
            Edit here, install outward, never the reverse (see CONTRACT.md).
    holds:  the gate table, the three legal states, the completion rule.
    holds NO gate reads. A gate's read lives in gates/NN-<name>/GATE.md.
    ruled:  the operator, 2026-08-31. He approved the 20-gate order below.
            It splits .95 into gates 09 and 20. It splits gate 17 into 17 and 18.

---

## Why this file exists

Until 2026-08-31 the conductor was a DERIVED ARTIFACT WITH NO SOURCE: a single
`SKILL.md` on one machine, unversioned, listing 15 gates in an order the
canonical repo had already superseded. It was loaded every session and recited
from memory, so its drift was invisible and looked like forgetfulness.

The cost was measured, not theorised. In one session the agent silently omitted
gates from completion tables, called `.95` by the wrong number, and ran the
six-lever `ask-dont-pour` bundle that gates 02-05 replaced. One table row read
"ask-dont-pour SKIPPED" while four other levers went unreported inside it.

## The outer loop is ka123n

Discipline governs HOW a step is executed. **ka123n decides WHICH step earns the
bits.** Every pass below sits inside one turn of that loop.

- **SELECT** — before any design work: is this step #1 by EV-per-byte? SELECT
  ends by SHOWING the window: three steps, ranked, priced. Each carries **why it
  is first**. That column proves a ranking happened rather than a list. A
  window he has not seen has not been selected; it has been assumed.
- **SLIDE** — after VERIFY and commit: re-rank. Never proceed by momentum into
  the old #2. Dropping SLIDE is how a session goes depth-first on a settled
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
| 09 | **set-the-prior** | DESIGN | before building: state the user-outcome ONCE and your prior on it | not yet |
| 10 | disprove-first | DESIGN | before code: name the observation that would REFUTE the design | not yet |
| 11 | root-cause | VERIFY | you are about to fix a symptom — ask how many distinct faults exist | not yet |
| 12 | karsholto | VERIFY | the change adds substrate or layers — smallest brick that proves the wall | not yet |
| 13 | completer | VERIFY | you are about to write "follow-up / next session / deferred", or claim done-with-residue | not yet |
| 14 | nomess | VERIFY | orphans, dead links, stale gates, doc-vs-runtime drift, missing smoke test | not yet |
| 15 | cold-read | VERIFY | you are shipping or retiring something another agent will read cold | not yet |
| 16 | vizcheck | VERIFY | a UI, CSS or layout change | not yet |
| 17 | chunk-it | VERIFY | a named move was produced — append it to the ledger NOW, not in a handoff | not yet |
| 18 | write-back | VERIFY | a reusable fact was derived — a number, endpoint, path, trap, ruling | not yet |
| 19 | adversarial-pass | VERIFY | before accepting any non-trivial claim, fix, or "done" | not yet |
| 20 | **state-the-posterior** | VERIFY | **LAST. Any claim of done · ready · verified · sure · it works** | not yet |

**Efficiency comes from TRIGGERS, not from running fewer gates.** Tiers were
tried and refuted: `cold-read` exists as a skill, an agent AND a hook at once,
and one scalar field cannot say that. A gate whose trigger did not fire is a
one-line **N/A citing that trigger** — cheap to write, and checkable against
this table by anyone. That is why the trigger column lives HERE: filling a
complete table must not require loading twenty skills.

Gates 02-05 replace the old six-lever `ask-dont-pour`. Lever 4 was DELETED as a
duplicate of chunk-it. Do not reinstate the bundle under any name.

## Why .95 sits at BOTH ends

`.95` used to be one gate, first in VERIFY. That let the number be quoted before
the gates that produce its evidence had run. On 2026-08-31 the signer's
enforcement was called 0.97. The refuter at gate 19 then found seven defects.
The repaired version was called sound. A second refuter broke six of the seven
fixes. Both numbers were stated before gate 19 ran.

It was a bundle of two acts at two moments, so it was split:

- **Gate 09 set-the-prior.** State the user-outcome ONCE and your prior BEFORE
  building. You cannot update a posterior you never set. A posterior with no
  prior is a first impression wearing a decimal.
- **Gate 20 state-the-posterior.** DEAD LAST, after the refuter. Give the number
  AND its evidence, gated by the WORST failure mode, never the best subsystem.

Gate 20 is a **standing trigger**, not only a table row. It fires on any claim of
done, ready, verified or sure. That includes a status report that asserts state.
It was dropped three times in one session AFTER a correction. A rule
recalled at the right moment fails; a rule compiled into a gate fires.

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
| 09 | set-the-prior | deployed `skills/95-percent-rule` — the prior half. NO GATE.md yet |
| 10 | disprove-first | **NO DEPLOYED READ — GAP.** Nearest kin: `skills/adversarial-pass`, its verify-time twin |
| 11-16 | root-cause · karsholto · completer · nomess · cold-read · vizcheck | deployed skills of the same name |
| 17 | chunk-it | **NO DEPLOYED SKILL.** Doctrine: `chunking-is-the-rsi-mechanism`; ledger `reference_coywolf_chunk_ledger.md` |
| 18 | write-back | **NO DEPLOYED SKILL.** Doctrine: `gifts-are-written-at-discovery` |
| 19 | adversarial-pass | deployed `skills/adversarial-pass` |
| 20 | state-the-posterior | deployed `skills/95-percent-rule` — the posterior half. NO GATE.md yet |

`skills/ask-dont-pour` remains deployed as the read-source for gates 03-05 ONLY.
It is the retired bundle. Do not run it as one gate.
`skills/95-percent-rule` is the read-source for BOTH 09 and 20 until each is
broken down. It still describes them as one act; the split is the ruling above.

## The forms that make this fire

| form | file | does |
|---|---|---|
| PostToolUse hook | `hooks/mark_build.py` | flags a turn that CHANGED something. Includes Bash, because a day of estate work can run entirely through ssh. Scratch redirects (`/dev/null`, `/tmp`) are stripped, so read-only turns stay quiet |
| Stop hook | `hooks/owe_table.py` | states that the completion table is owed, once per turn |

## Known debt, recorded rather than hidden

- Gates 03-20 have no `GATE.md`. They fire as reads; they have no automation.
- Gates 09, 10, 17, 18 and 20 have no dedicated deployed skill. 10 has no read
  anywhere and is the highest-priority gap.
- `~/.claude/skills/` is still not a checkout of this repo, so installs are
  manual and drift can recur. The second machine holds few deployed skills.
- Two seams were interrogated on 2026-08-31 and kept, but named for review:
  **06 substrate-search / 12 karsholto** are the same principle at two phases,
  the weakest distinction in the suite; **16 vizcheck** has the narrowest
  trigger and was N/A all day. Neither was merged. Two firing moments are two
  gates under "order is information". Forms describe HOW a gate is enforced,
  never WHEN it fires.
