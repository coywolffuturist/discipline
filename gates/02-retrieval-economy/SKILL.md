---
name: retrieval-economy
description: Gate 02 — take the cheapest retrieval door that ANSWERS, and never spend a judgement call on a lookup. Climb from the top: tombstone graph (9 bytes) → corpus grep (400 bytes, 0 model calls) → corpus check → SQL over the ledger → corpus rulings → corpus consult LAST (1 Opus call, the most expensive door, not the first). Use codebase-memory search_code for code structure — about 99% fewer tokens than reading files. Zero hits is a REAL answer that vector search cannot give. Trigger: about to read a corpus, grep a repo, brief a subagent, or answer a question about what exists.
---

# retrieval-economy — ask an index, do not read a corpus

The full read (origins, industry use, what is ours) lives in `GATE.md`.

## Climb from the top

| question | door | cost |
|---|---|---|
| Does the estate know this word at all? | `corpus grep <term>` | 400 bytes, 0 calls |
| Is this retired or superseded? | `corpus check <entity>` | 595 bytes, 0 calls |
| What has he ruled on X? | `corpus rulings <subject>`, or SQL | ~1k, 0 calls |
| Which page supersedes which? | the tombstone graph | 9 bytes |
| Where is this function, who calls it? | `codebase-memory search_code` | ~1% of reading |
| I need judgement across several pages | `corpus consult` | **1 Opus call, 10–20s** |

## The rules

1. **Never spend a judgement call on a lookup.** If the answer is a fact, a
   membership test, a count, or a name, a deterministic door has it.
2. **Prefer structure over similarity.** SQL, full-text search and the
   supersession graph are exact and free. Embeddings are approximate and cost a
   call to rerank.
3. **Zero results is information.** Write it down. Do not escalate to a more
   expensive door to obtain a non-empty answer.
4. **Reading a source file by hand is the poured path wearing a shell prompt.**
   Before `grep`, `sed` or `cat` on a repo, ask `search_code`.
5. **MCP first; if an MCP will not call, find the CLI door.** A tool showing
   "connected" can still be unusable. Do not abandon the capability.
6. **`corpus page` by NAME beats similarity.** Some pages are too large to
   retrieve well by embedding. If you know the slug, fetch the slug.
7. **Subagents QUERY; they are not briefed.** Give an agent the command, not
   the canon. The test is that the prompt is short.

## What this gate does NOT say

It does not say spend less. Spend freely on adversarial review and on deriving
what is not yet known. Spend nothing on re-reading and re-deriving.
