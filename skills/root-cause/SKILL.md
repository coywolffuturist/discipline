---
name: root-cause
description: Failure-phase gate — when something breaks, fix the LOWEST broken layer, never the symptom. Ladder: source-of-truth → substrate → implementation → pipeline → outcome. Per layer — reproduce the failure as a deterministic test BEFORE patching (Sholto: that red test defines done), smallest fix (Karpathy), same test green to ascend. Third leg of the triad (.95 + root-cause + karsholto). Trigger: a subsystem/tool fails, patches keep moving the failure without fixing the outcome, or about to blame a remembered cause. Shorthand "root-cause".
---

# /root-cause — act at the right depth

A fix at the wrong depth produces false confidence — the foundation
stays broken, the next bug surfaces, the cycle repeats. Find the
lowest broken layer; fix there; prove it; ascend.

## When to invoke

- A subsystem, tool, test, or daemon fails or misbehaves.
- A patch didn't fix it and you're about to dispatch patch #2.
- About to blame a cause recalled from memory.
- A problem surfaces mid-build, or the `discipline` triad fires.

## The ladder

Walk bottom-up. Don't start where the symptom showed — most broken
stacks have ONE broken layer, and the first mismatch going up is the
bug. Lock each layer before judging the one above:

1. **Source-of-truth** — what do the upstream docs name as canonical?
2. **Substrate** — does the code's data source match? Mismatch →
   STOP: replace the substrate, not the layer above.
3. **Implementation** — given correct substrate, is it read correctly?
4. **Pipeline** — does orchestration call it correctly?
5. **Outcome** — does the user-visible output match?

Patches above an unverified layer are wasted.

## Per-layer protocol

At each rung, in order:

1. **Eval before everything (Sholto).** Before citing memory, before
   patching: run the deterministic test that reproduces the CURRENT
   failure. It's both diagnosis and acceptance test — red now, its
   green defines done. No test exists for this surface? Build the
   smallest one first. Memory is a hypothesis source; the test is the
   conclusion.
2. **Trust the eval before its verdict.** Can the outcome fail while
   the test passes (blind spot), or succeed while it fails (noise)?
   Either → fix the test first.
3. **Read before write.** Read the failing source line; reproduce in
   isolation; capture stderr + return code + signal; hypothesis from
   code, THEN fix. Banned: "route around", "fall back", "alternate path".
4. **Adinv + Karpathy-minimum brick.** "Am I about to relax a
   deliberately-strict calibration?" Then the smallest patch that
   proves the layer — not the cathedral.
5. **Same eval, now green (Sholto).** Re-run the step-1 test —
   red → green on THE SAME test is the proof. Evidence invented after
   the fix is goalpost-moving. Ascend only at ≥.85 posterior.

## Supporting disciplines

- **Stop before building forward.** Problem surfaced while building
  X? Pause X; resolve first — building on unverified substrate caps
  X's confidence at the substrate's. Orthogonal → tracked side-task.
  Fix needs NEW substrate → `substrate-search` fires next.
- **Validators fire exactly when the outcome breaks.** Step 2's
  blind-spot/noise test, applied to any test suite you spec.

## Self-check

- Tool failed? Build/run the failing test BEFORE memory, BEFORE code.
- Do I have a red test that defines "fixed"? If not, I'm guessing.
- About to patch? Which rung — and is the one below verified?
- Fix #2 for the same outcome? Stop. Walk the ladder from rung 1.
- Claiming fixed? Same test, now green — not new evidence.

## Cross-references

- `95-percent-rule` — grades the posterior at CLAIM time; root-cause
  forces the eval to exist at BUILD time.
- `karsholto` — Sholto = steps 1/2/5, Karpathy = step 4.
- `adversarial-inverse` — the pre-patch audit in step 4.
- `nomess` — sweeps residue after the fix lands.
