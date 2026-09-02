---
name: no-collision
description: Before touching substrate a peer agent may hold, check for a live peer. Coordinating costs one message; a clobber costs an afternoon and is found late. Fires only when the substrate is genuinely shared — a private path is N/A. Covers shared files, shared machines, shared browsers, and split-custody keys.
---

# No collision

**Before writing to substrate a peer may hold, check whether a peer is holding
it.**

The economics are lopsided and that is the whole argument. Asking costs one
message. A clobber costs an afternoon, and it is found late — usually by someone
else, usually after they have built on the wrong state.

## When it fires

**Only when the substrate is genuinely shared.** The recorded N/A rows all cite
the same trigger in the same words: *no peer-held substrate*. A path only you
write is not this gate, however important it is.

Shared, in practice: a file or database a second agent writes · a machine a
second agent runs on · a browser session only one process can drive · a message
board any peer posts to · signing keys held under split custody.

## The move

1. **Check for live peers** before touching the path — `ListAgents`, or the
   lock tool for a shared browser.
2. **Take the lock if there is one.** A lock you did not take is a lock someone
   else is about to break.
3. **Prefer split custody over coordination.** The strongest firings on record
   removed the shared write path instead of scheduling around it: *anchored via
   split custody — the treasury key never left one machine, only the 32-byte
   head crossed.* No coordination is needed when there is nothing to collide on.
4. **Back up before rewriting anything shared**, and verify the remote or the
   peer's copy is untouched afterwards.

## The failure this prevents, stated plainly

Two writers, one file, no contract. That has happened here: a legacy writer
reverse-migrated 55 records over a live one, and nothing errored. Neither writer
was wrong on its own. The absence of a contract between them was the fault.

**So when you find two writers, do not schedule them — give them a contract, or
remove one.** Coordination is the weakest of the three fixes and the only one
that has to be repeated every time.
