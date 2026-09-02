# Gate 15 — vizcheck

    order:  15. VERIFY, after cold-read and before the captures. A surface must
            be readable by a stranger before it is worth checking against pixels.
    forms:  skill · tool · agent
    ruled:  the operator, 2026-09-01 — full moon. The screenshot tool plus an
            agent that reads the pixels. Hook and code are inapplicable, not
            deferred.
    where:  the tool `coywolf-screenshot` exists on the SECOND MACHINE ONLY. The
            agent `vizcheck-reader` is deployed to `~/.claude/agents/` and
            copied here.

---

## The read

**Verify the intent in the RENDERED form, not in the code that should produce
it.** Code that should render correctly is a hypothesis. The pixels are the
evidence.

Two words carry the gate. *Intent* — does the result match what was wanted, not
merely "did the change land". *Rendered* — in the state the viewer will see:
deployed, built, refreshed, never a local pre-build proxy.

**The narrowest trigger in the suite, and that is a feature.** Across one day:
**12 N/A, 1 FIRED, 2 BLOCKED.**

Ten of the twelve cite the trigger, in two phrasings — *"UI/CSS/layout change"*
and *"a UI, CSS or layout change"*. **Two cite neither** and are bare: *"No UI"*
and *"No interface authored"*. Separately, **three of the twelve name authorship
explicitly, and two of those three are inside the ten** — the groups overlap, so
they do not sum to twelve. An earlier version of this paragraph listed 10, 3 and
1 as though they partitioned the set, which no reader could reconcile.

Authorship is the sharper test, and one N/A states it exactly:
*driving a browser is not authoring an interface.* Reading someone else's page
is not this gate. The suite reviewed merging it away on 2026-08-31 and kept it:
one firing moment is one gate.

**The BLOCKED rows are the honest ones.** One reads *"Artifact HTML written but
not published. The gate cannot run on an unrendered page"*; the other, *"Artifact
HTML written but not published or rendered — trigger fired, gate cannot run
until it ships."* That is the gate
refusing to grade a hypothesis. A written file is not a rendered surface, and a
gate that accepted the file would be checking the thing it exists to reject.

## The intent

Look at what the viewer will actually see, before claiming the visual works.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: intent vs. rendered, and the rung ladder — perceptual reading, then crop, then coordinate readback when placement must be exact | any authored interface |
| **tool** | `coywolf-screenshot` — headless capture, no TCC dependency. **SECOND MACHINE ONLY** | localhost and unauthenticated surfaces |
| **agent** | `vizcheck-reader` — receives the image and one sentence of intent, with NO build context | when the author cannot see their own render |

**Why the agent is not redundant, which gate 05 required me to answer.** No
existing agent reads pixels. `cold-reader` reads text artifacts and asks whether
a future agent would act wrongly from them; `refuter` attacks a claim. Neither
renders anything. And the specific failure here is not ignorance — it is that
**the author cannot look at their own render without seeing what they meant.**
An agent with no build context is the only reader that sees what is there.

**No hook and no code.** Nothing can pattern-match "did this achieve its
intent". A green check for that judgement would be the ritual this suite forbids.

**THE TOOL LIES, TWICE, AND BOTH DEFECTS ARE PROVEN.** `--window-size` does not
lay out at the requested width — it renders wider and CROPS, so **every
responsive check made with it is invalid**; clipping in the capture is not
evidence of a page bug. `--virtual-time-budget` does not advance the page clock
past first paint, so two captures of an animation are two captures of one
instant. The first cost an hour chasing a phantom overflow. Both are written
into the agent's brief, because the agent is the reader most likely to trust a
capture it did not take.

## Disproof

Refuted if this gate reports FIRED and the shipped surface is then found
visually wrong in a way a look would have caught.

Watchable, and the record shows the gate working in the harder direction: it
went BLOCKED twice rather than passing an unrendered page. A gate that will not
grade its own hypothesis is doing the job.

**The unclosed risk is the instrument, not the judgement.** A FIRED row rests on
a capture, and the capture tool is known to lie about width and about time. The
gate cannot currently distinguish "the layout is correct" from "the tool cropped
the evidence" without a control render. That is the real limit today.

**REVISIT** when the capture tool's two defects are fixed or replaced, or when
the tool exists on the machine that holds this repo — today it does not, so a
FIRED row here depends on a second machine being reachable.
