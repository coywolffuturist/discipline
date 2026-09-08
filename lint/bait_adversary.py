#!/usr/bin/env python3
"""bait_adversary.py — the continuous adversary's recorder must be SEEN to refuse.

The point of a score is that it can be wrong. A recorder that accepts an
unstated attack, an out-of-range score, or a record against a run that was never
opened produces a ledger that cannot be audited — and the whole form exists to
be audited out of existence if it does not pay.
"""
import importlib.util, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.realpath(os.path.join(HERE, "..", "gates", "18-adversarial-pass", "adversary.py"))
POST = os.path.realpath(os.path.join(HERE, "..", "gates", "19-state-the-posterior", "posterior.py"))
fails = []
seen = []


def load(path, state_var, state):
    os.environ[state_var] = state
    name = os.path.basename(path)[:-3] + "_" + os.path.basename(state)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m          # the tracer walks sys.modules to attribute coverage
    spec.loader.exec_module(m)
    return m


def check(name, cond, detail=""):
    print("%s  %-58s %s" % ("OK " if cond else "XX ", name, "" if cond else detail[:60]))
    seen.append(name)
    if not cond:
        fails.append(name)


def refuses(m, fn, *a):
    # posterior.py refuses with SystemExit, adversary.py with its own Refused.
    # Naming only one of them made this helper report a real refusal as a crash.
    kinds = tuple(k for k in (getattr(m, "Refused", None), SystemExit) if k is not None)
    try:
        fn(*a)
        return False
    except kinds:
        return True


with tempfile.TemporaryDirectory() as d:
    a = load(SRC, "ADVERSARY_STATE", d)
    check("an unlabelled run is refused", refuses(a, a.open_run, "x"))
    run = a.open_run("the discipline build")
    check("opening a run returns an id", isinstance(run, str) and len(run) == 8)
    check("a record against an UNOPENED run is refused",
          refuses(a, a.record, "deadbeef", "f.py", 3, ["a specific mechanical attack"]))
    for bad in (11, -1, True, 7.5):
        if not refuses(a, a.record, run, "f.py", bad, ["a specific mechanical attack"]):
            check("score %r is refused" % (bad,), False, "accepted")
            break
    else:
        check("a score outside 0..10, or a bool or float, is refused", True)
    check("an attack that names nothing is refused", refuses(a, a.record, run, "f.py", 9, []))
    check("an attack too short to be mechanical is refused",
          refuses(a, a.record, run, "f.py", 9, ["it's bad"]))
    check("an unnamed artifact is refused",
          refuses(a, a.record, run, "  ", 3, ["a specific mechanical attack"]))
    out = a.record(run, "gates/02/budget.py", 8, ["the lock carries the pid of a process that exits"])
    check("a score >= 7 INTERRUPTS rather than being filed quietly", "INTERRUPT" in out)
    out = a.record(run, "gates/02/other.py", 2, ["a weak objection stated mechanically enough"])
    check("a low score does NOT interrupt", "INTERRUPT" not in out)
    check("max reports the worst score in the run", a.max_score(run) == 8)

with tempfile.TemporaryDirectory() as d:
    a = load(SRC, "ADVERSARY_STATE", d)
    open(os.path.join(d, "adversary.jsonl"), "w").write(
        '{"ts":"x","run":"r","event":"attack","artifact":"f","score":NaN,"attacks":["x"]}\n')
    try:
        a._entries()
        check("a NaN score FAILS CLOSED", False, "accepted")
    except a.Corrupt:
        check("a NaN score FAILS CLOSED", True)

with tempfile.TemporaryDirectory() as d:
    p = load(POST, "POSTERIOR_STATE", d)
    check("posterior refuses an out-of-range adversary score",
          refuses(p, p.log, "0.96", "reversible", ["a claim long enough to settle later"], 11))
    p.log("0.96", "reversible", ["a claim long enough to settle later"], 8)
    check("posterior carries the adversary score onto the claim",
          any(e.get("adv") == 8 for e in p._entries()))
    check("the audit REFUSES to read a signal from too few scored claims",
          "adversary signal: not enough evidence" in p.audit())

print("\n%s  %d/%d" % ("BAIT: PASS" if not fails else "BAIT: FAIL", len(seen) - len(fails), len(seen)))
for l in fails:
    print("   failed: %s" % l)
sys.exit(1 if fails else 0)
