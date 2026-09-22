#!/usr/bin/env python3
"""bait_posterior.py — the calibration ledger must be SEEN to refuse and to drift."""
import importlib.util, io, json, os, sys, tempfile, time

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
        p.log("0.96", "one-way-door",
              ["claim number %d about substrate_%d.py" % (i, i)])
    for e in p._entries():
        p.settle(e["id"], "wrong")
    before = p._floors()["one-way-door"]
    p.audit(apply=True)   # apply=True since 2026-09-21: audit alone no longer writes,
                          # so without it this bait would pass on a broken guard
    check("under 10 settled, the floor is NOT moved", p._floors()["one-way-door"] == before,
          "moved on 9")

with tempfile.TemporaryDirectory() as d:
    p = load(d)
    for i in range(10):
        p.log("0.96", "one-way-door",
              ["claim number %d about substrate_%d.py" % (i, i)])
    es = p._entries()
    for e in es[:4]:
        p.settle(e["id"], "right")
    for e in es[4:]:
        p.settle(e["id"], "wrong")
    before = p._floors()["one-way-door"]
    out = p.audit(apply=True)
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

# --- THE RATCHET. The floor must move on EVIDENCE, never on being looked at.
# Measured 2026-09-20/21: reversible went 0.95 -> 0.99 in one session on ONE
# unchanged body of evidence (7/11 right). Four raises from four glances --
# audit added 0.01 whenever it ran while the rate was low, nothing recorded
# that the evidence had already been charged, and no branch ever lowered a
# floor. The control below is what makes the rest readable: without it, "the
# floor did not move" is equally consistent with a working guard and with a
# bait that never reached the code.
with tempfile.TemporaryDirectory() as d:
    p = load(d)
    DOOR = "reversible"
    default = p.DEFAULT_FLOORS[DOOR]

    def seed(n_right, n_wrong):
        """Replace the ledger wholesale, so each stage is a known total."""
        rows = []
        for i in range(n_right):
            rows.append({"id": "r%d" % i, "p": 0.98, "door": DOOR,
                         "outcome": "right", "claim": "x", "ts": "2026-09-21T00:00:00Z"})
        for i in range(n_wrong):
            rows.append({"id": "w%d" % i, "p": 0.98, "door": DOOR,
                         "outcome": "wrong", "claim": "x", "ts": "2026-09-21T00:00:00Z"})
        io.open(p.LEDGER, "w").write("".join(json.dumps(r) + "\n" for r in rows))

    def floor():
        return p._floors()[DOOR]

    seed(6, 6)                       # 12 settled, 50% -- under DRIFT_RATE
    out = p.audit(apply=False)
    check("CONTROL: a dry run writes nothing", floor() == default, "floor=%.2f" % floor())
    check("CONTROL: and it SAYS what it would have done", "WOULD RISE" in out, out[:60])

    p.audit(apply=True)
    check("apply raises once", floor() == round(default + 0.01, 2), "floor=%.2f" % floor())
    at_one = floor()

    p.audit(apply=True)
    check("the SAME evidence does not raise again", floor() == at_one, "floor=%.2f" % floor())
    p.audit(apply=True)
    check("nor on a third look", floor() == at_one, "floor=%.2f" % floor())

    seed(8, 8)                       # 16 settled, still 50%
    p.audit(apply=True)
    check("NEW settlements, still bad -> raises once more",
          floor() == round(default + 0.02, 2), "floor=%.2f" % floor())

    seed(19, 1)                      # 20 settled, 95% -- above RECOVER_RATE
    p.audit(apply=True)
    check("RECOVERED -> the floor DECAYS", floor() == round(default + 0.01, 2),
          "floor=%.2f" % floor())

    seed(39, 1)
    p.audit(apply=True)
    check("and decays again on new evidence", floor() == default, "floor=%.2f" % floor())

    seed(79, 1)
    p.audit(apply=True)
    check("never falls below DEFAULT_FLOORS", floor() == default, "floor=%.2f" % floor())


# --- THE ANCHOR GATE. A claim nobody can find is a claim nobody can settle.
# Measured 2026-09-21 over 237 logged claims: a page name settled 100% of the
# time, a sha 81%, a bare path 56%, a bare number 39% -- and 100 of 122 open
# claims carried no anchor at all. The gate applies to HIGH claims only,
# because those are the ones that move the floor.
with tempfile.TemporaryDirectory() as d:
    p = load(d)

    def logs(text, **kw):
        try:
            p.log(0.96, "reversible", text.split(), **kw)
            return True
        except SystemExit:
            return False

    # CONTROL FIRST. If nothing logs, every refusal below passes for the wrong
    # reason.
    check("CONTROL: an ANCHORED high claim still logs",
          logs("the fix is in gates/19-state-the-posterior/posterior.py"))
    check("a sha anchors it", logs("landed as commit 9b5181d after the gate ran"))
    check("a canon page name anchors it",
          logs("recorded in decision_the_classifier_decides_on_the_argmax"))
    check("a bare filename anchors it", logs("bait_posterior.py now covers this"))

    check("an UNANCHORED high claim is REFUSED",
          not logs("everything works properly now and is fully verified"))

    # THE FOUR CASES A REFUTER BROKE, 2026-09-21. Hex alone is not a sha: a
    # balance and an English word both passed, while a real page name and a
    # relative repo path were refused. The gate was wrong in BOTH directions.
    check("a bare BALANCE is not a sha",
          not logs("the treasury holds 1043210.55 USDC and nothing else"))
    check("an English word spelled from a-f is not a sha",
          not logs("every trace of the old rail was effaced before the cutover"))
    check("a capture_ page name IS an anchor",
          logs("the command is on page capture_20260101000000_1000000000000000001"))
    check("a RELATIVE repo path IS an anchor",
          logs("the gate now lives in gates/19-state-the-posterior and is wired in"))
    check("prose with a slash is NOT a path",
          not logs("we shipped it and/or reverted it, unclear which"))

    # The anchor must be in the text that is STORED, not merely in what was typed.
    long_unanchored = ("padding " * 60) + "landed as commit 9b5181d"
    check("an anchor PAST the 400-char store cut does not count",
          not logs(long_unanchored), "anchor sits beyond claim[:400]")
    check("--no-anchor is the escape hatch, not a default",
          logs("a real telegram message was delivered to him", no_anchor=True))

    # The gate must not touch low claims: an unsettled hunch costs nothing.
    before = len(p._entries())
    try:
        p.log(0.60, "reversible", "some vague low confidence hunch".split())
        low_ok = True
    except SystemExit:
        low_ok = False
    check("a LOW claim is NOT gated", low_ok and len(p._entries()) == before + 1)

    # The flag is recorded, so the audit can report how much of the record is
    # unanchored rather than leaving it invisible.
    es = p._entries()
    check("anchored is RECORDED on the row, not just enforced",
          any("anchored" in e for e in es), "no anchored field on any row")


# run_baits reads this exact shape: `BAIT: PASS n/m`, n == m >= 1. A bait that
# exits 0 without it is reported as "did it run anything?" and the whole suite
# goes red -- correctly, because a silent bait is indistinguishable from none.
print("\n%s  %d/%d" % ("BAIT: PASS" if not fails else "BAIT: FAIL",
                       len(seen) - len(fails), len(seen)))
for l in fails:
    print("   failed: %s" % l)
sys.exit(1 if fails else 0)
