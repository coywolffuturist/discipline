---
name: ste
description: ASD-STE100 Simplified Technical English — gate 01, and FIRST because order is information. Governs what I write to MYSELF (notes, plans, canon pages) and to OTHER AGENTS (subagent prompts, agent-to-agent messages). Short sentences, one idea each, active voice, no stacked clauses. Keep the EXACT technical term wherever precision needs it — accuracy always outranks simplicity. Score any prompt with gates/01-ste/ste.py and put the number in the completion table. Trigger: writing any agent prompt, canon page, plan, or working note.
---

# STE — the language I think and coordinate in

The full read (origins, industry use, what is ours) lives in `GATE.md` beside
this file. This is the working standard.

## The rules

1. **Short sentences. One idea per sentence.** The limit is 25 words for a
   descriptive sentence, 20 for an instruction. Score, do not guess.
2. **Active voice. Say who does what.** "The parser dropped 28 claims", not
   "28 claims were dropped".
3. **Plain words — EXCEPT where a technical term is required to be precise.**
   Then use the exact term. **Never trade accuracy for simplicity.** This
   exception is the operator's and it is load-bearing.
4. **No stacked noun phrases. No metaphor stacks. No em-dash chains.**
5. **State the outcome first**, then the evidence beside its number.
6. **No ambiguous pronouns.** If "it" could point at two things, name the thing.

## Who this is for

Myself, later — and other agents. Both read without the author present, and
neither can ask a clarifying question cheaply.

The operator is not the primary audience. His reports inherit the clarity, but
the gate aims at the machine-facing surface, because that is where a misreading
goes uncorrected.

## The judgment case this form owns

Everything above is arithmetic and belongs to the tool. **One question is not:**
*is this technical term necessary, or am I hiding behind it?*

Ask it directly. If a plain word carries the same meaning with no loss of
precision, use the plain word. If it does not, keep the term and explain it in
the same breath.

## The compliance test

**If the agent prompt is not short, the thinking behind it was not clear.**

A long prompt is a symptom, not a style choice. Score it:

    python3 gates/01-ste/ste.py --stdin < prompt.txt

Put the score in the completion table. The table cannot be left blank; that is
the enforcement.
