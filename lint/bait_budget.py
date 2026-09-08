#!/usr/bin/env python3
"""bait_budget.py — budget.py must be SEEN to refuse.

Six baits. The corrupt-ledger one is the reason this file exists: on 2026-09-05
a NaN reached an accumulator and reopened a whole day's cap, because
`nan + 25 > 25` is False. A guard is tested against what it must CATCH.
"""
import importlib.util, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.realpath(os.path.join(HERE, "..", "gates", "02-retrieval-economy", "budget.py"))
fails = []
seen = []


def load(state):
    os.environ["COYWOLF_BUDGET_STATE"] = state
    spec = importlib.util.spec_from_file_location("budget_%s" % os.path.basename(state), SRC)
    m = importlib.util.module_from_spec(spec)
    # REGISTER IT. run_baits' tracer walks sys.modules at exit to decide which
    # form a bait executed, and module_from_spec does NOT register. Without this
    # the bait runs the code, passes, and is reported as an orphan that baited
    # nothing — green tests, uncovered form.
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def check(name, cond, detail=""):
    print("%s  %-58s %s" % ("OK " if cond else "XX ", name,
                            "" if cond else detail[:60]))
    seen.append(name)
    if not cond:
        fails.append(name)


with tempfile.TemporaryDirectory() as d:
    b = load(d)
    json.dump({"daily_call_cap": 500}, open(os.path.join(d, "budget-config.json"), "w"))

    tok = b.reserve(420, "v3 evidence arm")
    check("a run under the cap is allowed", isinstance(tok, str) and len(tok) == 12)

    try:
        b.reserve(10, "second run")
        check("a SECOND run is refused while one is in flight", False, "it was allowed")
    except b.BudgetRefused as e:
        check("a SECOND run is refused while one is in flight", "one at a time" in str(e))

    check("release frees the lock", b.release(tok) is True)

    try:
        b.reserve(200, "over cap")
        check("a run over the daily cap is refused", False, "420+200 > 500 was allowed")
    except b.BudgetRefused as e:
        check("a run over the daily cap is refused", "daily cap" in str(e))

    for bad in (0, -5, True, "420", 4.0, float("nan")):
        try:
            b.reserve(bad, "bad input")
            check("reserve(%r) is refused" % (bad,), False, "accepted")
            break
        except b.BudgetRefused:
            pass
    else:
        check("non-int / zero / bool / NaN call counts are refused", True)

    with open(os.path.join(d, "budget.jsonl"), "a") as f:
        f.write('{"ts": "2099-01-01T00:00:00", "event": "reserve", "calls": NaN}\n')
    try:
        b.spent_today()
        check("a NaN in the ledger FAILS CLOSED, never reads as zero", False, "it was accepted")
    except b.BudgetCorrupt:
        check("a NaN in the ledger FAILS CLOSED, never reads as zero", True)

with tempfile.TemporaryDirectory() as d:
    b = load(d)
    os.makedirs(d, exist_ok=True)
    json.dump({"token": "dead", "label": "crashed run", "calls": 1,
               "host": __import__("socket").gethostname(), "pid": 999999, "started": 0},
              open(os.path.join(d, "budget.lock"), "w"))
    try:
        t = b.reserve(1, "after a crash")
        check("a lock held by a DEAD pid on this host is broken", isinstance(t, str))
    except b.BudgetRefused as e:
        check("a lock held by a DEAD pid on this host is broken", False, str(e))


# --- the three the CONTINUOUS ADVERSARY found, score 8 ------------------------
import tempfile as _tf, json as _json, socket as _socket, os as _os  # noqa: E402 -- this block runs before the one below that also imports them
# Elapsed time is not liveness, and "permission denied" is not "dead". Both let a
# second run start beside a first -- the exact disaster budget.py exists to stop.
with _tf.TemporaryDirectory() as d:
    b = load(d)
    _json.dump({"token": "t", "label": "a run owned by another uid", "calls": 10,
                "host": _socket.gethostname(), "pid": 1, "started": __import__("time").time(),
                "holder": "inprocess"}, open(_os.path.join(d, "budget.lock"), "w"))
    try:
        b.reserve(1, "must not start")
        check("a lock held by ANOTHER UID's live process is not broken", False,
              "PermissionError read as dead")
    except b.BudgetRefused:
        check("a lock held by ANOTHER UID's live process is not broken", True)

with _tf.TemporaryDirectory() as d:
    b = load(d)
    _json.dump({"token": "t", "label": "an eval still running after 7h", "calls": 900,
                "host": _socket.gethostname(), "pid": 1,
                "started": __import__("time").time() - 7 * 3600, "holder": "cli"},
               open(_os.path.join(d, "budget.lock"), "w"))
    try:
        b.reserve(1, "must not start")
        check("a 7-hour-old lock is NOT broken by a timer", False, "elapsed time broke it")
    except b.BudgetRefused:
        check("a 7-hour-old lock is NOT broken by a timer", True)
    check("but `break` removes it by hand, and says so",
          b.main(["budget.py", "break"]) == 0 and not _os.path.exists(_os.path.join(d, "budget.lock")))

with _tf.TemporaryDirectory() as d:
    b = load(d)
    b.reserve(5, "a run whose day must not depend on the caller's timezone")
    row = _json.loads(open(_os.path.join(d, "budget.jsonl")).read().strip().split("\n")[-1])
    check("ledger timestamps are UTC-stamped, so two machines share one day",
          row["ts"].endswith("Z"))

# --- the bait that ESCAPED on 2026-09-07 -------------------------------------
# A CLI hold has no live process behind it. The first version broke it instantly
# as a "dead holder" and let a 20-call gate start anyway. Reserving in-process,
# as every earlier bait did, could never have caught this.
import tempfile as _tf, json as _json, socket as _socket, os as _os, sys as _sys
with _tf.TemporaryDirectory() as d:
    b = load(d)
    _json.dump({"token": "cli1", "label": "operator hold", "calls": 400,
                "host": _socket.gethostname(), "pid": 999999, "started": __import__("time").time(),
                "holder": "cli"},
               open(_os.path.join(d, "budget.lock"), "w"))
    try:
        b.reserve(20, "a gate that must NOT start")
        check("a CLI hold is NOT broken just because its pid exited", False, "the run started")
    except b.BudgetRefused:
        check("a CLI hold is NOT broken just because its pid exited", True)

# run_baits reads this exact shape: `BAIT: PASS n/m`, n == m >= 1. A bait that
# exits 0 without it is reported as "did it run anything?" and the whole suite
# goes red -- correctly, because a silent bait is indistinguishable from none.
# --- the two the third adversary pass found, score 6 (fail-closed, still bugs) -
with _tf.TemporaryDirectory() as d:
    b = load(d)
    # a truncated lock: a process killed between O_EXCL create and the write.
    # `break` is the ONLY recovery path, so it must survive exactly this.
    open(_os.path.join(d, "budget.lock"), "w").write('{"token": "t", "lab')
    # A bait must REPORT, never die: the first version let break's own crash kill
    # the bait file, so the whole suite went red with no line naming the case.
    try:
        rc = b.main(["budget.py", "break"])
    except Exception as e:
        rc = "raised %s" % type(e).__name__
    check("break survives a corrupt lock file and removes it",
          rc == 0 and not _os.path.exists(_os.path.join(d, "budget.lock")),
          "rc=%s, lock still present" % rc)

with _tf.TemporaryDirectory() as d:
    b = load(d)
    _json.dump({"token": "t", "label": "a crashed run", "calls": 1,
                "host": _socket.gethostname(), "pid": 999999, "started": 0,
                "holder": "inprocess"}, open(_os.path.join(d, "budget.lock"), "w"))
    import threading as _th2
    errs, ready = [], _th2.Barrier(4)
    def _reap():
        ready.wait()
        try:
            b._held_by()
        except Exception as e:
            errs.append(type(e).__name__)
    ts = [_th2.Thread(target=_reap) for _ in range(4)]
    for t in ts: t.start()
    for t in ts: t.join()
    check("four callers reaping ONE dead lock: no raw traceback", not errs,
          "raised %s" % errs[:3])

# --- CONCURRENCY, reproduced rather than reasoned about ----------------------
# The continuous adversary broke this file at score 9 with two concurrent
# `reserve` calls: both won, 4 of 5 trials, and 800 calls landed against a cap of
# 500. Every earlier bait here reserved sequentially in one process, so the file
# had NO synchronisation and twelve green baits. A race is baited by racing.
import subprocess as _sp, threading as _th

def _race(state, n, calls, cap):
    _os.makedirs(state, exist_ok=True)
    _json.dump({"daily_call_cap": cap}, open(_os.path.join(state, "budget-config.json"), "w"))
    env = dict(_os.environ, COYWOLF_BUDGET_STATE=state)
    wins, start = [], _th.Barrier(n)
    def go():
        start.wait()
        r = _sp.run([_sys.executable, SRC, "reserve", str(calls), "racer"],
                    capture_output=True, text=True, env=env)
        if r.returncode == 0:
            wins.append(r.stdout.strip())
    ts = [_th.Thread(target=go) for _ in range(n)]
    for t in ts: t.start()
    for t in ts: t.join()
    reserved = sum(json.loads(l)["calls"] for l in
                   open(_os.path.join(state, "budget.jsonl"), encoding="utf-8")
                   if l.strip() and json.loads(l).get("event") == "reserve")
    return len(wins), reserved

_multi, _over = 0, 0
with _tf.TemporaryDirectory() as base:
    for trial in range(5):
        w, reserved = _race(_os.path.join(base, "t%d" % trial), 4, 400, 500)
        if w > 1:
            _multi += 1
        if reserved > 500:
            _over += 1
check("4 concurrent reservations: exactly ONE wins, every trial", _multi == 0,
      "%d/5 trials handed the lock to more than one caller" % _multi)
check("4 concurrent reservations never exceed the daily cap", _over == 0,
      "%d/5 trials reserved more than the cap" % _over)

print("\n%s  %d/%d" % ("BAIT: PASS" if not fails else "BAIT: FAIL",
                       len(seen) - len(fails), len(seen)))
for l in fails:
    print("   failed: %s" % l)
sys.exit(1 if fails else 0)
