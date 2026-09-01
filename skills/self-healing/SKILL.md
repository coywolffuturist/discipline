---
name: self-healing
description: When building any monitor / health-check / audit / cron / observer, design it to ACT, not just alert. Pattern — detect → attempt recovery → log to durable telemetry → escalate ONLY on persistent failure (after N recovery attempts) or a decision that genuinely needs a human. A monitor that just posts to a human channel and hopes someone acts is wrong-pattern; a cron that reports without acting is theater — wire it to act or kill it. Trigger: about to build a health-check / monitor / audit / cron / watcher.
---

# /self-healing — act, don't alert

The default action when a thing breaks is "try to fix it," not "tell a
human it broke." A human channel is a finite-attention sink: signal
routed there for a human to act on is signal that mostly won't be acted
on. Build substrate that corrects itself and escalates only what truly
needs a person.

## The pattern

1. **Detect** — observe the state change, drift, or failure.
2. **Attempt recovery** — restart the dead daemon, retry the request,
   reapply the patch, archive the stale artifact. This is the default
   response, not an afterthought.
3. **Log to durable telemetry** — every detect+recover cycle writes a
   structured line (JSONL/row). Trends become visible; the rules can
   improve from them.
4. **Escalate ONLY on:**
   - persistent failure after N recovery attempts (a genuine
     action-required signal),
   - a decision that actually needs human judgment (architectural,
     strategic, security, irreversible),
   - anything that costs MORE by staying silent than by interrupting
     (e.g. funds at risk).
5. **Close the loop** — escalation patterns feed back into the rules,
   so false escalations shrink over time.

## Anti-patterns

- ❌ Health monitor that posts to a chat channel hoping someone reads
   it — they mostly won't.
- ❌ Audit that files a proposal somewhere and hopes for review —
   either auto-apply within a safe allowlist, or surface it where
   decisions actually get made.
- ❌ "We'll add a manual review step" — every manual step not
   auto-handled is a future pothole.
- ❌ A cron that *reports* without *acting* — that's theater. Wire it
   to act, or kill it.

## Before shipping any monitor/audit/cron — answer:

1. What ACTION does it take when it detects a problem?
2. What's the recovery attempt?
3. What telemetry does it write so trends are visible?
4. What's the persistent-failure threshold that escalates?
5. If the answer to #1 is "post to a human channel" — STOP. Add real
   auto-remediation, or don't ship it.

## One-line summary

**Detect → recover → log → escalate-only-on-persistent-failure. A
monitor that only alerts a human is wrong-pattern; a cron that reports
without acting is theater.**
