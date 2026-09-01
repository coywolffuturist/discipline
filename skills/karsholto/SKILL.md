---
name: karsholto
description: The Karpathy + Sholto filter — two equal forces, one optimum. Karpathy = minimum-viable restraint (smallest brick, no cathedral, no N-layers-ahead). Sholto = eval-driven leadership (build the trusted eval FIRST; the eval-that-matters is the only currency; never trust an unvalidated number). Their intersection: the smallest brick that PROVES the wall stands. Run before any architecture, substrate, abstraction, multi-step plan (>3 steps), or "once X exists we can Y" speculation — and before trusting any result enough to build on it. Shorthand "karsholto".
---

# Karsholto filter

Two forces, equal weight, one optimum. **Karpathy** pulls toward *less*
(build the minimum). **Sholto** pulls toward *proven* (let a trusted
eval lead). Neither alone is right — Kar without Sholto ships fast junk
you never validate; Sholto without Kar gold-plates eval cathedrals N
layers deep before any result. The move is the point where both hold at
once: **the smallest brick that proves the wall stands.** Solve them
jointly — *minimize* (Kar) *subject to* eval-proven (Sholto) — not in
sequence.

## Karpathy lens — minimum-viable restraint

- Smallest concrete failure observed → build the minimum thing that
  prevents it. Nothing for hypothetical futures.
- Build for the N you need, not the N you imagine.
- Code first; design doc second, if at all — today's doc is wrong in
  ways unknown today. Premature architecture is premature optimization.

## Sholto lens — eval-driven leadership

- **Build the eval BEFORE the thing it evaluates.** The eval leads the
  investigation; it is not bolted on at the end.
- **The eval-that-matters is the only currency** — the real test
  (held-out / out-of-sample / a fresh case), never an in-sample or
  unvalidated number. Be excited by *nothing* until it speaks.
- **One trusted instrument, reused** — not a pile of ad-hoc one-offs,
  which breed bugs and let inflation hide.
- Pass/fail/measurable. Architecture follows from data, not data from
  architecture.

> *Distinct from .95 and substrate-search — don't let it dissolve into
> them.* substrate-search is Kar's neighbor (don't build dupes); **.95
> is the done-time posterior gate.** Karsholto's niche is the
> **design-time synthesis**: the minimum *eval-backed* brick, with the
> trusted eval stood up *first* so it can lead.

## The two-sided gate (answer BOTH before drafting — eval first)

1. **(Sholto) What's the eval, and is it built + trusted FIRST?** Name
   the real pass/fail test. If the instrument doesn't exist, build it
   before the thing.
2. **(Sholto) What's the only currency here?** The number that would
   actually settle this. Refuse to trust anything weaker.
3. **(Kar) What's the smallest brick?** The minimum the concrete
   failure demands — nothing for hypothetical futures.
4. **(Kar) What gets cut?** Everything else → "future direction if
   proven," not proposed for execution.
5. **(Both) Architecture or a fix?** Ship the fix; the architecture is
   residue — and it still has to pass the eval.

**Imbalance check:** answer 3–4 but not 1–2 → Kar-only (fast +
unvalidated). Answer 1–2 but keep expanding the build → Sholto-only
(eval cathedral). Both halves must clear.

## Anti-patterns this catches

- ❌ (Kar) Comprehensive design doc / multiple arch changes for one
  failure; "once X exists we can Y" chains; substrate ahead of runtime.
- ❌ (Sholto) Eval built *last* as a distillation; excitement over an
  in-sample number before the held-out test; a pile of throwaway eval
  scripts instead of one trusted instrument; "validated / it works" on
  an unvalidated cycle.

## One-line summary

**Build the smallest brick — and stand up the trusted eval first, so
the brick must PROVE the wall stands. Minimum and proven, or it doesn't
ship.**
