# Gate 12 — completer

    order:  12. VERIFY, after karsholto and before nomess. Decide what is
            genuinely left before sweeping for mess.
    forms:  skill · hook
    ruled:  the operator, 2026-09-01 — full moon. A hook catches deferral
            language in output. Tool, code and agent are inapplicable, not
            deferred.

---

## The read

**About to write "follow-up / next session / separate pass / deferred"? Classify
it before you write it.**

Two things wear the same words:

- **A GENUINE blocker** — data, a decision or access you lack, or a distinct NEW
  build. Name it, and name what would unblock it.
- **Stopping short** — "it's big", "end of session". Those are cop-outs. Finish
  it now. The user outcome is the whole job.

**32 FIRED, 4 BLOCKED**, and the four BLOCKED rows are this gate working rather
than failing. Every one names what is unverified and what remains:

> Unverified: whether the popup actually stopped. Only you can confirm. Nine
> adhoc-python jobs remain, and gmail sync is off

> Unverified: whether the modal actually stopped. Nine other adhoc-python jobs
> remain unconverted

That is the shape: **a blocker outside my reach, named, with the count of what
is left.** Residue is legitimate. Silent residue is not.

## The intent

Make the difference between "I cannot" and "I did not want to" visible, in
writing, at the moment it is decided.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: classify the residue, name the blocker AND what unblocks it | before any done-with-residue claim |
| **hook** | `hooks/hook_completer.py`, `Stop` — reads the turn's last output for deferral language and asks which of the two it was | every turn that uses those words |

**The hook asks the question; it cannot answer it.** No pattern distinguishes a
real blocker from a cop-out — they are written in identical words, which is
precisely why the gate exists. A hook that tried to decide would be a green
check standing in for the judgement, which this suite forbids.

**It reads only the LAST assistant message, and only the tail of the
transcript.** The deferral phrases appear constantly in tool output and in the
operator's own words; flagging those would train the reminder into noise within
a day, which is how `mark_build.py` had to be repaired. Parsing a whole session
on every turn would be a tax on every turn.

**No tool, no code, no agent.** The classification is a judgement about what I
could have finished, and nothing outside my context can make it.

## Disproof

Refuted if this gate reports FIRED, residue is named as blocked, and it turns
out I could have finished it with what I had at the time.

**Watchable and directly checkable** — every BLOCKED row states the blocker, so
a later reader can ask whether it was real. All four on record name something
outside my reach: another person's confirmation, a peer's idle window, an
environment restart.

**The hook's own blind spot:** it fires on the WORDS, so residue left silently —
work simply not mentioned — passes it untouched. Silence is the harder failure
and this form does not catch it. Gate 18 is what catches that.

**And it has a measured false-positive loop.** Observed 2026-09-01: the hook
matched the phrase "the two follow-up calls", which described calls already
made, not work postponed. Answering the reminder required quoting the phrase —
which re-armed the hook, which demanded another answer. **A word-matching Stop
hook that reads its own turn's output cannot be answered in words it matches.**

That is left as a known cost rather than patched, and the reasoning is gate 05's:
the alternative is a growing exemption list of contexts, which is the
hand-maintained enumeration this estate has been burned by repeatedly. The gate
fails toward flagging on purpose. The correct response to a false positive is
one line classifying it — and the loop ends when the classification stops
quoting the trigger.

**REVISIT** if BLOCKED rows start naming blockers that dissolve on inspection —
that is stopping-short learning the vocabulary of a real blocker, which is worse
than the plain cop-out because it reads as rigour.
