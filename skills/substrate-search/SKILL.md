---
name: substrate-search
description: Design-phase gate — before creating anything new (table, module, endpoint, script, skill, doc, abstraction), answer in writing "what existing piece is insufficient?" Search the repos' CURRENT state — concurrent sessions, git-log, grep — not your memory. Default: reuse. Never build a parallel "fallback" to something that works; never place an artifact in a canonical home whose runtime doesn't exist yet. The discipline conductor's design gate. Trigger: about to create a file/primitive/layer, or "substrate" / "substrate-search".
---

# /substrate-search — what existing piece is insufficient?

Before any new substrate exists, answer in writing: **"What already
does this, and what specifically makes it insufficient here?"** A weak
answer kills the proposal. Default: reuse.

The answer must hold against the repos' CURRENT state, not your
working memory — concurrent sessions build things you can't recall.

## Search (don't recall)

1. If other sessions may be editing the same files, read the team's
   coordination ledger first (if one exists) and register your lane.
2. `git log --oneline -15 -- <paths>` on each repo you'd touch.
3. `grep -rn '<concept>'` for existing names/functions; honor any
   KEEP-IN-SYNC / GENERATED / CONTRACT marker nearby — mirror, don't fork.
4. The repo's canonical doc + memory index for "does this exist?" —
   then confirm against code.
5. **Consuming side:** about to code against a dependency (an API
   route, a symbol, a column, a config key)? Confirm it EXISTS with the
   expected shape — curl the endpoint, grep the symbol, read the schema
   — never infer it from a sibling's name.

## Verdict

- Found a fit → use it. Deprecated-looking or half-fit → ASK, don't
  build a sibling.
- Found nothing, need is REAL and in flight → build, and record the
  one-line justification in writing: what existing piece was
  insufficient, and why.
- A "fallback" / "alternate" / "simpler" version of a working
  load-bearing piece is banned, not a design option.

## Placement

Smallest invocable artifact in a runtime that exists TODAY. Don't
build a canonical/shared home ahead of its runtime; promote only when
the runtime exists, ≥2 instances motivate it, and drift is real.

## Self-check

- Can I name the piece I'm NOT using, and why, in one sentence?
- Did I search current state, or recall it?
- Is this a fallback for something that already works? Stop.

## Cross-references

- `discipline` design gate #1; `karsholto` / `think-3x` fire next on
  survivors; `nomess` is the mirror at the end.
