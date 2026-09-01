---
name: 95-percent-rule
description: Bayesian check before any "done / ready / verified / safe / clean / it works / fixed / no regressions" claim. Define success ONCE at the user-outcome level before verifying. Set explicit prior. Update posterior with each observation — failures count, "intentional behavior" does NOT exempt. Do NOT claim ready until P(success | evidence) ≥ 0.95. Use whenever about to declare a workstream done, OR when user asks "are you sure / did you check / did you break anything / is it ready?" Also user shorthand ".95".
---

# The 95% Rule

Don't claim ready until **P(success | evidence) ≥ 0.95** on the user-visible outcome.

## Step 1 — Define success at user-outcome level (BEFORE verifying)

Write one sentence: what does the user want from this workstream? This is the **fixed denominator** — don't redefine midway to match what you happened to verify.

| Bad (subsystem) | Good (user-outcome) |
|---|---|
| "The migration script ran without errors" | "Every row from the old table is queryable in the new schema" |
| "No references to the deprecated API remain in code" | "No request path hits the removed endpoint in production" |
| "The new service starts up" | "A user request completes end-to-end through the new service, including across a restart" |

If you can't write the user-outcome sentence in plain language, you haven't earned the right to verify anything yet.

## Step 2 — Set an explicit prior

P(success) RIGHT NOW, before further verification. Be honest.

- Historical rate: fraction of comparable cases that succeeded recently
- Greenfield untested code: ~30-50%
- Well-tested with prior wins: ~70-85%
- Known unfixed failure modes pull it down

"Should be fine" is not a prior. It's evasion.

## Step 3 — Gather evidence (four-criterion check)

1. **Ran it.** Executed the actual user-outcome code path against representative input with a real interpreter/runtime — not "AST parses" / "diff looks right" / "comment is correct." Two specifics:
   - **Test-outcome claims** ("tests pass / suite green / no regressions") require running the test command AND quoting its real summary as the receipt — "657 passed, 1 skipped; exit 0," never an unquoted "passes." If you didn't run it, the honest sentence is "I did not run the suite."
   - **"Ready to ship"** requires executing the changed path once and observing runtime — not that it merely compiles.
2. **Enumerated** failure modes for the user-outcome (not your favorite subsystem).
3. **Closed each risk with an artifact** — grep output, query result, screenshot, log line, exit code, file readback.
4. **Named the unverified residue** explicitly.

## Step 4 — Update the posterior

| Observation | Update |
|---|---|
| Successful end-to-end cycle of the user-outcome | + large |
| Failed cycle for ANY reason (including "intentional behavior") | − large |
| Smoke test / unit test pass | + small |
| Subsystem verified that's necessary-but-not-sufficient | + small |
| AST parse / "diff looks right" / code review of self | + minimal (proves syntax, not correctness) |
| Untested code path | residue — no update either direction |
| Failure rate ≥ 10% over recent cycles | posterior ceiling ~0.90 regardless of positives |

## Step 5 — Decide

- **Posterior ≥ 0.95:** state the math + evidence trail + residue, then claim ready.
- **Posterior < 0.95:** do NOT claim ready. Either close more gaps OR surface explicitly: *"P(success | evidence) = X. Distance from 0.95: Y. Specific blockers: <list>. Greenlight to proceed with known shortfall?"*

## Calibration anchors (don't shift mid-claim)

- **"Intentional product behavior" does NOT exempt.** If a cascade / retry-exhaustion / auto-pause / sibling-block prevented the user's task from completing, it counts as a failure against the user-outcome. Don't draw a self-serving line between "infrastructure bug" and "feature behaving correctly."
- **Don't redefine success.** Definition is fixed at the START. Drift is the bug.
- **Confidence is gated by the WORST contributing failure mode, not the BEST verified subsystem.**
- **When asked "are you confident / did you check / did you break anything?":** answer with the posterior + evidence, not a feeling.

## The one-line summary

**Confidence is gated by the worst failure mode, not the best verified subsystem. Evidence beats assertion.**
