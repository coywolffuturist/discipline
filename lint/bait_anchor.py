#!/usr/bin/env python3
"""bait_anchor.py — gate 02's checkpoint-and-pause must refuse what it exists to refuse.

Each case is a planted defect that a broken anchor.py would let through. Fake meters stand
in for the provider (in-process, through COYWOLF_METER_CMD, and through the real CLI), so no
case spends a token. Rebuilt 2026-10-03 after a refuter planted six breaks the first version
passed: the reserve pause deleted, meter() failing open, main() exiting 0 on a dead meter, the
path guard removed, a NaN estimate, and re-pricing that laundered a budget past his approval.
"""
import importlib.util, json, os, subprocess, sys, tempfile
sys.dont_write_bytecode = True   # a stale .pyc from a same-second edit once masked a restored file

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.realpath(os.path.join(HERE, "..", "gates", "02-retrieval-economy", "anchor.py"))
os.environ["COYWOLF_BUDGET_STATE"] = tempfile.mkdtemp()
os.environ.pop("COYWOLF_METER_CMD", None)
spec = importlib.util.spec_from_file_location("anchor_bait", SRC)
A = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = A   # run_baits traces sys.modules; module_from_spec alone does not register the form
spec.loader.exec_module(A)

fails = 0
total = 0
def expect(name, got, want):
    global fails, total
    total += 1
    ok = got == want
    fails += 0 if ok else 1
    print("%s  %s (got %r, want %r)" % ("ok  " if ok else "FAIL", name, got, want))

W1, W2 = 1791608400, 1792213200   # two provider week ids (weekly reset epochs)
def m(week, session=10, period=W1):
    return lambda: {"week": week, "session": session, "period": period}
def broken():
    raise A.MeterUnavailable("planted")
def raises(fn):
    try:
        fn(); return "returned"
    except A.MeterUnavailable:
        return "raised"

# ── price: the ask line, the reserve, bad estimates, laundering ─────────────────────────
expect("over the 2% line without his yes -> ask", A.price("j1", 2.5, read=m(10))[0], 3)
expect("over the line WITH his yes -> go", A.price("j1", 2.5, approved=True, read=m(10))[0], 0)
expect("under the line -> go", A.price("j2", 1.5, read=m(10))[0], 0)
expect("would cut into the reserve -> ask", A.price("j3", 1.5, read=m(84))[0], 3)
expect("NaN estimate -> ask", A.price("jn", float("nan"), read=m(10))[0], 3)
expect("negative estimate -> ask", A.price("jneg", -100, read=m(10))[0], 3)
expect("non-number estimate -> ask", A.price("jx", "lots", read=m(10))[0], 3)
expect("re-pricing adds up: 1.5 + 1.5 passes the line -> ask", A.price("j2", 1.5, read=m(30))[0], 3)
expect("re-pricing never moves the baseline", json.load(open(A._path("j2")))["baseline_week"], 10)
A.price("lj", 1, approved=True, read=m(10))
A.price("lj", 1, approved=True, read=m(15))   # an approved re-price must not reset what was already spent
expect("approved re-price keeps the first baseline", json.load(open(A._path("lj")))["baseline_week"], 10)
expect("so the earlier spend still counts -> pause", A.check("lj", read=m(15))[0], 2)
A.price("s1", 1.5, read=m(10))   # unapproved today: j2 1.5 + s1 1.5 = 3.0
expect("many small unapproved jobs are one big job -> ask", A.price("s2", 1.5, read=m(10))[0], 3)
expect("price on a dead meter raises, never GO", raises(lambda: A.price("jd", 0.5, approved=True, read=broken)), "raised")

# ── check: every failure pauses ─────────────────────────────────────────────────────────
expect("never priced -> pause", A.check("ghost", read=m(10))[0], 2)
expect("within budget -> climb", A.check("j1", read=m(11))[0], 0)
expect("small budget pauses one step early (2.5% at 2%)", A.check("j1", read=m(12))[0], 2)
# With the reserve check in price(), a job only reaches the reserve by spending its budget, unless the reserve
# line moves after pricing (an operator tightening it mid-job). Lower it and the pause must still fire.
A.price("big", 20, approved=True, read=m(40))
_r = A.RESERVE_USED_PCT; A.RESERVE_USED_PCT = 45
expect("RESERVE alone (budget far from spent) -> pause", A.check("big", read=m(46))[0], 2)
A.RESERVE_USED_PCT = _r
expect("meter unreadable -> pause (fail closed)", A.check("j1", read=broken)[0], 2)
A.price("ten", 10, approved=True, read=m(10))
expect("a budget of 3% or more pauses exactly at its line", (A.check("ten", read=m(19))[0], A.check("ten", read=m(20))[0]), (0, 2))
open(A._path("corrupt"), "w").write("{not json")
expect("corrupt state -> pause", A.check("corrupt", read=m(10))[0], 2)
json.dump({"budget_pct": 1}, open(A._path("partial"), "w"))
expect("record without a baseline -> pause", A.check("partial", read=m(10))[0], 2)

# ── the weekly reset is READ from the provider, never inferred (refuter 2026-10-03, two rounds) ──
A.price("night", 1.9, approved=True, read=m(80))
expect("week reset since pricing -> pause", A.check("night", read=m(3, period=W2))[0], 2)
expect("the reset pause LATCHES: a later check above the old baseline still pauses", A.check("night", read=m(85, period=W2))[0], 2)
A.price("night", 1, approved=True, read=m(3, period=W2))
rec = json.load(open(A._path("night")))
expect("re-pricing after a reset starts a fresh period: new baseline", rec["baseline_week"], 3)
expect("...and the old budget does not carry over", rec["budget_pct"], 1)
expect("...and the latch clears", A.check("night", read=m(3, period=W2))[0], 0)
A.price("zero", 5, approved=True, read=m(0))
expect("a job priced at week 0 still sees the reset", A.check("zero", read=m(4, period=W2))[0], 2)
A.price("same", 1, approved=True, read=m(10))
A.price("same", 1, approved=True, read=m(10))
expect("re-pricing in the SAME week never starts a fresh period", json.load(open(A._path("same")))["budget_pct"], 2)
A.price("dip", 5, approved=True, read=m(20))
expect("the meter falling inside one week pauses (untrusted), never launders", A.check("dip", read=m(19))[0], 2)
# (an estimate over 100% is also refused, but the reserve check refuses it first, so no case can isolate it)

# ── the daily cap: its window, what it counts, and stale corrupt files ───────────────────
import time as _t
CAPDIR = tempfile.mkdtemp(); _old = A.DIR; A.DIR = os.path.join(CAPDIR, "anchors"); os.makedirs(A.DIR)
now = _t.time()
json.dump({"pricings": [{"at": now - 23 * 3600, "est": 3.5, "approved": False}]}, open(os.path.join(A.DIR, "old23.json"), "w"))
expect("an unapproved pricing 23h ago still counts in the cap", A._unapproved_today(now), 3.5)
json.dump({"pricings": [{"at": now - 25 * 3600, "est": 3.5, "approved": False}]}, open(os.path.join(A.DIR, "old23.json"), "w"))
expect("one 25h ago has aged out", A._unapproved_today(now), 0.0)
json.dump({"pricings": [{"at": now, "est": 3.5, "approved": True}]}, open(os.path.join(A.DIR, "appr.json"), "w"))
expect("approved budgets do not count against the unapproved cap", A._unapproved_today(now), 0.0)
open(os.path.join(A.DIR, "bad.json"), "w").write("{corrupt")
expect("a fresh corrupt record counts against the cap (fails closed)", A._unapproved_today(now), A.ASK_PCT)
os.utime(os.path.join(A.DIR, "bad.json"), (now - 2 * 3600, now - 2 * 3600))
expect("a corrupt record 2h old still counts", A._unapproved_today(now), A.ASK_PCT)
os.utime(os.path.join(A.DIR, "bad.json"), (now - 2 * 86400, now - 2 * 86400))
expect("a stale corrupt record ages out", A._unapproved_today(now), 0.0)
A.DIR = _old

# ── job names ───────────────────────────────────────────────────────────────────────────
for bad in ("../x", "..", "a/b", "--approved", ""):
    try:
        A._path(bad); got = "accepted"
    except ValueError:
        got = "refused"
    expect("job name %r refused" % bad, got, "refused")

# ── meter(): junk, NaN, out-of-range and a failing command are all unreadable ───────────
def meter_with(cmd):
    os.environ["COYWOLF_METER_CMD"] = cmd
    try:
        A.meter(); return "read"
    except A.MeterUnavailable:
        return "unreadable"
    finally:
        os.environ.pop("COYWOLF_METER_CMD", None)
expect("meter cmd printing NaN -> unreadable", meter_with('echo \'{"week_pct": NaN, "session_pct": 1}\''), "unreadable")
expect("meter cmd printing junk -> unreadable", meter_with("echo hello"), "unreadable")
expect("meter cmd over 100 -> unreadable", meter_with('echo \'{"week_pct": 140, "session_pct": 1}\''), "unreadable")
expect("meter cmd that exits 1 -> unreadable", meter_with('echo \'{"week_pct": 5, "session_pct": 1, "week_reset": 1791608400}\'; exit 1'), "unreadable")
expect("meter cmd with the old key names -> unreadable", meter_with('echo \'{"week": 5, "session": 1}\''), "unreadable")
expect("meter cmd with a zero reset time -> unreadable", meter_with('echo \'{"week_pct": 5, "session_pct": 1, "week_reset": 0}\''), "unreadable")
expect("meter cmd without the weekly reset time -> unreadable", meter_with('echo \'{"week_pct": 5, "session_pct": 1}\''), "unreadable")
expect("a good meter cmd -> read", meter_with('echo \'{"week_pct": 5, "session_pct": 1, "week_reset": 1791608400}\''), "read")

# ── main(): the CLI never exits 0 on a dead meter ───────────────────────────────────────
env = dict(os.environ, COYWOLF_METER_CMD="exit 1")
env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
cli = lambda *a: subprocess.run([sys.executable, SRC] + list(a), env=env, capture_output=True, text=True).returncode
expect("CLI price on a dead meter -> 3", cli("price", "clijob", "0.5", "--approved"), 3)
expect("CLI check on a dead meter -> 2", cli("check", "j1"), 2)
expect("CLI check on a bad job name -> 2", cli("check", "../x"), 2)
expect("CLI '--approved' as a job name is refused", cli("price", "--approved", "50") != 0, True)
expect("CLI --model with no name is refused", cli("price", "mm", "0.5", "--model", "--approved") != 0, True)
bad_env = dict(env, COYWOLF_ASK_PCT="nan", COYWOLF_METER_CMD='echo \'{"week_pct": 10, "session_pct": 1, "week_reset": 1791608400}\'')
# (a setting of 0 is refused too, but 0 already refuses every job, so no case can isolate it)
expect("a NaN ask line refuses to run", subprocess.run([sys.executable, SRC, "price", "x", "0.5"], env=bad_env, capture_output=True).returncode, 3)

# ── parallel pricing: 8 jobs at once must not all see an empty cap (the 10-02 incident) ──
PDIR = tempfile.mkdtemp()
penv = dict(env, COYWOLF_BUDGET_STATE=PDIR, COYWOLF_METER_CMD='sleep 0.3; echo \'{"week_pct": 10, "session_pct": 1, "week_reset": 1791608400}\'')
procs = [subprocess.Popen([sys.executable, SRC, "price", "par%d" % i, "1.9"], env=penv, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in range(8)]
gos = sum(1 for p in procs if p.wait() == 0)
expect("8 parallel unapproved 1.9% jobs: only those that fit the 4% cap start", gos, 2)
cps = [subprocess.Popen([sys.executable, SRC, "checkpoint", "par0", "unit %d" % i, "next"], env=penv) for i in range(8)]
[c.wait() for c in cps]
expect("8 parallel checkpoints are all kept (the lock)", len(json.load(open(os.path.join(PDIR, "anchors", "par0.json")))["checkpoints"]), 8)

# ── resume ──────────────────────────────────────────────────────────────────────────────
A.price("mjob", 0.5, approved=True, model="claude-opus-5-5", read=m(10))
A.checkpoint("mjob", "page 3 of 9 written", "page 4")
rc, msg = A.resume("mjob")
expect("resume returns the last anchor", rc == 0 and "page 4" in msg, True)
expect("resume names the recorded model", "claude-opus-5-5" in msg, True)
expect("no downgrade path exists", any(w in open(SRC).read().lower() for w in ("fallback_model", "downgrade_to", "cheaper_model")), False)

# run_baits reads this exact shape: `BAIT: PASS n/m`.
print("\n%s  %d/%d" % ("BAIT: PASS" if not fails else "BAIT: FAIL", total - fails, total))
sys.exit(1 if fails else 0)
