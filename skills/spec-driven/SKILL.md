---
name: spec-driven
description: "Spec-driven development for agentic work: discover what exists, draft the spec as code, refute it before the human sees it, grill only the consequential rulings, audit anchors to past decisions, refute again, then build ONLY from the spec — every build step names a section and a test. Depth scales with stakes (5 lines for a task, the full loop for a system). Trigger: 'spec this', 'write a spec', 'no more patchwork', a multi-part build, or any plan other agents will build from."
---

# spec-driven — spec the destination, navigate by instruments

**Core (2026-06-15 canon, `feedback_private_rule_06`):** don't choose between spec-driven and
verify-driven — sequence them. Ground truth unknown → VERIFY first; a spec over a misunderstood
reality executes the wrong work faithfully. Work understood → SPEC it: goal, acceptance checks,
non-goals, before building. Spec the intent; verify the execution.

**Proven on 2026-09-22** building `SPEC-one-coywolf`: two refuter passes found 40+ defects the author
could not see; the anchor audit overturned 6 past rulings and 6 invariants for the better.

## Step 0 — pick the depth (gate 00)

| stakes | depth |
|---|---|
| a task, reversible, one sitting | **5-line spec:** goal · acceptance checks (runnable) · non-goals. Steps 1, 2, 8 only. |
| a feature or subsystem | steps 1–8, one refuter pass, rulings batched |
| a whole system, money, security, privacy, one-way doors | the full loop, two refuter passes, consequential rulings one at a time |

Heavy process on light work kills momentum. Name the depth before starting.

## The loop

1. **Discover.** Ask the mind first (existing specs, rulings, canon). Then read-only evidence sweeps of
   what actually runs, in parallel agents: DECIDED · LIVE (with the proving command) · SPECIFIED BUT
   UNBUILT · CONFLICTS · OPEN QUESTIONS. The new spec ABSORBS existing specs; it never sits beside them.
2. **Draft the spec as code** (template below). Every gap gets a runnable test. Every "today" line is a
   dated measurement. Tests are list items starting with their ID so `spec_lint` can read them.
3. **Refute before the human sees it.** A `refuter` checks facts against the machines; a `cold-reader`
   checks what a context-free agent would misread. Fix everything. Then run
   `~/.claude/scripts/spec_lint.py check SPEC.md` until clean.
4. **Publish a readable document GENERATED from the file.** The file is the source of truth; the document
   carries the same status and says so. Never a second hand-edited copy.
5. **Rule.** Every decision row: question · recommendation · cost · default if unruled · ruling (dated).
   - **Batch the low-stakes, reversible rulings:** "accept all of these, or pull any out."
   - **One at a time** for money, security, privacy, outward-facing and one-way doors. One question per
     turn, recommendation first.
6. **Audit the anchors — Molt (I11).** Also fires mid-build: before repairing existing substrate, run gate 05's Molt read. For every recommendation and invariant ask: would I recommend this if the
   past ruling did not exist? If not, surface it with the better option, mark the departure, and ask.
   Invariants are included — they go stale too.
7. **Refute again, then approve.** A consistency pass: stale text left behind by rulings, rulings that land
   in no phase, tests that cannot fail, invariants the rulings now break. `spec_lint` clean. The human
   re-reads and approves. Commit once to its home; mark every superseded document.
7b. **Put it on the progress dashboard — required, part of approval (his rule 2026-09-27: "Anything that has been
   spec'd out needs to have a dashboard configured like this").** The spec lives at `coywolf-mind/SPEC-<name>.md` on the
   den with `status: APPROVED ...`; `scripts/health/spec_progress.py` DISCOVERS it and the spec progress dashboard
   shows it (tests per phase, READY/BLOCKED, open rulings, a line over time until completion). Its results come from a
   live runner (add it to `LIVE` in spec_progress.py) or from `coywolf-mind/checks/<name>_status.json` (recorded, each
   result citing its evidence; a test nobody measured is UNMEASURED, never PASS). The spec is not approved until you
   have run spec_progress.py and SEEN it on the page. Every later measurement updates the runner or the status file.
8. **Build only from the spec.** `spec_lint.py window SPEC.md` lists phases whose rulings exist (READY)
   and what blocks the rest. Every ka123n row names a spec section and its test. Repairs outside the spec
   rank behind it. A phase ends only when its tests pass.

## Four rules for agentic speed

1. **The tests are the spec; prose is the view.** Acceptance tests live as runnable code; a section's
   status should be derived from their results, not typed.
2. **Rulings are data.** Structured rows (question · options · default · choice · date) that agents and
   the linter can query — never buried in prose.
3. **Depth proportional to stakes** (step 0).
4. **The human is the bottleneck, not the build.** Batch what is safe; spend their attention only where a
   wrong call is costly.

## Template

```
---
name: SPEC-<name>
status: DRAFT vN — NOT IN FORCE until approved
as_of: YYYY-MM-DD
location: where the source of truth lives, and where it goes on approval
---
# <name> (DRAFT vN)
Why this exists · how to read it
## 1. The shape
## 2. Invariants            | # | invariant | source |
## 3. The parts             per part: Target · Today (dated) · Gaps · Tests (- FAM-T1 ...)
## 4. Rulings               | # | question | recommendation | cost | default | ruling |
## 4b. OPEN                 | OPEN-n | question | recommendation |
## 5. Build order           | Pn name | delivers | done when (test IDs) | needs (ruling IDs) |
## 6. Tests that could prove the design wrong
## 7. What this replaces    (on approval only)
## 8. Contract              source of truth · derived views · writer
## 9. Glossary              every code family, including FAM- for each test family
```

## Tools and agents it uses

- The progress dashboard: the spec progress dashboard fed by `scripts/health/spec_progress.py` (coywolf repo,
  daily at 05:45 on the den) through the hourly health feed. Step 7b.

- `~/.claude/scripts/spec_lint.py check|window` — the mechanical checks and the derived window
  (source: discipline repo `scripts/spec_lint.py`, baited by `lint/bait_spec_lint.py`).
- Agents: evidence sweeps (`general-purpose`, read-only), `refuter`, `cold-reader`.
- Skills: `grill-me` (one question per turn), `ka123n` (the window), `discipline` (gates 00, 05, 07, 08,
  09, 14, 18, 19 fire inside this loop).
