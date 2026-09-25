#!/usr/bin/env python3
"""bait_hook_prior_posterior.py — hooks/hook_prior.py and hooks/hook_posterior.py, seen to fire.

Two Stop hooks, gates 08 and 19. Each owns ONE flag and consumes it, because a
shared flag let whichever hook drew first silence the rest. So the baits are:
fires when its flag exists, quiet when it does not, consumes on firing, and
neither hook's firing touches the other's flag.
"""
import json, os, shutil, subprocess, sys, tempfile
os.environ["STOP_HOOK_MODE"] = "force"   # these baits test what the hooks DETECT; bait_stop_mode.py tests the silence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = {
    "prior": (os.path.join(ROOT, "hooks", "hook_prior.py"), "prior-owed", "GATE 08"),
    "posterior": (os.path.join(ROOT, "hooks", "hook_posterior.py"), "posterior-owed", "GATE 19"),
}

bad = []
total = 0


SESSION = "baitsession"


def flagfile(which, session=None):
    """Where the hook ACTUALLY looks. Flags are one-per-consumer PER SESSION
    (_flags.path builds coywolf-<name>.<session>.flag), so a flat name is a
    file nothing reads. This bait used a flat name and therefore never fired
    the hooks at all: H1/H4/H5 passed because nothing ran."""
    return "coywolf-%s.%s.flag" % (HOOKS[which][1], session or SESSION)


def run(which, d, session=None):
    path = HOOKS[which][0]
    payload = json.dumps({"session_id": session or SESSION, "hook_event_name": "Stop"})
    r = subprocess.run([sys.executable, path], input=payload, capture_output=True, text=True,
                       env=dict(os.environ, TMPDIR=d), timeout=30)
    ctx = ""
    if r.stdout.strip():
        out = json.loads(r.stdout)
        # THE ENVELOPE IS THE CONTRACT. A reviewer changed the event name to
        # PostToolUse and suppressOutput to False; the harness would have
        # ignored the block, and every bait stayed green.
        if out.get("hookSpecificOutput", {}).get("hookEventName") != "Stop" or out.get("suppressOutput") is not True:
            return r.returncode, "WRONG ENVELOPE: %s" % json.dumps(out)[:80]
        ctx = out["hookSpecificOutput"]["additionalContext"]
    return r.returncode, ctx


def bait(label, cond, detail=""):
    global total
    total += 1
    print("  %s %-62s %s" % ("ok " if cond else "XX ", label, detail[:40]))
    if not cond:
        bad.append(label)


for which, (path, flag, marker) in HOOKS.items():
    d = tempfile.mkdtemp(prefix="hook-%s-bait-" % which)
    rc, ctx = run(which, d)
    bait("BAIT H1 %s: no flag, no output" % which, rc == 0 and ctx == "")
    ff = flagfile(which)
    open(os.path.join(d, ff), "w").write("Bash\n")
    rc, ctx = run(which, d)
    bait("BAIT H2 %s: flag present, the question is restored" % which,
         rc == 0 and marker in ctx, ctx[:40])
    bait("BAIT H3 %s: the flag was CONSUMED" % which, not os.path.exists(os.path.join(d, ff)))
    rc, ctx = run(which, d)
    bait("BAIT H4 %s: a second Stop is quiet" % which, rc == 0 and ctx == "")
    shutil.rmtree(d, ignore_errors=True)

d = tempfile.mkdtemp(prefix="hook-both-bait-")
for _which in HOOKS:
    open(os.path.join(d, flagfile(_which)), "w").write("Bash\n")
rc, ctx = run("prior", d)
bait("BAIT H5 gate 08 firing leaves gate 19's flag alone",
     os.path.exists(os.path.join(d, flagfile("posterior"))))
rc, ctx = run("posterior", d)
bait("BAIT H6 gate 19 still fires after gate 08 drew first", "GATE 19" in ctx)
shutil.rmtree(d, ignore_errors=True)

# H7 — CROSS-SESSION FLAG THEFT, the reason flags became session-scoped.
# Session A owes the question; session B stops. B must NOT consume A's flag and
# must NOT be asked A's question. Untested until 2026-09-21: the bait used one
# flat filename, under which this failure is not even expressible.
d = tempfile.mkdtemp(prefix="hook-xsession-bait-")
a_flag = os.path.join(d, flagfile("prior", "session-A"))
open(a_flag, "w").write("Bash\n")
rc, ctx = run("prior", d, session="session-B")
bait("BAIT H7 prior: session B is not asked session A's question", ctx == "", ctx[:40])
bait("BAIT H8 prior: session B did NOT consume session A's flag", os.path.exists(a_flag))
shutil.rmtree(d, ignore_errors=True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
