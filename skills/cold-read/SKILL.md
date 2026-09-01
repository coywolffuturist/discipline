---
name: cold-read
description: The primary reader of everything you write — code, config, docs, data — is a future agent with NO context who will ACT on it. Before shipping or retiring any artifact, read it as that agent would: does anything dead/deprecated/superseded read as LIVE? Could it be mistaken for current? Is the intent legible without you? When you retire something, tombstone-or-remove it AND eliminate the whole CLASS (sweep every occurrence), never just the instance you tripped over. Trigger: shipping / retiring / replacing an artifact, or "cold-read".
---

# cold-read — the next agent is your reader; build so it can't misread you

Everything you write will be read, with no memory of this moment, by a future
agent that will act on it. That agent is your primary user. Write — and
delete — for it.

## The cold-read test (before calling an artifact done)

Read it as a context-free agent would:
- **Could it be mistaken for current / authoritative when it isn't?**
- **Does anything dead, deprecated, or superseded read as LIVE?** — a retired
  identifier, a replaced config, a stale flag, an old endpoint, a superseded
  doc presented as the canon.
- **Is the intent legible without you to explain it?** — would the next agent
  reconstruct *why*, not just *what*?
- **One source of truth, or competing copies that will silently diverge?**

If a cold agent would reason or act wrongly from it, it isn't done.

## When you retire or replace something

A deprecated artifact left bare is a landmine — the next agent reasons from it
as if it were live, and propagates the error.
- **Tombstone or remove.** Delete it, or mark it unambiguously dead where it
  lives (DEPRECATED / SUPERSEDED-by-X, with a pointer to the live thing). Never
  leave a dead thing in a live-looking context.
- **Eliminate the CLASS, not the instance.** What you're retiring is rarely in
  one place. Search the whole substrate — every repo, file, and store — and
  neutralize every occurrence. The one you tripped over is not the only one;
  patching instances as you find them is the failure mode. If the sweep is mechanical and recurring, compile it (`compile-it`) instead of re-reasoning it each time.
- **Keep one canonical tombstone**; redact everywhere else and point to it.

## The rule

You write for an agent later who cannot ask what you meant. Make it impossible
to misread.
