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
print("\n%s  %d/%d" % ("BAIT: PASS" if not fails else "BAIT: FAIL",
                       len(seen) - len(fails), len(seen)))
for l in fails:
    print("   failed: %s" % l)
sys.exit(1 if fails else 0)
