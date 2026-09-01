---
name: retrieval-economy
description: Gate 02 — take the cheapest retrieval door that ANSWERS, and never spend a judgement call on a lookup. Climb from the top: mind grep / mind check / mind moons / SQL over the ledger all answer in ~1.5 KB with ZERO model calls; mind consult goes LAST because it spends an Opus call and 10-20s — it is the most expensive door, not the first. Re-measure before quoting any number; byte counts are query-dependent. Use codebase-memory search_code for code structure — about 99% fewer tokens than reading files. Zero hits is a REAL answer that vector search cannot give. Trigger: about to read a corpus, grep a repo, brief a subagent, or answer a question about what exists.
---

# retrieval-economy — ask an index, do not read a corpus

The full read (origins, industry use, what is ours) lives in `GATE.md`.

## Climb from the top

Costs below are from one measured query ("<term>", 2026-08-22, on the den host).
They are ORDERS OF MAGNITUDE, not a fixed ranking — re-measure before quoting.

| question | door | cost |
|---|---|---|
| Does the estate know this word at all? | `mind grep <term>` | ~1.6 KB, 0 calls |
| Is this retired or superseded? | `mind check <entity>` | ~1.5 KB, 0 calls |
| What has he ruled on X? | `mind moons <subject>`, or SQL | ~1.4 KB, 0 calls |
| Where is this function, who calls it? | `codebase-memory search_code` | ~1% of reading |
| I need judgement across several pages | `mind consult` | **1 Opus call, 10–20s** |

## The rules

1. **Never spend a judgement call on a lookup.** If the answer is a fact, a
   membership test, a count, or a name, a deterministic door has it.
2. **Prefer structure over similarity.** SQL and full-text search are exact
   and free. `mind check` reads supersession straight from page frontmatter,
   also free. Embeddings are approximate and cost a call to rerank.
   (There is no standalone tombstone-graph command. An earlier version of this
   skill told agents to call one. It did not exist.)
3. **Zero results is information.** Write it down. Do not escalate to a more
   expensive door to obtain a non-empty answer.
4. **Reading a source file by hand is the poured path wearing a shell prompt.**
   Before `grep`, `sed` or `cat` on a repo, ask `search_code`.
5. **MCP first; if an MCP will not call, find the CLI door.** A tool showing
   "connected" can still be unusable. Do not abandon the capability.
6. **`mind page` by NAME beats similarity.** Some pages are too large to
   retrieve well by embedding. If you know the slug, fetch the slug.
7. **Subagents QUERY; they are not briefed.** Give an agent the command, not
   the canon. The test is that the prompt is short.

## What this gate does NOT say

It does not say spend less. Spend freely on adversarial review and on deriving
what is not yet known. Spend nothing on re-reading and re-deriving.
