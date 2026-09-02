# Gate 03 — collapse-round-trips

    order:  03. DESIGN, after retrieval-economy and before no-collision. The
            cheapest door is chosen first; this decides how many times you walk
            through it.
    forms:  skill · hook · code
    ruled:  the operator, 2026-09-01 — full moon. A hook that counts
            near-identical sequential calls in a turn, and a check that flags
            foreseeable chains.

---

## The read

**Before a call, ask what else you will need if it returns as expected — and
send that in the same call.**

Every call re-sends the whole conversation, so a chain of six probes pays six
times for one answer. The gate fires on the **foreseeable** follow-up: the one
you already know you will make.

Across one day: **35 FIRED, 1 N/A**. Not the highest FIRED rate in the suite —
disprove-first ran 38 of 38, nomess 37 of 37, and set-the-prior 35 of 35, all
perfect. This one is 35 of 36. An earlier version of this file called it "the
most consistently fired gate in the suite", which was an impression, not a
count. The artifacts show what a firing looks like:

> 16 accumulator assertions in one python -c; 10 clock assertions in another;
> census fix + doc fix + control + census re-run in one ssh

And what a MISS looks like, recorded in the same log:

> Watch in one ssh; on-chain verification in one call. Weakest gate this turn —
> six sequential discovery calls hunting the venv and the CLI shape that one
> memory file would have collapsed to zero

**The one N/A names the honest limit:** *a single append.* A branch you could
not foresee is not a round trip. If the second call exists because the first
returned something unpredicted, batching was never available, and a batch that
guesses the second step answers a question the evidence had not reached.

**The second failure mode is the expensive one, and it is caused by this gate.**
Twelve assertions in one `ssh` is a proper collapse — but a shell that aborts on
the fourth reports nothing for the last eight, and the batch still looks like it
ran. That has happened here: **zsh errors on an unmatched glob and aborts the
whole command**, which produced a GREEN result over three real defects. Batch
calls that are INDEPENDENT. When one step's failure must stop the rest, that is
a sequence, not a batch.

## The intent

Pay once for one answer, without letting the batch conceal which part failed.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: name the foreseeable follow-up, batch independent calls, never trust one exit code for many | before any probe |
| **hook** | `gates/06-compile-it/repeats.py`, `PostToolUse[Bash]` — logs the SHAPE of each command | every call |
| **code** | `repeats.py report` — the gate 03 reading: shapes issued back-to-back | when the table is filled |

**THE LOG IS NOT TURN-SCOPED, and an earlier version of this file said it was.**
Nothing truncates or rotates `$TMPDIR/coywolf-cmd-shapes.log`, so it spans the
whole session and a "back-to-back" pair can straddle a turn boundary. The count
is still evidence — two identical shapes in a row are worth seeing wherever they
fall — but it is a SESSION reading, not a turn reading. Read it as such.

**Shared with gate 06 compile-it, and separate rows.** Both gates count a
repeat; they differ in window and remedy. Gate 03 reads the same shape issued
**twice in a row** and the remedy is to batch. Gate 06 reads a shape reaching
**three** in the session log and the remedy is to write the script. One mechanism,
two readings — the arrangement `capture.py` has with gates 16 and 17.

**Quoted text is treated as data, not action.** `grep "rm " f.txt` reduces to
`grep S f.txt`. That is `mark_build.py`'s expensive lesson: matching command
TEXT made a guard fire on nearly every turn until it was anchored instead.

**No tool, no agent.** Whether two calls could have been one is a judgement
about foreseeability, and an agent without the context cannot make it.

## Disproof

Refuted if this gate reports FIRED and the turn still shows a chain of calls
whose follow-ups were foreseeable.

**Directly checkable, which is unusual for a DESIGN gate** — `repeats.py report`
counts back-to-back shapes from a log, so the claim can be audited rather than
asserted. **An absent or empty log reports UNVERIFIED, not zero.** A counter that
reads a missing log as "no repeats" would report health it does not have.

The harder disproof the counter cannot serve: a batch that ran green while
concealing a failure inside it. The counter sees one call and calls it
collapsed. Only reading each result separately catches that.

**REVISIT** if firings start batching dependent steps to lower the count — that
is the gate being gamed by its own instrument, and it is worse than the chain.
