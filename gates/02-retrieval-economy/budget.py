#!/usr/bin/env python3
"""budget.py — gate 02's ENFORCEMENT form. Price the loop, then HOLD the price.

Anything that spends model calls on the operator's account calls reserve()
BEFORE it spends. Two refusals, both loud:

  1. CONCURRENCY — one run at a time, across every session and both machines.
     On 2026-09-07 two LongMemEval runs were launched in parallel (~900 Opus
     calls on his Max account). The session wall then killed a 420-call run
     that bought nothing.
  2. DAILY CAP — refuse when today's reservations would exceed the cap.

WHY THIS IS NOT A HOOK. Gate 02's hook and code forms were DELETED after three
refutations for false positives (see DELETED.md in this directory): a guard that
reads command text is guessing at what will spend. This one is called BY the
spender, with the number it is about to spend, so it never guesses.

A RESERVATION IS SPENT. release() frees the lock; it does NOT refund the calls.
A run that dies at q120 of 420 still counted 420. That is deliberate: the
conservative direction is the one that cannot overspend his account.

KNOWN LIMIT, stated rather than hidden: the day boundary is the LOCAL clock,
which the constrained party can set. Acceptable for a token budget; it would NOT
be acceptable for settlement authority, which is on block time.

  budget.py status
  budget.py reserve <calls> <label>   -> prints a token on stdout; exit 1 = REFUSED
  budget.py release <token>
  budget.py cap <calls_per_day>
"""
import json, math, os, socket, sys, time, uuid

STATE = os.path.expanduser(os.environ.get("COYWOLF_BUDGET_STATE", "~/.coywolf/state"))
LEDGER = os.path.join(STATE, "budget.jsonl")
LOCK = os.path.join(STATE, "budget.lock")
CFG = os.path.join(STATE, "budget-config.json")
DEFAULT_CAP = 600
STALE_FOREIGN_LOCK = 6 * 3600


class BudgetRefused(Exception):
    pass


class BudgetCorrupt(Exception):
    """The ledger could not be read. FAIL CLOSED — never treat it as zero.

    On 2026-09-05 a NaN reached an accumulator and reopened a whole day's cap,
    because `nan + 25 > 25` is False. Every number that reaches the comparison
    is validated here, not only the inputs.
    """


def _cap():
    try:
        with open(CFG) as f:
            v = json.load(f).get("daily_call_cap", DEFAULT_CAP)
    except FileNotFoundError:
        return DEFAULT_CAP
    except Exception as e:
        raise BudgetCorrupt("budget-config.json unreadable: %s" % e)
    if not isinstance(v, int) or isinstance(v, bool) or v < 1:
        raise BudgetCorrupt("daily_call_cap is not a positive int: %r" % (v,))
    return v


def _entries():
    if not os.path.exists(LEDGER):
        return []
    out = []
    for n, line in enumerate(open(LEDGER, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception as ex:
            raise BudgetCorrupt("ledger line %d is not JSON: %s" % (n, ex))
        c = e.get("calls", 0)
        if isinstance(c, bool) or not isinstance(c, (int, float)) or not math.isfinite(c) or c < 0:
            raise BudgetCorrupt("ledger line %d has a non-finite calls value: %r" % (n, c))
        out.append(e)
    return out


def spent_today(entries=None):
    day = time.strftime("%Y-%m-%d")
    return sum(e["calls"] for e in (entries if entries is not None else _entries())
               if e.get("event") == "reserve" and str(e.get("ts", "")).startswith(day))


def _append(rec):
    os.makedirs(STATE, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def _held_by():
    """Return the live holder dict, or None. Breaks a lock that provably died."""
    try:
        with open(LOCK, encoding="utf-8") as f:
            h = json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return {"label": "<unreadable lock>", "host": "?", "pid": "?", "started": 0}
    # A CLI hold has NO live process behind it: `budget.py reserve` prints a token
    # and exits, so its pid is dead one millisecond later. Breaking on a dead pid
    # is correct ONLY for an in-process holder, which lives as long as the run.
    # Measured 2026-09-07: without this distinction a CLI hold self-invalidated and
    # a 20-call gate started anyway, spending his quota. The first bait missed it
    # because it reserved in-process, where the pid stays alive.
    if h.get("holder", "inprocess") == "cli":
        if time.time() - float(h.get("started", 0)) > STALE_FOREIGN_LOCK:
            os.unlink(LOCK)
            _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": "broke_stale_cli_lock",
                     "calls": 0, "label": h.get("label", "?")})
            return None
        return h
    if h.get("host") == socket.gethostname():
        if _pid_alive(h.get("pid")):
            return h
        os.unlink(LOCK)                      # same host, process is gone: safe to break
        _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": "broke_dead_lock",
                 "calls": 0, "label": h.get("label", "?")})
        return None
    if time.time() - float(h.get("started", 0)) > STALE_FOREIGN_LOCK:
        os.unlink(LOCK)                      # another host, older than 6h
        _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": "broke_stale_foreign_lock",
                 "calls": 0, "label": h.get("label", "?")})
        return None
    return h


def reserve(calls, label, holder="inprocess"):
    if isinstance(calls, bool) or not isinstance(calls, int) or calls < 1 or calls > 100000:
        raise BudgetRefused("calls must be an int in 1..100000, got %r" % (calls,))
    label = str(label).strip()[:120] or "unlabelled"
    held = _held_by()
    if held:
        raise BudgetRefused(
            "a run is already in flight — one at a time across all sessions. "
            "holder: %s on %s (pid %s), started %s. Wait, or release it if you know it is dead."
            % (held.get("label"), held.get("host"), held.get("pid"),
               time.strftime("%H:%M:%S", time.localtime(float(held.get("started", 0) or 0)))))
    cap, spent = _cap(), spent_today()
    if spent + calls > cap:
        raise BudgetRefused(
            "daily cap: %d already reserved today, this run wants %d, cap is %d. "
            "Raise it deliberately with `budget.py cap N` — never silently."
            % (spent, calls, cap))
    token = uuid.uuid4().hex[:12]
    os.makedirs(STATE, exist_ok=True)
    with open(LOCK, "w", encoding="utf-8") as f:
        json.dump({"token": token, "label": label, "calls": calls, "host": socket.gethostname(),
                   "pid": os.getpid(), "started": time.time(), "holder": holder}, f)
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": "reserve", "calls": calls,
             "label": label, "token": token, "host": socket.gethostname()})
    return token


def release(token):
    try:
        with open(LOCK, encoding="utf-8") as f:
            h = json.load(f)
    except FileNotFoundError:
        return False
    if h.get("token") != token:
        raise BudgetRefused("that token does not hold the lock (holder: %s)" % h.get("label"))
    os.unlink(LOCK)
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": "release", "calls": 0,
             "label": h.get("label", "?"), "token": token})
    return True


def main(argv):
    try:
        cmd = argv[1] if len(argv) > 1 else "status"
        if cmd == "status":
            held = _held_by()
            print("spent today: %d / cap %d" % (spent_today(), _cap()))
            print("in flight  : %s" % ("%s on %s (pid %s)" % (held.get("label"), held.get("host"),
                  held.get("pid")) if held else "nothing"))
            return 0
        if cmd == "reserve":
            print(reserve(int(argv[2]), " ".join(argv[3:]), holder="cli"))
            return 0
        if cmd == "release":
            print("released" if release(argv[2]) else "no lock held")
            return 0
        if cmd == "cap":
            os.makedirs(STATE, exist_ok=True)
            json.dump({"daily_call_cap": int(argv[2])}, open(CFG, "w"))
            print("daily cap now %d calls" % int(argv[2]))
            return 0
        print(__doc__)
        return 2
    except BudgetRefused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 1
    except BudgetCorrupt as e:
        print("REFUSED (fail-closed): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
