---
name: compile-it
description: Agents think; code does. Before reasoning through a procedure, decide whether it should be DETERMINISTIC CODE instead — a script, hook, query, or function that runs free and identically forever — rather than re-reasoned with tokens each time. WRITE THE HARD CODE when ALL four hold: (1) it repeats / recurs, (2) the steps are mechanical (fixed given inputs, no judgment), (3) the rules are stable, (4) correctness is checkable (a test / expected output / backtest). Keep it LLM-driven when novel, judgment-laden, fast-changing, or unevaluable. Crystallize on the 2nd–3rd repeat, never the 1st. Trigger: about to re-run a multi-step mechanical procedure, a scheduled/looping task, or "compile-it".
---

# compile-it — agents think, code does

Tokens are for thinking, which happens rarely. Doing is cheap and happens
forever — so the doing belongs in deterministic code, not in re-reasoning the
same steps with the model every run. Use the model as a COMPILER (understand the
task once, emit the code) not a RUNTIME (re-derive it on every run).

## WRITE THE HARD CODE when ALL four identifiers hold

- **Repeats** — you've done it before, it's scheduled, or it loops. Sharpest
  tell: *you're about to re-reason something you've already reasoned through.*
- **Mechanical** — steps are fixed given the inputs: grep, transform, compute,
  validate, move/format data. No genuine judgment in the loop.
- **Stable** — the rules aren't changing every run; the logic is settled.
- **Checkable** — correctness has an eval (a test, an expected output, a
  backtest). No eval → it would decay into slop; don't compile yet.

All four hold → STOP re-reasoning and emit the script / hook / query / function.
It then runs free, fast, and identically every time.

## Keep it LLM-driven when ANY hold

- **Novel** — first encounter, no proven pattern to compile.
- **Judgment-laden** — taste, ambiguity, the human's call.
- **Fast-changing rules** — compiling now is premature and brittle.
- **Unevaluable** — you can't measure correct, so you'd compile slop.
- **It embeds a human gate.** A deliberate checkpoint the human must own — what
  goes public, money movement, an irreversible or outward-facing decision. Even
  when the surrounding steps are mechanical, do NOT compile the gate away: the
  friction is the feature — it forces the human pause. Compile the grunt-work
  *after* the gate clears, never the gate itself.

## Timing

Crystallize on the **2nd–3rd repeat, never the 1st.** Build the eval first
(karsholto), prove the procedure, then compile. Premature hard code is worse
than re-reasoning — you ship the wrong procedure, and now it's a landmine.

## Auditing a system for candidates

Scanning a codebase, a set of crons, or your own session work for what to compile:
- **Inventory the recurring procedures** — scheduled jobs, loops, and the steps
  *you re-derive by hand each session* (the richest seam — well-written automated
  code is usually already split right: mechanical in code, model for judgment).
- **Score each** against the four identifiers + the guards above; **rank by
  leverage** (heaviest token-spend first, don't boil the ocean); **name each
  candidate's eval** before compiling.
- **Don't manufacture candidates.** "Already disciplined" is a valid, valuable
  result — and never compile a human gate just because the steps around it are mechanical.

## One line

Agents think once; code does forever. Re-deriving mechanical, stable, checkable
steps you've derived before → write the hard code.
