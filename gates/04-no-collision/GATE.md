# Gate 04 — no-collision

    order:  04. DESIGN, after collapse-round-trips and before substrate-search.
            Find out who else is holding the thing before you propose changing
            it.
    forms:  skill · tool · hook
    ruled:  the operator, 2026-09-01 — full moon. The lock tool exists; a hook
            warns before touching a shared path. Code and agent are
            inapplicable, not deferred.
    where:  the tool `gui-browser-lock` lives on the SECOND MACHINE and is
            invoked over ssh — `gates/13-nomess/nomess.py --remote` already
            calls it.

---

## The read

**Before writing to substrate a peer may hold, check whether a peer is holding
it.**

The economics are lopsided, and that is the whole argument. Asking costs one
message. A clobber costs an afternoon and is found late — usually by someone
else, usually after they have built on the wrong state.

**28 FIRED, 8 N/A**, and every N/A cites the same written trigger in almost the
same words: *no peer-held substrate.* That consistency is what makes the N/A
checkable — a path only you write is not this gate, however important it is.

**The strongest firings did not coordinate. They removed the shared write
path:**

> Anchored via split custody — the treasury key never left one machine, only the
> 32-byte head crossed.

> Anchored while her cycle ran; split custody meant no shared write path.

That is the ranking this gate teaches. **Split custody beats a lock, and a lock
beats coordination** — because coordination is the only one that must be
repeated every single time.

**The failure it prevents has happened here.** Two writers, one file, no
contract: a legacy writer reverse-migrated 55 records over a live one and
nothing errored. Neither writer was wrong alone. The missing contract between
them was the fault.

## The intent

Never be the second writer to a thing that has no contract.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: check for peers, prefer split custody, back up before rewriting anything shared | before touching shared substrate |
| **tool** | ADOPTED — `gui-browser-lock who` on the second machine, the only lock in the estate today | the shared browser |
| **hook** | `hooks/warn_shared_path.py`, `PreToolUse[Bash]` — names the shared path a WRITE is about to touch | every write |

**THE HOOK WARNS. IT DOES NOT DENY, AND THAT IS DELIBERATE.** Three versions of
a denying Bash-text guard were built in this suite and all three were refuted;
the third simultaneously allowed the thing it targeted and denied a plain
`grep`. A false denial is what gets a guard switched off. This one raises the
question and gets out of the way.

**Its first version was wrong in BOTH directions**, and a refuter found it the
day it shipped. It matched a list of write VERBS, so `echo x > ~/pack/board.txt`
and `printf x >> ~/pack/rendezvous/log` passed silently — and `cat >
~/pack/rendezvous/board.db` was *actively exempted* by the read-shape early
exit. Meanwhile `ssh den 'cat notes.md'`, a pure read, warned. The PATHS matched
every time; the verb list was the hole. A write is now a write verb **or a
redirection**, the read exit applies only when there is no redirection, and a
read-only `ssh` payload passes. Baited on **fourteen** shapes, both directions, and the baits are in the repo
at `lint/bait_warn_shared_path.py`, wired into `lint/all.sh`. An earlier version
of this file said "baited on twelve shapes" with the baits living only in a
session transcript — unfalsifiable by any reader, which is the property gate 09
forbids. Two of the fourteen are the defects reviewers actually found: a
redirect write that passed silently, and `ssh host "python3 -c ...write..."`
classified as a read.

**What it cannot do, stated rather than implied:** it does not know whether a
peer is actually holding the path right now. That is the lock's job. The hook
only notices that the path is *shared*, which is the fact I forget.

**No code, no agent.** Whether a peer is live is a question about the world at
this instant, answered by `ListAgents` or the lock — not by a static check. An
agent without the context cannot know what is shared.

## Disproof

Refuted if this gate reports FIRED and two writers still meet on one path.

Watchable: the 55-record reverse-migration is the recorded instance, and it
predates the hook. The honest limit is that **the hook covers only the paths
listed in it** — the pack tree, the Rendezvous, the second machine, the shared
browser, the signing keys. A shared path not on that list is invisible to it,
and the list is hand-maintained, which is the failure class that broke
`skill_share.sh` five times.

**But the refutation came from the other side.** Every silent miss had a
matching path and an unmatched VERB. Both lists are enumerations of things I
thought of, and enumerations are what this estate keeps getting wrong.

**REVISIT** when a second lock exists, or when the shared-path list can be
derived rather than maintained. Until then the hook is a reminder over a known
set, not coverage.
