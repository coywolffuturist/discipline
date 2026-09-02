# Gate 01 — ASD-STE100

    order:  1. FIRST, and the position is load-bearing. A language rule read at
            position 12 fires after every prompt in the run is already written.
    forms:  skill · tool · hook · code
    ruled:  the operator, 2026-08-22 — "warn + score in completion table".

---

## The read

### What it is

**ASD-STE100, Simplified Technical English.** A controlled subset of English:
a restricted vocabulary of roughly 900 approved words, each allowed in ONE
meaning and ONE part of speech, plus about 60 writing rules. The best known:
short sentences, one instruction per sentence, active voice, no ambiguous
pronouns, and no omitted articles.

### Where it came from

It was built for **aircraft maintenance manuals**, not for style. In 1986 the
European Association of Aerospace Industries (AECMA) produced it at the request
of European airlines. The problem was concrete and safety-critical: mechanics
working in English as a second language were misreading procedures, and a
misread procedure on an aircraft is not a typo. It is now maintained as
ASD-STE100 by the ASD Simplified Technical English Maintenance Group.

The founding insight is the one we are borrowing: **the writer is not present
when the text is read.** A mechanic in a hangar at 3 a.m. cannot ask the author
what a sentence meant. So ambiguity is not a cost to be traded off. It is a
defect.

### How the world uses it

Aerospace, defence, and heavy industry, for procedural documentation. It is a
compliance standard in those industries — often contractual — and it is applied
almost entirely to **manuals read by humans**. Tooling exists commercially
(vocabulary checkers, term databases). Outside those industries it is largely
unknown.

### How we use it — the part that is cutting-edge

We apply it to **agent-to-agent communication and to canon that outlives its
author.** That is not its documented use, and it is the part worth naming.

The structural argument transfers exactly. An agent given a prompt cannot
cheaply ask what I meant; a clarifying round trip costs a full turn and often
does not happen at all. A canon page is read months later by an agent with
none of my context. Both are the mechanic in the hangar.

The evidence is local and recent. On 2026-08-22 I wrote seven long, nested
agent prompts. Two agents misread their scope, and one stopped at partial
repair and reported success. The failure mode STE was invented to prevent —
a reader acting confidently on a misread instruction — reproduced exactly, in
a domain the standard has never been applied to.

### What is ours — corrected 2026-08-22, after a refuter broke every claim here

The first version of this section made two novelty claims. **Both were wrong,
and the correction is kept rather than quietly replaced.**

- *"The industry checks finished manuals; we check the instruction while it can
  still be rewritten."* **False.** Commercial STE tooling runs inside the
  authoring editor as the writer types. Shift-left checking is the ordinary
  shape of every linter that exists.
- *"Score-in-the-table instead of block."* **Not novel.** That is warn-only CI
  plus a required checklist — coverage gates and quality gates already work
  this way.

**What we can actually evidence:** we apply a documentation standard to
**agent-to-agent prompts**, which is not its documented use, and the transfer
argument holds — an agent cannot cheaply ask what a prompt meant.

**We have NOT verified that this application is novel.** No web access was
available to check. Treat it as unusual-to-us, not as new-to-the-world. That
sentence is the honest version, and it is falsifiable by anyone with a search
engine.

**The local evidence is real regardless of novelty.** Seven long prompts on
2026-08-22, two agents misreading scope, one reporting success on partial work.
That happened here and is measurable here.

### Where we deliberately differ from the standard

We do **not** adopt the 900-word approved vocabulary. Aerospace can restrict
its terms because its domain is fixed. Ours is not, and the operator's own exception
governs: *use the exact technical term where precision needs it, and never
trade accuracy for simplicity.* A controlled vocabulary would fight that.

So we take the **structural** rules — sentence length, one idea per sentence,
active voice, no stacked clauses — and reject the lexical ones.

---

## The intent

Make writing legible where ambiguity cannot be repaired cheaply.

Two audiences, both of them unable to ask a follow-up question at low cost:

- **Myself, later.** Canon pages, plans, working notes.
- **Other agents.** Subagent prompts, agent-to-agent messages.

The operator is explicitly NOT the primary audience of this gate. His ruling,
2026-08-22: STE is how I write to myself and to other agents. Reports to him
inherit the clarity, but the gate is aimed at the machine-facing surface,
because that is where a misreading goes uncorrected.

**The intent is NOT simplicity.** It is unambiguity. Where those conflict,
precision wins and the exact term stays.

---

## The forms

| form | artifact | what it enforces |
|---|---|---|
| **skill** | `SKILL.md` | Nothing. It is the standard and the judgment cases — *is this term necessary?* is reasoning, and reasoning belongs in context. |
| **tool** | `ste.py` | Nothing. It MEASURES: words per sentence, longest sentence, clause depth. **Not passive voice** — that metric was DELETED 2026-08-22, not repaired, and `test_gates.py` asserts it stays gone. Zero model calls. Callable by me and by any agent. |
| **hook** | `hook_prompt.py` | Warns at PreToolUse on the Agent tool, before a subagent spawns. **Never blocks** — the operator's ruling. A blocker that refuses a 26-word sentence is the ritual the suite forbids. |
| **code** | `lint_ste.py` | Exits non-zero on canon pages and agent definitions at commit time. Canon outlives the session; a page written badly is read wrong for months. |

**Not an agent.** A checker agent spends a model call on arithmetic. The
judgment cases are rare enough that the skill covers them.

### Why four forms and not one

The skill form alone was tried and failed. The rule sat in context on
2026-08-22 while seven bad prompts were written. Worse, the second machine holds exactly
ONE installed skill, so a skill-only gate does not deploy to the machine where
most work runs. A gate that is not installed cannot fire, and that is a
deployment failure, not a discipline failure.

---

## Disproof — registered before the forms were built

This gate is refuted if, after the hook is live, agent prompts stay long. That
would mean the advisory form is theatre, and it must then either become
blocking or be removed. **A warning nobody acts on is worse than no warning,
because it reports a safety that is not there.**

Measure: median words-per-sentence and longest-sentence length across agent
prompts, before and after. If the numbers do not move, the form failed.
