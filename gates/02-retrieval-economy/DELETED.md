# hook_corpus_read.py and door_report.py — DELETED 2026-08-22

Not repaired. Deleted, after three refutations.

## Why

**It leaked credentials by construction.** `SECRETISH` redaction was applied to
the path but never to the verb, and the cheap-door regex deliberately captured
the leading environment assignment — which is exactly where a key lives. A
refuter wrote `ANTHROPIC_API_KEY=<key> corpus check opus` and the key landed
verbatim in a mode-0644 file. The test that was supposed to catch this put its
fixture in a grep argument, which the code discards anyway, so the redactor was
never exercised.

**It was systematically wrong, not noisily wrong.** 12 of 25 realistic commands
misclassified. Ordinary commit messages logged as corpus hand-reads, because
the reader pattern matches the English words "cat", "more", "less" and "cut".
The commonest cheap-door idiom, `cd X && corpus grep`, logged nothing, because
the door pattern is anchored to the start of the line. The numerator deflated
and the denominator inflated — both toward the same wrong answer.

**It was write-only.** The hook wrote a field called `shape`; the report read a
field called `detail`. Every report printed "(no detail recorded)". Nobody
noticed, because nobody read it.

## What replaces it

Nothing, for now. A ratio built from a classifier that is wrong half the time
is worse than no ratio: it gets pasted into a completion table as evidence.

The DOORS still exist and still work — `corpus grep`, `corpus check`,
`codebase-memory search_code`. The gate's tool form is real. What is deleted is
the attempt to MEASURE whether they were used.

If a measurement returns, it must count tool calls at the source rather than
pattern-match shell text, and it must be tested against commands nobody wrote
for it.
