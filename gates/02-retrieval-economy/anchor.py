#!/usr/bin/env python3
"""anchor.py — gate 02's CHECKPOINT-AND-PAUSE form. Clip in before the hard moves.

The operator's teaching, 2026-10-03, from the man who created LAPD SWAT and trained a
Navy SEAL sniper team: SLOW IS FAST AND FAST IS SLOW. A job that rushes at its budget
line breaks something, and fixing what was broken costs more than the rush saved.
His picture for this tool: a climber who clips in and hammers protection, so that a slip
ends at the last anchor, not at the bottom of the mountain.

What it replaced: on 2026-10-02 parallel jobs ran the weekly limit to 99% with no
warning; on 2026-10-03 a 70-run check loop was launched with no stated price. My first
proposal, "switch to a cheaper model near the cap", was REJECTED by him: a weaker model
writes work a stronger one must redo. So there is no downgrade here. Ever.

Four acts, each called BY THE JOB (not guessed from command text; see DELETED.md):

  price      before starting: the estimated cost as a share of the weekly limit, and the
             model the job runs on. The job does NOT start without --approved (= he said
             yes) when its TOTAL budget passes the ask line (default 2%, his figure), when
             today's unapproved budgets across ALL jobs would pass twice that line, or when
             it would cut into the conversation reserve. Re-pricing a job ADDS to its budget
             and never moves its baseline, so a budget cannot be laundered by re-pricing.
  check      between units: read the meter. Exit 2 = PAUSE NOW at this anchor: the job spent
             its budget, the week reached the reserve (default 85% used: the last 15% is
             kept so he can always talk to his agent), the meter is unreadable, or the job's
             state is missing or corrupt. Every failure pauses; nothing fails open.
  checkpoint after each finished unit: what is done, what comes next. The resume note.
  resume     print the last checkpoint and the job's model, so it restarts on the SAME model.

The meter is the provider's own rate-limit headers (anthropic-ratelimit-unified-7d-
utilization etc.), read with one tiny call. They report whole percents. A budget is
enforced at the first whole percent at or above it, minus one when that still leaves at
least 1% (so 2.5% pauses at 2% spent, 1% pauses at 1%, 0.5% pauses at 1%: a budget under
1% cannot be enforced finer than the meter's own step).

  anchor.py price <job> <est_week_pct> [--model M] [--approved]   exit 3 = ASK HIM FIRST
  anchor.py check <job>                                           exit 2 = PAUSE AT THIS ANCHOR
  anchor.py checkpoint <job> <done> <next>
  anchor.py resume <job>
  anchor.py meter                                                 print the meter

Meter source: $COYWOLF_METER_CMD if set (a command that exits 0 and prints JSON
{"week_pct": .., "session_pct": .., "week_reset": <epoch of the weekly reset>}, each pct 0 to 100); otherwise one API call
with $CLAUDE_CODE_OAUTH_TOKEN. Anything else is an unreadable meter, and an unreadable
meter refuses (price) or pauses (check): a job that cannot see the meter cannot know it is safe.
"""
import contextlib, fcntl, json, math, os, subprocess, sys, time, urllib.request, urllib.error

STATE = os.path.expanduser(os.environ.get("COYWOLF_BUDGET_STATE", "~/.coywolf/state"))
DIR = os.path.join(STATE, "anchors")
DAY = 86400


def _setting(name, default):
    """An override must be a finite percent in (0, 100]; anything else refuses to run (a NaN once switched the ask line off)."""
    v = os.environ.get(name, default)
    try:
        x = float(v)
    except ValueError:
        x = float("nan")
    if not math.isfinite(x) or x <= 0 or x > 100:
        sys.stderr.write("REFUSED: %s=%r is not a percent in (0, 100]\n" % (name, v))
        sys.exit(3)
    return x


ASK_PCT = _setting("COYWOLF_ASK_PCT", "2")              # his figure, 2026-10-03
RESERVE_USED_PCT = _setting("COYWOLF_RESERVE_AT", "85")  # last 15% kept for talking to him


@contextlib.contextmanager
def _locked():
    """One price/checkpoint at a time per state folder: the daily cap is read-then-write, and 8 parallel prices
    once all saw a total of zero (refuter, 2026-10-03). Held across the meter read on purpose."""
    os.makedirs(DIR, exist_ok=True)
    with open(os.path.join(DIR, ".lock"), "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


class MeterUnavailable(Exception):
    pass


def _pct(v, what):
    """A meter value is a finite percent in [0, 100]; anything else is an unreadable meter."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        raise MeterUnavailable("%s is not a number" % what)
    if not math.isfinite(x) or x < 0 or x > 100:
        raise MeterUnavailable("%s=%r is not a percent in [0, 100]" % (what, v))
    return x


def _period(v):
    """The provider's own week id: the epoch second its weekly window resets. A reset is READ, never inferred from
    the meter falling (refuter 2026-10-03: inference missed a reset when the job was priced at 0%, and a dip in a
    rolling figure would have laundered a budget)."""
    try:
        x = int(float(v))
    except (TypeError, ValueError):
        raise MeterUnavailable("weekly reset time missing")
    if x <= 0:
        raise MeterUnavailable("weekly reset time %r is not an epoch" % (v,))
    return x


def meter():
    """{'week': pct, 'session': pct} from the provider's headers. Raises MeterUnavailable."""
    cmd = os.environ.get("COYWOLF_METER_CMD")
    if cmd:
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        except Exception as e:
            raise MeterUnavailable("COYWOLF_METER_CMD failed: %s" % str(e)[:120])
        if r.returncode != 0:
            raise MeterUnavailable("COYWOLF_METER_CMD exited %d" % r.returncode)
        try:
            d = json.loads(r.stdout)
        except ValueError:
            raise MeterUnavailable("COYWOLF_METER_CMD printed no JSON")
        if not isinstance(d, dict):
            raise MeterUnavailable("COYWOLF_METER_CMD printed no JSON object")
        return {"week": _pct(d.get("week_pct"), "week_pct"), "session": _pct(d.get("session_pct"), "session_pct"),
                "period": _period(d.get("week_reset"))}
    tok = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not tok:
        raise MeterUnavailable("no COYWOLF_METER_CMD and no CLAUDE_CODE_OAUTH_TOKEN")
    body = json.dumps({"model": "claude-haiku-4-5-20251001", "max_tokens": 1,
                       "system": "You are Claude Code, Anthropic's official CLI for Claude.",
                       "messages": [{"role": "user", "content": "."}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "Authorization": "Bearer " + tok, "anthropic-version": "2023-06-01",
        "anthropic-beta": "oauth-2025-04-20", "content-type": "application/json"})
    try:
        h = urllib.request.urlopen(req, timeout=30).headers
    except urllib.error.HTTPError as e:
        h = e.headers
    except Exception as e:
        raise MeterUnavailable(str(e)[:120])
    if h is None:
        raise MeterUnavailable("no headers")
    # the headers carry a fraction 0..1; convert, then validate as a percent
    try:
        wk = float(h["anthropic-ratelimit-unified-7d-utilization"])
        ss = float(h["anthropic-ratelimit-unified-5h-utilization"])
    except (TypeError, KeyError, ValueError):
        raise MeterUnavailable("rate-limit headers missing")
    return {"week": _pct(100 * wk, "7d-utilization"), "session": _pct(100 * ss, "5h-utilization"),
            "period": _period(h.get("anthropic-ratelimit-unified-7d-reset"))}


def _path(job):
    if not job or "/" in job or job.startswith(".") or job.startswith("-"):
        raise ValueError("bad job name %r" % job)
    return os.path.join(DIR, job + ".json")


def _load(job):
    try:
        return json.load(open(_path(job)))
    except FileNotFoundError:
        return None


def _save(job, rec):
    os.makedirs(DIR, exist_ok=True)
    tmp = "%s.%d.tmp" % (_path(job), os.getpid())
    json.dump(rec, open(tmp, "w"), indent=1)
    os.replace(tmp, _path(job))


def _unapproved_today(now):
    """Sum of budgets priced WITHOUT his yes in the last 24h, across all jobs (splitting a job stays visible)."""
    total = 0.0
    if not os.path.isdir(DIR):
        return total
    for f in os.listdir(DIR):
        if not f.endswith(".json"):
            continue
        fp = os.path.join(DIR, f)
        try:
            rec = json.load(open(fp))
            for p in rec.get("pricings", []):
                if not p.get("approved") and now - float(p.get("at", 0)) < DAY:
                    total += float(p.get("est", 0))
        except Exception:
            # an unreadable record counts against the allowance, never for it, but only while it is recent:
            # a stale corrupt file must not block every job forever
            try:
                if now - os.path.getmtime(fp) < DAY:
                    total += ASK_PCT
            except OSError:
                pass
    return total


def price(job, est_pct, approved=False, model=None, read=meter, now=None):
    """Exit codes: 0 = go, 3 = ask him first. Never starts a job it cannot see the meter for."""
    with _locked():
        return _price(job, est_pct, approved, model, read, now)


def _price(job, est_pct, approved, model, read, now):
    now = now or time.time()
    try:
        est = float(est_pct)
    except (TypeError, ValueError):
        return 3, "ASK HIM FIRST: the estimate %r is not a number." % (est_pct,)
    if not math.isfinite(est) or est <= 0 or est > 100:
        return 3, "ASK HIM FIRST: an estimate must be a percent above 0 and at most 100 (got %r)." % (est_pct,)
    try:
        rec = _load(job) or {"job": job, "checkpoints": [], "pricings": []}
        prior = float(rec.get("budget_pct", 0))
    except ValueError:
        raise
    except Exception as e:
        return 3, "ASK HIM FIRST: '%s' has an unreadable record (%s)." % (job, str(e)[:80])
    if not math.isfinite(prior):
        return 3, "ASK HIM FIRST: '%s' has a corrupt budget." % job
    m = read()
    if "baseline_week" in rec and rec.get("period") != m["period"]:
        # the provider's week reset since this job was priced (its own reset time changed): a new period starts
        # from zero. Same period = same baseline, however the meter moved.
        prior = 0.0
        rec.pop("baseline_week")
        rec["period_reset_at"] = now
    rec["period"] = m["period"]
    total = prior + est
    if not approved:
        if total > ASK_PCT:
            return 3, ("ASK HIM FIRST: '%s' would total %.1f%% of the week, above the %.1f%% line. "
                       "Show him the price and the plan; rerun with --approved only after he says yes." % (job, total, ASK_PCT))
        if _unapproved_today(now) + est > 2 * ASK_PCT:
            return 3, ("ASK HIM FIRST: today's unapproved jobs would total over %.1f%% of the week. "
                       "Many small jobs are one big job." % (2 * ASK_PCT))
    if m["week"] + est > RESERVE_USED_PCT:
        return 3, ("ASK HIM FIRST: '%s' (%.1f%%) would cut into the conversation reserve "
                   "(week at %.0f%%, reserve starts at %.0f%%)." % (job, est, m["week"], RESERVE_USED_PCT))
    if "baseline_week" not in rec:
        rec["baseline_week"] = m["week"]              # set ONCE: re-pricing never resets what was spent
    if model:
        rec["model"] = model
    rec["budget_pct"] = total
    rec.setdefault("pricings", []).append({"at": now, "est": est, "approved": bool(approved)})
    _save(job, rec)
    return 0, "GO: '%s' budget now %.1f%% (week at %.0f%%)" % (job, total, m["week"])


def check(job, read=meter):
    """Exit codes: 0 = keep climbing, 2 = PAUSE at this anchor. Every failure pauses."""
    try:
        rec = _load(job)
        if not rec or "budget_pct" not in rec or "baseline_week" not in rec:
            return 2, "PAUSE: '%s' was never priced (or its record is incomplete). Price it first." % job
        budget, base = float(rec["budget_pct"]), float(rec["baseline_week"])
        if not (math.isfinite(budget) and math.isfinite(base)):
            return 2, "PAUSE: '%s' has a corrupt record." % job
        m = read()
    except MeterUnavailable as e:
        return 2, "PAUSE: meter unreadable (%s). A job that cannot see the meter cannot know it is safe." % e
    except Exception as e:
        return 2, "PAUSE: '%s' state unreadable (%s)." % (job, str(e)[:100])
    if rec.get("period") != m["period"]:
        # LATCHED by construction: the stored week id differs from the provider's until the job is priced again
        return 2, "PAUSE: the week reset since '%s' was priced. Price it again for the new week." % job
    spent = m["week"] - base
    if spent < 0:
        return 2, "PAUSE: the meter fell below '%s's baseline inside one week; it cannot be trusted." % job
    edge = max(math.ceil(budget) - 1, 1) if budget < 3 else budget
    if spent >= edge:
        return 2, "PAUSE: '%s' has spent ~%.0f%% of its %.1f%% budget. Checkpoint, stop, resume on the same model." % (job, spent, budget)
    if m["week"] >= RESERVE_USED_PCT:
        return 2, "PAUSE: the week is at %.0f%%; the last %.0f%% is kept for talking to him." % (m["week"], 100 - RESERVE_USED_PCT)
    return 0, "CLIMB: '%s' spent ~%.0f%% of %.1f%% (week %.0f%%, session %.0f%%)" % (job, spent, budget, m["week"], m["session"])


def checkpoint(job, done, nxt):
    with _locked():
        rec = _load(job) or {"job": job, "checkpoints": []}
        rec.setdefault("checkpoints", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "done": done, "next": nxt})
        _save(job, rec)
    return 0, "anchored: %s" % done


def resume(job):
    rec = _load(job)
    if not rec or not rec.get("checkpoints"):
        return 1, "no checkpoint for '%s'" % job
    c = rec["checkpoints"][-1]
    return 0, "RESUME '%s' on the same model (%s). Last anchor %s. Done: %s. Next: %s" % (
        job, rec.get("model") or "model not recorded: use the one it was priced for", c["at"], c["done"], c["next"])


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 1
    cmd = argv[1]
    try:
        if cmd == "meter":
            print(json.dumps(meter())); return 0
        if cmd == "price":
            job, est, rest = argv[2], argv[3], argv[4:]
            model = rest[rest.index("--model") + 1] if "--model" in rest else None
            if model is not None and model.startswith("-"):
                raise ValueError("--model needs a model name, got %r" % model)
            rc, msg = price(job, est, approved="--approved" in rest, model=model)
        elif cmd == "check":
            rc, msg = check(argv[2])
        elif cmd == "checkpoint":
            rc, msg = checkpoint(argv[2], argv[3], argv[4])
        elif cmd == "resume":
            rc, msg = resume(argv[2])
        else:
            print(__doc__); return 1
    except MeterUnavailable as e:
        print("REFUSED: meter unreadable (%s); nothing starts blind." % e, file=sys.stderr)
        return 2 if cmd == "check" else 3
    except (IndexError, ValueError) as e:
        print("usage error: %s" % e, file=sys.stderr)
        return 2 if cmd == "check" else 1
    print(msg)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
