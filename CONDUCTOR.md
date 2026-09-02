# CONDUCTOR — the phase-aware gate runner

    role:   CANONICAL. The deployed copy is ~/.claude/skills/discipline/SKILL.md.
            Edit here, install outward, never the reverse (see CONTRACT.md).
    holds:  the gate table, the three legal states, the completion rule.
    holds NO gate reads. A gate's read lives in gates/NN-<name>/GATE.md.
    ruled:  the operator, 2026-08-31 — the 19-gate order below is approved. All 20 cards of the 2026-09-01 deck cast FULL; gate 03 price-the-loop retired into gate 02 as a lever, and the table renumbered.
            It splits .95 into gates 08 and 19. It splits the old gate 17 into 16 and 17.

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
| 03 | collapse-round-trips | DESIGN | a sequence of calls could have been one with foreknowledge you could have had. A foreseeable sequence is a MISS, not a pass | built |
| 04 | no-collision | DESIGN | you are about to touch SHARED substrate a peer may hold. Scratchpad and single-machine private work is N/A | built |
| 05 | substrate-search | DESIGN | you are proposing anything that SURVIVES THE SESSION — table, module, endpoint, daemon, layer, script | built |
| 06 | compile-it | DESIGN | you are deriving something for the SECOND time. Count derivations, not difficulty | built |
| 07 | think-3x | DESIGN | there is a real fork with a second option worth naming. No second option, no gate | built |
| 08 | **set-the-prior** | DESIGN | before building: state the user-outcome ONCE and a NUMERIC prior on it. No number, no FIRED | built |
| 09 | disprove-first | DESIGN | before code: name the observation that would REFUTE the design, and RUN it. Registered-but-unrun is BLOCKED | built |
| 10 | root-cause | VERIFY | something FAILED — ask how many distinct faults exist. Nothing failed is N/A | built |
| 11 | karsholto | VERIFY | the change adds substrate — count what a READER MUST HOLD, not what is on disk | built |
| 12 | completer | VERIFY | you are about to write "follow-up / deferred". Residue is legitimate ONLY when the blocker is outside your reach | built |
| 13 | nomess | VERIFY | orphans, dead links, stale gates, doc-vs-runtime drift — INCLUDING remote state: locks held, windows open, processes started | built |
| 14 | cold-read | VERIFY | you are shipping or retiring something another agent reads cold. Without a CONTEXT-FREE READER the row is BLOCKED, not FIRED | built |
| 15 | vizcheck | VERIFY | an interface YOU AUTHORED. Driving or reading someone else's surface is N/A | built |
| 16 | chunk-it | VERIFY | a named move was produced, OR something went wrong. A wrong conclusion is a chunk by definition | built |
| 17 | write-back | VERIFY | a fact was derived that would cost MORE THAN ONE CHEAP CALL to re-derive | built |
| 18 | adversarial-pass | VERIFY | **money, irreversibility, or anything outward-facing — a refuter runs or the work does not ship.** Everything else may block honestly | built |
| 19 | **state-the-posterior** | VERIFY | **LAST. Any claim of done · ready · verified · sure. One number PER CRITERION plus the gated floor** | built |

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

- **Gate 08 set-the-prior.** State the user-outcome ONCE and your prior BEFORE
  building. You cannot update a posterior you never set. A posterior with no
  prior is a first impression wearing a decimal.
- **Gate 19 state-the-posterior.** DEAD LAST, after the refuter. Give the number
  AND its evidence, gated by the WORST failure mode, never the best subsystem.

Gate 19 state-the-posterior is a **standing trigger**, not only a table row. It fires on any claim of
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
| **NOT FIRED** / **SKIPPED**, when the trigger DID fire | Not a state. Either run the gate, or write **BLOCKED** and say what is now UNVERIFIED. `18 adversarial-pass — NOT FIRED` should read `BLOCKED: no independent refuter ran; the claim is unverified by anyone but its author.` |

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
| 03 | collapse-round-trips | `gates/03-collapse-round-trips/GATE.md` · deployed `skills/collapse-round-trips` · hook + code `gates/06-compile-it/repeats.py` (shared with gate 06) |
| 04 | no-collision | `gates/04-no-collision/GATE.md` · deployed `skills/no-collision` · tool ADOPTED `gui-browser-lock` (SECOND MACHINE) · hook `hooks/warn_shared_path.py` |
| 05 | substrate-search | `gates/05-substrate-search/GATE.md` · deployed `skills/substrate-search` · code ADOPTED: the estate `commit-msg` guard (shared with gate 11) |
| 06 | compile-it | `gates/06-compile-it/GATE.md` · deployed `skills/compile-it` · code `gates/06-compile-it/repeats.py report` (shared with gate 03) |
| 07 | think-3x | `gates/07-think-3x/GATE.md` · deployed `skills/think-3x` |
| 08 | set-the-prior | `gates/08-set-the-prior/GATE.md` · deployed `skills/set-the-prior` · hook `hooks/hook_prior.py` |
| 09 | disprove-first | `gates/09-disprove-first/GATE.md` · deployed `skills/disprove-first` · code ADOPTED `lint/baits_pair.py` |
| 10 | root-cause | `gates/10-root-cause/GATE.md` · deployed `skills/root-cause` |
| 11 | karsholto | `gates/11-karsholto/GATE.md` · deployed `skills/karsholto` · code ADOPTED: the estate `commit-msg` YAGNI guard |
| 12 | completer | `gates/12-completer/GATE.md` · deployed `skills/completer` · hook `hooks/hook_completer.py` |
| 13 | nomess | `gates/13-nomess/GATE.md` · tool `gates/13-nomess/nomess.py` · code (in `lint/all.sh`) · deployed `skills/nomess` |
| 14 | cold-read | `gates/14-cold-read/GATE.md` · deployed `skills/cold-read` · agent `skills/agents/cold-reader.md` |
| 15 | vizcheck | `gates/15-vizcheck/GATE.md` · deployed `skills/vizcheck` · tool `coywolf-screenshot` (SECOND MACHINE ONLY) · agent `vizcheck-reader` |
| 16 | chunk-it | `gates/16-chunk-it/GATE.md` · code `gates/16-chunk-it/capture.py chunk`. No skill BY RULING: an obligation on every table, not a judgement |
| 17 | write-back | `gates/17-write-back/GATE.md` · code `capture.py writeback` (shared with gate 16, separate rows). No skill BY RULING |
| 18 | adversarial-pass | `gates/18-adversarial-pass/GATE.md` · deployed `skills/adversarial-pass` · agent `refuter` · code ADOPTED: the estate `pre-push` hook (opt-in via `.gate18-guarded`) · hook `hooks/mark_refuter.py` |
| 19 | state-the-posterior | `gates/19-state-the-posterior/GATE.md` · deployed `skills/95-percent-rule` — the posterior half · hook `hooks/hook_posterior.py` |

The `ask-dont-pour` bundle remains deployed on the primary workstation as the
read-source for gates 03-05 ONLY. It is deliberately NOT published in this repo:
it is the six-lever bundle those gates replaced, and no gate may bundle. Shipping
it would hand a reader the exact anti-pattern this suite forbids. The debt is a
GATE.md for 03, 04 and 05 — not a copy of the bundle.
It is the retired bundle. Do not run it as one gate.
`skills/95-percent-rule` is the read-source for BOTH gate 08 set-the-prior and
gate 19 state-the-posterior. It still describes them as one act; the split is the
ruling above, and each gate's own GATE.md is authoritative over it.

## The forms that make this fire

| form | file | does |
|---|---|---|
| PostToolUse hook | `hooks/mark_build.py` | flags a turn that CHANGED something. Includes Bash, because a day of estate work can run entirely through ssh. Scratch redirects (`/dev/null`, `/tmp`) are stripped, so read-only turns stay quiet |
| Stop hook | `hooks/owe_table.py` | states that the completion table is owed, once per turn |

## Known debt, recorded rather than hidden

- **Every gate has a `GATE.md`.** An earlier version of this block said "Gates
  03-20 have no GATE.md", that five gates had no deployed skill, and that "10
  has no read anywhere and is the highest-priority gap". Every one of those was
  false by the time it was read, and there is no gate 20. This block was never
  updated as the gates were built, so it described a repository that had stopped
  existing — which is worse than no debt list, because a reader trusts it.
- The real remaining debt: **11 gates carry code forms and 5 have a bait harness
  that RUNS.** Gate 09 disprove-first records this as its own REVISIT.
- `~/.claude/skills/` is still not a checkout of this repo, so installs are
  manual and drift can recur. The second machine holds exactly ONE deployed skill
  from this suite, plus five hooks of its own that are NOT part of it.
- Two seams were interrogated on 2026-08-31 and kept, but named for review:
  **05 substrate-search / 11 karsholto** are the same principle at two phases,
  the weakest distinction in the suite; **15 vizcheck** has the narrowest
  trigger and was N/A all day. Neither was merged. Two firing moments are two
  gates under "order is information". Forms describe HOW a gate is enforced,
  never WHEN it fires.
