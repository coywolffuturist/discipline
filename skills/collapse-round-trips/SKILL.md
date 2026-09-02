---
name: collapse-round-trips
description: Before issuing a call, ask what ELSE you will need if it returns as expected — and send that in the same call. A round trip is not free: it costs a full request, and a chain of them is one action split into six. Fires when two or more calls could have been one. Not about doing less work; about not paying six times for one answer.
---

# Collapse round-trips

**Before a call, ask what else you will need if it returns as expected. Send
that too.**

Every call re-sends the whole conversation. A chain of six probes costs six
requests to answer one question. The gate fires on **foreseeable** chains — the
follow-up you already know you will make.

## When it fires

Two or more calls that could have been one. In practice:

- a probe, then the obvious follow-up on its result
- reading four files one at a time to answer one question
- a check, a fix, then re-running the same check
- polling in a loop when one wait would do

## When it is N/A, and this is the honest half

**A branch you could not foresee is not a round trip.** If the second call
exists *because* the first returned something you did not predict, batching was
never available. The recorded N/A rows say it plainly: *one-shot verification*,
*a single append*, *one-shot correction*.

Do not collapse calls whose results must be read before the next is written. A
batch that guesses the second step is worse than two honest calls — it produces
a confident answer to a question the evidence had not yet reached.

## The two failure modes, and the second is the expensive one

1. **Six calls for one answer.** Slow and costly, and visible.
2. **A batch that hides a failure.** Twelve assertions in one `ssh` is a
   collapse — but if the shell aborts on the fourth, the last eight report
   nothing and the batch still looks like it ran. Batch calls that are
   INDEPENDENT. When one step's failure should stop the rest, that is a
   sequence, not a batch.

Never read `$?` after a pipe: it returns the pipe's exit, not the command's.
That mistake produced three false findings in one day, and a batch makes it
harder to see.

## The move

State what the call should return. Name the follow-up you already know you will
need. Send them together, independent of each other, and check each result
separately rather than trusting one exit code for all of them.
