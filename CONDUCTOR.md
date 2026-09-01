# CONDUCTOR — the phase-aware gate runner

    role:   CANONICAL. The deployed copy is ~/.claude/skills/discipline/SKILL.md.
            Edit here, install outward, never the reverse (see CONTRACT.md).
    holds:  the gate table, the three legal states, the completion rule.
    holds NO gate reads. A gate's read lives in gates/NN-<name>/GATE.md.
    ruled:  the operator, 2026-08-31 — the 19-gate order below is approved. All 20 cards of the 2026-09-01 deck cast FULL; gate 03 price-the-loop retired into gate 02 as a lever, and the table renumbered.
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
| 01 | ste | DESIGN | you write a prompt, canon page, plan, note or agent message. NOT conversation with the operator — unless he asks for a concept, and then explain it fully | built |
| 02 | retrieval-economy | DESIGN | you are about to read a corpus, grep a repo, brief a subagent, or answer "what exists" — and, as its own lever, before firing a model in a LOOP, price it in CALLS | built |
| 03 | collapse-round-trips | DESIGN | a sequence of calls could have been one with foreknowledge you could have had. A foreseeable sequence is a MISS, not a pass | approved |
| 04 | no-collision | DESIGN | you are about to touch SHARED substrate a peer may hold. Scratchpad and single-machine private work is N/A | approved |
| 05 | substrate-search | DESIGN | you are proposing anything that SURVIVES THE SESSION — table, module, endpoint, daemon, layer, script | not yet |
| 06 | compile-it | DESIGN | you are deriving something for the SECOND time. Count derivations, not difficulty | not yet |
| 07 | think-3x | DESIGN | there is a real fork with a second option worth naming. No second option, no gate | not yet |
| 08 | **set-the-prior** | DESIGN | before building: state the user-outcome ONCE and a NUMERIC prior on it. No number, no FIRED | not yet |
| 09 | disprove-first | DESIGN | before code: name the observation that would REFUTE the design, and RUN it. Registered-but-unrun is BLOCKED | GATE.md, no form |
| 10 | root-cause | VERIFY | something FAILED — ask how many distinct faults exist. Nothing failed is N/A | not yet |
| 11 | karsholto | VERIFY | the change adds substrate — count what a READER MUST HOLD, not what is on disk | not yet |
| 12 | completer | VERIFY | you are about to write "follow-up / deferred". Residue is legitimate ONLY when the blocker is outside your reach | not yet |
| 13 | nomess | VERIFY | orphans, dead links, stale gates, doc-vs-runtime drift — INCLUDING remote state: locks held, windows open, processes started | not yet |
| 14 | cold-read | VERIFY | you are shipping or retiring something another agent reads cold. Without a CONTEXT-FREE READER the row is BLOCKED, not FIRED | not yet |
| 15 | vizcheck | VERIFY | an interface YOU AUTHORED. Driving or reading someone else's surface is N/A | not yet |
| 16 | chunk-it | VERIFY | a named move was produced, OR something went wrong. A wrong conclusion is a chunk by definition | not yet |
| 17 | write-back | VERIFY | a fact was derived that would cost MORE THAN ONE CHEAP CALL to re-derive | not yet |
| 18 | adversarial-pass | VERIFY | **money, irreversibility, or anything outward-facing — a refuter runs or the work does not ship.** Everything else may block honestly | not yet |
| 19 | **state-the-posterior** | VERIFY | **LAST. Any claim of done · ready · verified · sure. One number PER CRITERION plus the gated floor** | not yet |

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
omitting the row.** Silent omission is the failure this table exists to
stop: every gate appears in every table, or the table is incomplete.

### The illegal words, and what they should have been

Operator ruling, 2026-08-31: **fix the usage, not the canon.** On that day the
agent wrote PARTIAL, FAILED, NOT FIRED and SKIPPED into completion tables. None
is a state. Each is a softer vocabulary for the exact case the rule prevents —
a row that neither commits to evidence nor admits a gap.

| word used | what it must be instead |
|---|---|
| **PARTIAL** | **FIRED**, and the artifact names precisely what was and was not produced. The remainder belongs to gate 13 completer, never to a new state. |
| **FAILED** | **FIRED**, artifact: the failure. A gate that ran and caught you is the gate working. |
| **NOT FIRED** / **SKIPPED**, when the trigger DID fire | Not a state. Either run the gate, or write **BLOCKED** and say what is now UNVERIFIED. `19 adversarial-pass — NOT FIRED` should read `BLOCKED: no independent refuter ran; the claim is unverified by anyone but its author.` |

PARTIAL is the most dangerous of the four, because it is where a BLOCKED gate
goes to hide. A blocked gate is a live risk. "Partial" sounds like progress.

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
| 02 | retrieval-economy | `gates/02-retrieval-economy/GATE.md` · deployed `skills/retrieval-economy`. Also carries the price-the-loop lever, folded in 2026-09-01 |
| 03 | collapse-round-trips | **READ NOT SHIPPED.** Lever 3 of the retired six-lever `ask-dont-pour` bundle, which this repo does not publish: it is the bundle these gates replaced, and no gate may bundle. Owed: its own GATE.md. |
| 04 | no-collision | **READ NOT SHIPPED.** Lever 6 of the same retired bundle. Owed: its own GATE.md. |
| 05 | substrate-search | deployed `skills/substrate-search` |
| 06 | compile-it | deployed `skills/compile-it` |
| 07 | think-3x | deployed `skills/think-3x` |
| 08 | set-the-prior | deployed `skills/95-percent-rule` — the prior half. NO GATE.md yet |
| 09 | disprove-first | `gates/09-disprove-first/GATE.md` · **NO DEPLOYED READ — GAP.** Nearest kin: `skills/adversarial-pass`, its verify-time twin |
| 10 | root-cause | deployed `skills/root-cause` |
| 11 | karsholto | deployed `skills/karsholto` |
| 12 | completer | deployed `skills/completer` |
| 13 | nomess | deployed `skills/nomess` |
| 14 | cold-read | deployed `skills/cold-read` |
| 15 | vizcheck | deployed `skills/vizcheck` |
| 16 | chunk-it | **NO DEPLOYED SKILL, BY RULING.** It folds into the completion rule: an obligation on every table, not a judgement. Ruled 2026-09-01. |
| 17 | write-back | **NO DEPLOYED SKILL, BY RULING.** Same — an obligation, not a judgement. Ruled 2026-09-01. |
| 18 | adversarial-pass | deployed `skills/adversarial-pass` |
| 19 | state-the-posterior | deployed `skills/95-percent-rule` — the posterior half. NO GATE.md yet |

The `ask-dont-pour` bundle remains deployed on the primary workstation as the
read-source for gates 03-05 ONLY. It is deliberately NOT published in this repo:
it is the six-lever bundle those gates replaced, and no gate may bundle. Shipping
it would hand a reader the exact anti-pattern this suite forbids. The debt is a
GATE.md for 03, 04 and 05 — not a copy of the bundle.
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
  manual and drift can recur. The second machine holds exactly ONE deployed skill.
- Two seams were interrogated on 2026-08-31 and kept, but named for review:
  **06 substrate-search / 12 karsholto** are the same principle at two phases,
  the weakest distinction in the suite; **16 vizcheck** has the narrowest
  trigger and was N/A all day. Neither was merged. Two firing moments are two
  gates under "order is information". Forms describe HOW a gate is enforced,
  never WHEN it fires.
