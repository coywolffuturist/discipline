# Gate 14 — cold-read

    order:  14. VERIFY, after nomess and before vizcheck. Earlier there is no
            artifact to read; later it has already shipped.
    forms:  skill · agent
    where:  the `cold-reader` agent and the `cold-read` skill are installed on
            the machine this repo lives on — verified 2026-09-02 at
            `~/.claude/agents/cold-reader.md` and `~/.claude/skills/cold-read`.
            This gate can RUN here.

            An earlier version of this block said they were ABSENT here and the
            gate "permanently BLOCKED". That was true when written and false by
            the time it was read: the repo moved to this machine on 2026-09-01.
            A reader following it would have written BLOCKED for a gate that
            works — which is the "true when written, now false" failure this
            gate exists to catch, inside this gate's own header.

            The estate spans two hosts; a path resolves per-host and no file
            here should name one without saying which.
    ruled:  the operator, 2026-09-01 — full moon. Without a context-free reader
            the row is BLOCKED, not FIRED.

---

## The read

**Read the artifact as the agent who arrives with no context and cannot ask a
question.** Not "is this clear" — clarity is self-reported and correlates poorly
with correct action. The question is narrower: *what would a competent reader
DO wrongly on the strength of this?*

The failure this catches is not error. It is **text that is true, or was true,
and produces a wrong action anyway** — because it omits a condition the author
held in their head, or because it has quietly stopped being true.

Both halves happened on 2026-09-01, and both were caught by readers, not by this
gate:

- An auditor read "the deployed copy at `~/.claude/skills/...` matches its
  source", checked that path on the machine the repository lives on, found
  nothing, and reported the claim false. It was true — on the *other* machine.
  The sentence named neither.
- An agent evaluating the suite quoted a banner reading "neither hook is
  registered anywhere" and concluded it was documentation rather than mechanism.
  The banner had been true when written and false for weeks.

Both readers read exactly what was written and reasoned correctly to a wrong
conclusion. One omitted **which host**; the other omitted **as of when**.

So the read asks four questions, not one:

1. Would a competent reader **act** wrongly from this?
2. Does a claim depend on a **context the text never states** — which machine,
   which account, which environment?
3. Was this **true when written and now false**? Every self-critical note is a
   claim with a timestamp.
4. Does anything dead, retired or superseded **read as live**?

## The intent

Ship artifacts that survive their author, so a future agent gains a capability
from the text rather than inheriting a prohibition it cannot evaluate.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the four questions, applied to your own output | every ship |
| **agent** | `cold-reader` — spawned with no build context, read-only, reports what it would MISinterpret | non-trivial or outward-facing artifacts |

No hook **in this gate**: no pattern decides whether a stranger would act wrongly.

But one exists elsewhere and a cold reader found it: `cold-read-check.py` is
registered on the SECOND MACHINE on `PreToolUse[ExitPlanMode]` and it DENIES —
raw JSON blobs, implementation-before-why openings, six or more acronyms. It is a
narrow syntactic proxy, not this gate, and it is not owned here. Named so that a
sweep does not retire it as an orphan, and so a stranger denied by it on that host
is not hunting a phantom.

No code form: same reason as the hook.

**An author re-reading their own work is not a cold read.** Without a
context-free reader the row is BLOCKED. Across one day this gate recorded 35
FIRED, 3 N/A and zero BLOCKED — with zero cold-readers spawned. Under this
standard nearly all 35 were BLOCKED, and the two misses above are what that
overstatement cost.

## Disproof

Refuted if a cold-reader pass runs on an artifact, reports no misinterpretation,
and a real reader then acts wrongly from that same artifact for a reason the
pass had the access and the brief to catch.

The narrower disproof for the four questions: run them against the two artifacts
that fooled readers on 2026-09-01. If they do not surface the missing host and
the expired banner, this revision fixed nothing. **That test is owed and unrun.**

**REVISIT** if the enforcement proves insufficient — this gate has no hook, so it
relies on honest self-report, which is exactly the dependency that left gate 08
blocked five times before it got a form.
