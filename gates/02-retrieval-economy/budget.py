#!/usr/bin/env python3
"""budget.py — gate 02's ENFORCEMENT form. Price the loop, then HOLD the price.

Credit: the spend cap is adapted from bajpainaman/solve's budget gating (its Step 0.6
and bin/budget-track, v0.5.0: caps checked between steps, halt at the cap). The
one-run-at-a-time lock below is this suite's own; solve has no equivalent.

Anything that spends model calls on the operator's account calls reserve()
BEFORE it spends. Two refusals, both loud:

  1. CONCURRENCY — one run at a time within one STATE DIRECTORY.

     READ THIS BEFORE TRUSTING THE WORD "MACHINES". Exclusion is exactly as wide
     as the filesystem holding COYWOLF_BUDGET_STATE, and nothing here can check
     that. As deployed on 2026-09-07 the Den and the laptop have SEPARATE local
     state directories, so each wins its own O_EXCL and cross-machine exclusion
     DOES NOT EXIST. That is survivable only because the harnesses that spend
     model calls all run on the Den. Point COYWOLF_BUDGET_STATE at one
     atomically-shared path on both hosts before claiming more, and note that a
     cloud-synced folder is NOT such a path. Found by the continuous adversary,
     which called the earlier docstring what it was: a claim with no mechanism.
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
  budget.py break                        # explicit, logged; NO timer ever breaks a lock
  budget.py cap <calls_per_day>
"""
import json, math, os, socket, sys, time, uuid

STATE = os.path.expanduser(os.environ.get("COYWOLF_BUDGET_STATE", "~/.coywolf/state"))
LEDGER = os.path.join(STATE, "budget.jsonl")
LOCK = os.path.join(STATE, "budget.lock")
CFG = os.path.join(STATE, "budget-config.json")
DEFAULT_CAP = 600


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
    # UTC, not local. REFUTED 2026-09-07: the day was matched against the
    # CALLER's local date, so two machines in different zones -- or one with a
    # drifted clock -- each believed a fresh cap window was open. The claim is
    # "across both machines", so the clock has to be shared too.
    day = time.strftime("%Y-%m-%d", time.gmtime())
    return sum(e["calls"] for e in (entries if entries is not None else _entries())
               if e.get("event") == "reserve" and str(e.get("ts", "")).startswith(day))


def _append(rec):
    os.makedirs(STATE, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def _pid_alive(pid):
    """Fail CLOSED: anything but a definitive "no such process" counts as ALIVE.

    REFUTED 2026-09-07 by the continuous adversary, score 8: the first version
    caught bare OSError, and PermissionError -- raised by os.kill(pid, 0) for a
    process owned by ANOTHER uid, e.g. a daemon or a launchd job -- is an
    OSError subclass. It reproduced this against pid 1: launchd is plainly
    alive, and the guard declared the lock free with no grace period at all.
    A liveness check on a guard must resolve ambiguity toward "still held".
    """
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False                 # the ONLY definitive dead answer
    except PermissionError:
        return True                  # it exists; we simply may not signal it
    except (ValueError, TypeError):
        return True                  # unreadable pid -> assume held
    except OSError:
        return True


def _drop_lock():
    """Remove the lock, tolerating another caller having removed it first.

    REFUTED 2026-09-07 (adversary pass 3): three of four threads reaping ONE
    dead lock raised a bare FileNotFoundError out of _held_by(), which main()
    does not catch — so the refusal arrived as a traceback instead of the clean
    diagnosable message this file's own doctrine requires. Every unlink of the
    lock goes through here.
    """
    try:
        os.unlink(LOCK)
        return True
    except FileNotFoundError:
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
    # REFUTED 2026-09-07 by the continuous adversary, score 8. The first version
    # broke any CLI lock older than six hours on ELAPSED TIME ALONE. The founding
    # incident this file cites is a ~900-call run, which can easily run past six
    # hours -- so the mitigation reintroduced the exact disaster. ELAPSED TIME IS
    # NOT LIVENESS. A lock we cannot prove dead is never broken automatically;
    # `budget.py break` is the explicit, logged, human decision.
    if h.get("holder", "inprocess") == "cli":
        return h
    if h.get("host") == socket.gethostname():
        if _pid_alive(h.get("pid")):
            return h
        if not _drop_lock():
            return None                      # another caller reaped it first
        _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "broke_dead_lock",
                 "calls": 0, "label": h.get("label", "?")})
        return None
    # A foreign host's liveness cannot be checked from here, so it is never
    # broken on a timer either. Same ruling, same reason.
    return h


def _acquire(token, label, calls, holder):
    """The ENTIRE mutual-exclusion primitive: O_EXCL, which either creates the
    lock or fails because someone else already did. Atomic on a local FS.

    REFUTED 2026-09-07 by the continuous adversary, score 9. The first version
    called _held_by() and THEN wrote the lock with a plain open(LOCK, "w") --
    classic check-then-act. It reproduced two concurrent `reserve` calls both
    succeeding in 4 of 5 trials, and 800 calls landing against a cap of 500.
    Every liveness and clock fix before this was correct and irrelevant: the
    file had no synchronisation at all, and the two harness processes it exists
    to gate are exactly the near-simultaneous callers that expose it.
    """
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as f:
        json.dump({"token": token, "label": label, "calls": calls,
                   "host": socket.gethostname(), "pid": os.getpid(),
                   "started": time.time(), "holder": holder}, f)
    return True


def reserve(calls, label, holder="inprocess"):
    if isinstance(calls, bool) or not isinstance(calls, int) or calls < 1 or calls > 100000:
        raise BudgetRefused("calls must be an int in 1..100000, got %r" % (calls,))
    label = str(label).strip()[:120] or "unlabelled"
    os.makedirs(STATE, exist_ok=True)
    token = uuid.uuid4().hex[:12]

    # 1. TAKE THE LOCK FIRST, atomically. Never inspect-then-write.
    if not _acquire(token, label, calls, holder):
        held = _held_by()                      # may clear a provably-dead same-host lock
        if held:
            raise BudgetRefused(
                "a run is already in flight — one at a time across all sessions. "
                "holder: %s on %s (pid %s), started %s. Wait, or `budget.py break` if you "
                "have checked it is dead."
                % (held.get("label"), held.get("host"), held.get("pid"),
                   time.strftime("%H:%M:%S", time.localtime(float(held.get("started", 0) or 0)))))
        if not _acquire(token, label, calls, holder):
            raise BudgetRefused("lost the race for the lock to another caller — try again")

    # 2. The cap is checked UNDER the lock, so read-compare-append is serialised.
    #    Checking it before acquiring was the second half of the same race.
    try:
        cap, spent = _cap(), spent_today()
        if spent + calls > cap:
            raise BudgetRefused(
                "daily cap: %d already reserved today, this run wants %d, cap is %d. "
                "Raise it deliberately with `budget.py cap N` — never silently."
                % (spent, calls, cap))
    except BaseException:
        _drop_lock()                       # never keep a lock for a run we refused
        raise
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "reserve",
             "calls": calls, "label": label, "token": token, "host": socket.gethostname()})
    return token


def release(token):
    try:
        with open(LOCK, encoding="utf-8") as f:
            h = json.load(f)
    except FileNotFoundError:
        return False
    if h.get("token") != token:
        raise BudgetRefused("that token does not hold the lock (holder: %s)" % h.get("label"))
    _drop_lock()
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "release", "calls": 0,
             "label": h.get("label", "?"), "token": token})
    return True


def main(argv):
    try:
        cmd = argv[1] if len(argv) > 1 else "status"
        if cmd == "status":
            held = _held_by()
            print("spent today: %d / cap %d" % (spent_today(), _cap()))
            print("state dir  : %s   (exclusion is exactly this wide)" % STATE)
            print("in flight  : %s" % ("%s on %s (pid %s)" % (held.get("label"), held.get("host"),
                  held.get("pid")) if held else "nothing"))
            return 0
        if cmd == "reserve":
            print(reserve(int(argv[2]), " ".join(argv[3:]), holder="cli"))
            return 0
        if cmd == "break":
            # A truncated lock is the case break EXISTS for: a process killed
            # between creating the file and finishing the write. The first
            # version parsed it inline and died on JSONDecodeError, leaving the
            # lock in place -- pushing the operator to an unlogged `rm`, which
            # is exactly the "explicit, logged" guarantee this command sells.
            if not os.path.exists(LOCK):
                print("no lock held")
                return 0
            try:
                h = json.load(open(LOCK, encoding="utf-8"))
            except Exception:
                h = {"label": "<unreadable lock file>", "host": "?", "pid": "?"}
            _drop_lock()
            _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "event": "broken_by_hand", "calls": 0, "label": h.get("label", "?")})
            print("BROKE the lock held by %r on %s (pid %s). Recorded."
                  % (h.get("label"), h.get("host"), h.get("pid")))
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
