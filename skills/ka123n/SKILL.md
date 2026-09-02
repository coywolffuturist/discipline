---
name: ka123n
description: "The standing build mode — a rolling window of the 3 most important next steps, where the ranking IS a ranking of the most +EV usage of the processed bits available. Execute #1, re-evaluate #2/#3 against fresh evidence and steering, slide forward, generate a new #3. Behind the window stays unplanned BY DESIGN. Trigger: always on for real work; re-rank on every steer, verdict, or budget change."
---

# Ka123n — the rolling three

## What it is

A window of exactly **three next steps, ranked**. The ranking is not a task
queue and not a priority label: it is **a ranking of the most +EV deployment
of the processed bits available right now** — attention, model calls, compute,
context. The question the ranking answers is always: *given what we hold and
what it costs to spend, which use of bits buys the most expected value?*

Lightweight scales. Heavy collapses under its own weight. Three is a hand you
can hold; everything behind the three stays **unplanned by design** — planning
it would spend bits on futures that steering will rewrite anyway.

## The loop

0. **SHOW the window.** Before #1 executes, the principal sees the three —
   ranked, one line each, priced where cost matters. An invisible ranking
   cannot be steered, and steering is the point. Invoked bare ("ka123n"),
   this skill does ONLY this: display the current window and stop.
1. **Execute #1.** Fully — gates, verification, commit. Done means done.
2. **Re-evaluate #2 and #3** against what #1's execution revealed and any
   steering that arrived. They earned their slots under old evidence; fresh
   evidence re-earns or replaces them.
3. **Slide**: old #2 becomes #1, old #3 becomes #2.
4. **Generate a new #3** from the backlog, the steering, and the discoveries —
   never by momentum.

## Ranking rules

- **EV per bit, not EV alone.** A free deterministic step that aims an
  expensive step outranks the expensive step. Under budget pressure this
  dominates: spend authored/local/deterministic bits first; spend judged or
  metered bits only where they multiply.
- **Steering re-ranks immediately.** A verdict, correction, or new constraint
  from the principal reorders the window the moment it lands — the window
  serves the mission as currently steered, not as previously planned.
- **Deadlines enter as evidence, not as panic**: a world-enforced date rises
  in rank as its runway shortens, and gets said out loud while it waits.
- **Dependencies are honest**: a step blocked on an unbuilt feed does not sit
  at #1 pretending; the feed takes the slot.
- **A discovered failure outranks planned progress.** A refuted claim, a
  broken gate, or a corrupted record takes #1 until repaired — compounding on
  a cracked base is negative EV at any speed.

## What Ka123n is NOT

- Not a backlog display: the principal sees the window, never the pile.
- Not a promise about step 4: there is no step 4 until the slide creates it.
- Not self-steering: the ranking is proposed; the principal's steering is the
  gradient it descends — which is WHY the window is always shown before work
  begins, and why a slide is announced, not silent.
