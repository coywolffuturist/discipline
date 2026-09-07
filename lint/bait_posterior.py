#!/usr/bin/env python3
"""bait_posterior.py — the calibration ledger must be SEEN to refuse and to drift."""
import importlib.util, json, os, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.realpath(os.path.join(HERE, "..", "gates", "19-state-the-posterior", "posterior.py"))
fails = []
seen = []


def load(state):
    os.environ["POSTERIOR_STATE"] = state
    spec = importlib.util.spec_from_file_location("post_%s" % os.path.basename(state), SRC)
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


def refuses(fn, *a):
    try:
        fn(*a)
        return False
    except SystemExit:
        return True


with tempfile.TemporaryDirectory() as d:
    p = load(d)
    check("one-way-door floor is stricter than reversible",
          p._floors()["one-way-door"] > p._floors()["reversible"])
    out = p.log("0.80", "reversible", ["the ledger records a weak claim"])
    check("a claim BELOW the floor is flagged, not silently accepted", "BELOW" in out)
    check("an unknown door is refused", refuses(p.log, "0.99", "maybe", ["x" * 20]))
    check("p outside 0..1 is refused", refuses(p.log, "1.4", "reversible", ["x" * 20]))
    check("a claim with no text is refused", refuses(p.log, "0.99", "reversible", ["no"]))
    check("settling an unknown id is refused", refuses(p.settle, "deadbeef", "right"))

with tempfile.TemporaryDirectory() as d:
    p = load(d)
    for i in range(9):
        p.log("0.96", "one-way-door", ["claim number %d about the substrate" % i])
    for e in p._entries():
        p.settle(e["id"], "wrong")
    before = p._floors()["one-way-door"]
    p.audit()
    check("under 10 settled, the floor is NOT moved", p._floors()["one-way-door"] == before,
          "moved on 9")

with tempfile.TemporaryDirectory() as d:
    p = load(d)
    for i in range(10):
        p.log("0.96", "one-way-door", ["claim number %d about the substrate" % i])
    es = p._entries()
    for e in es[:4]:
        p.settle(e["id"], "right")
    for e in es[4:]:
        p.settle(e["id"], "wrong")
    before = p._floors()["one-way-door"]
    out = p.audit()
    check("40%% right over 10 settled RAISES the floor", p._floors()["one-way-door"] > before,
          "floor stayed %.2f" % before)
    check("the drift is reported, not silent", "CALIBRATION DRIFT" in out)

with tempfile.TemporaryDirectory() as d:
    p = load(d)
    old = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 40 * 86400))
    with open(os.path.join(d, "posteriors.jsonl"), "w") as f:
        for i in range(6):
            f.write(json.dumps({"id": "old%d" % i, "ts": old, "p": 0.96,
                                "door": "reversible", "claim": "an abandoned claim",
                                "outcome": "TBD"}) + "\n")
        f.write(json.dumps({"id": "new1", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "p": 0.96,
                            "door": "reversible", "claim": "a settled claim",
                            "outcome": "right"}) + "\n")
    check("claims older than 30 days go stale, not unnoticed", p.mark_stale() == 6)
    check("more stale than settled REFUSES to score", "REFUSED to score" in p.audit())

with tempfile.TemporaryDirectory() as d:
    p = load(d)
    open(os.path.join(d, "posteriors.jsonl"), "w").write(
        '{"id":"x","ts":"2026-01-01T00:00:00","p":NaN,"door":"reversible",'
        '"claim":"poison","outcome":"TBD"}\n')
    try:
        p._entries()
        check("a NaN posterior FAILS CLOSED", False, "accepted")
    except p.Corrupt:
        check("a NaN posterior FAILS CLOSED", True)

# run_baits reads this exact shape: `BAIT: PASS n/m`, n == m >= 1. A bait that
# exits 0 without it is reported as "did it run anything?" and the whole suite
# goes red -- correctly, because a silent bait is indistinguishable from none.
print("\n%s  %d/%d" % ("BAIT: PASS" if not fails else "BAIT: FAIL",
                       len(seen) - len(fails), len(seen)))
for l in fails:
    print("   failed: %s" % l)
sys.exit(1 if fails else 0)
