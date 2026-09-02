# Gate 16 — chunk-it

    order:  16. VERIFY, after vizcheck and before write-back. Both are appends;
            this one captures the MOVE, the next captures the FACT.
    forms:  code
    ruled:  the operator, 2026-09-01 — full moon. A wrong conclusion is a chunk
            by definition. Folds into the completion rule; no skill of its own.
    where:  `capture.py` runs on the primary workstation and appends to the
            ledger in the private memory store, which is not in this repo.

---

## The read

**Did anything become a named move that will cost almost nothing next time?
Append it now — at the moment, not in a handoff.**

The trigger was ruled to remove my judgement from it: **a wrong conclusion is a
chunk by definition.** Not "was this interesting" — if something cost a wrong
conclusion, it is a chunk whether or not it feels like one.

The failure mode is silence. A chunk not written is simply lost, and nothing
notices; there is no red build, no failing test, no reader who complains. Across
one day this gate was BLOCKED 9 times out of 36 — always at the end of a turn,
scanning what had just happened, which is the moment I am least able to see it.

**A ledger entry is not a fix.** One lesson recorded that morning — *a hardcoded
list needs a checker, not a more careful author* — was hit twice more the same
day, because the chunk named a mechanism and the mechanism was never built.
Capturing is necessary and is not sufficient.

## The intent

Make the second encounter with a problem cheap, by writing the move down at the
moment it is understood rather than at the moment it is needed.

## The forms

| form | what it is | when |
|---|---|---|
| **code** | `capture.py chunk "<title>" "<body>"` — appends to the ledger above the Pending anchor, then reads the file back to confirm it landed | every turn that produced a named move or a wrong conclusion |

**No skill, by ruling.** This is an obligation, not a judgement: it fires on every
turn, so it belongs in the completion rule rather than in a document to consult.

**No hook, and gate 05 is why.** The completion table already demands this row on
every turn that changed something, so a second hook would add a demand where one
exists. What was missing was the append itself — roughly ten hand-written Python
heredocs in one day, each re-deriving the anchor and the escaping, one of which
silently did not land and was reported as though it had. That is compile-it's
trigger met several times over, and it is what `capture.py` fixes.

The tool verifies its own write, refuses when the ledger's anchor is missing
rather than guessing where to append, and is shared with gate 17 — two gates, one
mechanism, separate rows.

## Disproof

Refuted if a turn produces a named move, this gate reports FIRED, and the move is
not in the ledger afterwards.

Directly checkable: the ledger is a file, and `capture.py` reads back what it
wrote. **The failure has already happened once** — a chunk claimed as appended
that was not, which is why the read-back exists.

The harder disproof, which the tool cannot serve: refuted if the ledger fills
with entries and the same class of error keeps recurring. That happened three
times in one day with one entry, and it is the reason the file above says
capturing is not fixing.

**REVISIT** if the ledger grows past what a reader can hold — at which point the
gate needs a retrieval story, not a bigger append.
