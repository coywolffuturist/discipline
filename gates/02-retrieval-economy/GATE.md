# Gate 02 — retrieval-economy

    order:  2. Immediately after the language gate, and BEFORE ka123n SELECT.
            You cannot rank work you have not cheaply established.
    forms:  tool · skill · hook · code
    ruled:  the operator, 2026-08-22 — approved the four-way split of the old
            `ask-dont-pour` bundle, and the renumbering below it.

---

## The read

### What it is

Take the cheapest retrieval door that ACTUALLY ANSWERS the question. Ask an
index; do not read a corpus.

### Where it came from

This is **query planning**, borrowed from databases. A planner chooses between
an index seek and a full table scan by estimated cost, never by preference.
Reading everything is always available, and it is almost always wrong.

The same shape appears in **cache hierarchies**. You take the fastest tier that
holds the answer, and you fall through only on a miss.

### How the world uses it

Query planners, CPU and CDN caches, and lately retrieval-augmented generation.
In agent work the popular form is thin: *"use RAG instead of stuffing the
context window."* That framing has ONE door and ONE tier.

### How we use it — the cutting-edge part

We measured our own ladder, in bytes and in model calls, on the same question:

| door | bytes | model calls | seconds |
|---|---|---|---|
| tombstone graph | 9 | 0 | 0.04 |
| `corpus grep` (FTS5) | 400 | 0 | 0.04 |
| `corpus check` | 595 | 0 | 0.08 |
| SQL over the ledger | 761 | 0 | 0.00 |
| `corpus rulings` | 1,127 | 0 | 0.00 |
| `corpus consult` | ~3,500 | **1 Opus** | 10–20 |
| reading the corpus | 4,326,756 | 0 | — |

Five orders of magnitude separate the top rung from the bottom.

### What is wholly ours

Three findings, none of them standard practice:

1. **The smart door is the MOST expensive, not the first.** `corpus consult` runs
   the full retrieval stack with a rerank, and it spends an Opus call. Reaching
   for it when a deterministic door would answer IS the waste. Popular RAG
   framing cannot express this, because it has only one door.
2. **Zero hits is decision-grade.** A lexical index can say "no page contains
   this word." A vector index structurally cannot — it always returns its top
   *k*. We treat an empty lexical result as a real answer and write it down.
3. **Code is a graph, not a corpus.** `codebase-memory` answers structural
   questions for roughly 1% of the tokens that reading the files costs.

### The evidence that this gate is needed

On 2026-08-22 the author read repositories with `grep`, `sed` and `cat` for a
full session, then called the code door once. It immediately found substrate
that the hand-reading had missed: an entire hook chain, a three-layer defence
design, and a trust architecture with six closed threats. The proposal written
without it was refuted on all five of its claims, two of them because it
described the system from a stale document instead of querying the machine.

---

## The intent

Know what information costs before you spend it. Never spend a judgment call on
a lookup.

**The intent is NOT to read less.** The most expensive single act on 2026-08-22
was an independent refuter at 143k tokens, and it was correct spending — it
found five defects in the author's own audit.

Spend freely on adversarial review and on deriving what is not yet known.
Spend nothing on re-reading, re-deriving, and re-confirming.

---

## The forms

| form | artifact | what it enforces |
|---|---|---|
| **tool** | the doors themselves — `mind` CLI, `mind_*` MCP, `codebase-memory` MCP | Nothing. They ARE the rungs. Already built; this gate does not rebuild them. |
| **skill** | `SKILL.md` | Nothing. Choosing a door is judgment. |
| **hook** | `hook_corpus_read.py` — PreToolUse on Bash | **Warns, never blocks.** Names the cheaper door when a command reads a known corpus by hand. |
| **code** | `door_report.py` | Nothing. It MEASURES the session ratio for the completion table. |

**Not an agent.** Choosing a door is an inline decision. Delegating it costs
more than the door.

### A blind spot this gate declares rather than hides

The hook sees **Bash only**. Door calls made through MCP do not pass through
it, so the reporter undercounts cheap-door use. The report states the blind
spot on every run. A measurement that hides what it cannot see is the failure
this whole repo exists to stop.

---

## Disproof — registered before the forms were built

This gate is refuted if the hook fires and hand-reading continues. The
advisory form would then be theatre, and must become blocking or be deleted.

**Baseline, measured on the day of writing:** roughly 4 cheap-door calls
against 40 hand-reads in one session. That number is bad, it is honest, and it
is what the next measurement is compared against.
