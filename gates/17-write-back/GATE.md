# Gate 17 — write-back

    order:  17. VERIFY, after chunk-it and before adversarial-pass. Chunk-it
            captures the MOVE; this captures the FACT.
    forms:  code
    ruled:  the operator, 2026-09-01 — full moon. The bar is one cheap call to
            re-derive. Folds into the completion rule; no skill of its own.
    where:  `capture.py` runs on the primary workstation and writes to the
            private memory store, which is not in this repo.

---

## The read

**Did you derive something reusable and non-obvious — a measured number, a path,
an endpoint, a trap, a ruling? Write it to memory now.**

The bar was ruled: **write it back only if re-deriving would cost more than one
cheap call.** That test keeps the expensive findings and rejects roughly half of
what I would otherwise save.

It earns its place on the cheap side too. Signing a message required a venv whose
location had never been written down; finding it cost five calls that a single
recorded line would have made zero. Derivation is expensive once and retrieval is
cheap forever — but only if it was written down.

**Both halves or neither.** A memory file that is never indexed is not
retrievable, and an unretrievable file is indistinguishable from one that was
never written. This estate has a name for that failure: structure without a
reader. `capture.py writeback` writes the file and the index line in one act and
refuses if either does not land.

Across one day this gate was BLOCKED 11 times of 36 — the most-blocked gate after
adversarial-pass, and for the same reason: it fires at the end, when the
derivation already feels obvious.

## The intent

Pay a derivation once, so the next agent — including me tomorrow — retrieves it
instead of rediscovering it.

## The forms

| form | what it is | when |
|---|---|---|
| **code** | `capture.py writeback <name> <description> --kind <type> --body <text> --index <line>` — writes the memory file AND its index pointer, verifies both landed, and refuses to create a duplicate of an existing file | every turn that derived a reusable fact |

**No skill, by ruling** — an obligation on every turn, so it lives in the
completion rule.

**No hook, per gate 05:** the completion table already demands this row. The gap
was the append, not the demand. Shared mechanism with gate 16, separate rows.

## Disproof

Refuted if a fact is written back and later re-derived from scratch anyway —
which means it was written somewhere retrieval does not reach, and the write was
theatre.

Watchable and it has fired: a recorded fact about where the discipline repo lived
went stale when the repo moved, and a reader acted on the old location. The
remedy in that case was not a better index but **correcting the entry**, which is
why the tool refuses to create a second file where one exists.

**REVISIT** when the store gets a retrieval evaluation. Today the write half is
mechanical and the read half is not measured, so "did this actually get
retrieved" is unanswered — the honest limit of this gate.
