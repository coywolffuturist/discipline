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

We measured our own ladder. **Provenance, because the first version of this
table had none and every row I could re-run came out wrong:**

    query: "<term>"   date: 2026-08-22T21:09Z   host: <host>
    corpus: <corpus>/corpus, 1,372 .md files

| door | bytes | model calls | seconds |
|---|---|---|---|
| `corpus rulings` | 1,363 | 0 | 0.08 |
| `corpus check` | 1,496 | 0 | 0.30 |
| `corpus grep` (FTS5) | 1,567 | 0 | 0.91 |
| `corpus consult` | ~3,500 | **1 Opus** | 10–20 |
| reading the corpus by hand | **5,398,044** | 0 | — |

**Roughly 3,400x between the cheapest door and reading the corpus.** That is
the finding, and it survives the correction.

### What the first version of this table got wrong

It claimed 400 bytes for `corpus grep` (measured: 1,567 — 3.9x low), 595 for
`corpus check` (measured: 1,496), and 4,326,756 for the corpus (measured:
5,398,044 — 25% low). It also carried a **tombstone graph** rung at 9 bytes.
**There is no such door.** "Tombstone" appears only in the description of what
`corpus consult` does internally. `SKILL.md` instructed agents to call a command
that does not exist, and rule 3 of that same skill forbids escalating when it
failed. The rung is deleted.

**Byte counts are query-dependent and the ordering can change with the query.**
On this query `corpus rulings` came back smaller than `corpus grep`. Treat the ladder
as orders of magnitude, never as a fixed ranking. Re-measure before quoting.

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
