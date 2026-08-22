#!/usr/bin/env python3
"""lint/bait_baits_pair — bait the pairing rule itself.

The rule cannot exempt itself. Every mutation below is a mistake already made in
this repo during the three refutations of 2026-08-22.
"""
import os, shutil, subprocess, sys, tempfile

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []

def run(root):
    r = subprocess.run([sys.executable, os.path.join(root, "lint/baits_pair.py")],
                       capture_output=True, text=True, cwd=root, timeout=60)
    return r.returncode, (r.stdout + r.stderr).strip()

def sandbox():
    root = tempfile.mkdtemp(prefix="bait-bp-")
    dst = os.path.join(root, "x")
    shutil.copytree(R, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return root, dst

def check(label, cond, detail=""):
    results.append((label, cond))
    print("%s  %-56s %s" % ("OK " if cond else "XX ", label, detail[:38]))

def bait(label, mutate, want_rc, want_text):
    root, d = sandbox()
    if not mutate(d):
        check(label, False, "MUTATION DID NOT LAND")
        shutil.rmtree(root, ignore_errors=True); return
    rc, out = run(d)
    line = next((l for l in out.splitlines() if want_text in l), out.splitlines()[0] if out else "")
    check(label, rc == want_rc and want_text in out, line.strip()[:38])
    shutil.rmtree(root, ignore_errors=True)

root, d = sandbox()
rc, out = run(d)
check("B1 a pristine tree passes", rc == 0 and "GREEN" in out, out.splitlines()[0][:38])
shutil.rmtree(root, ignore_errors=True)
print()

def new_unbaited(d):
    p = os.path.join(d, "gates", "01-ste", "checks.py")
    s = open(p).read().replace('    "S5":', '    "S9": "a check nobody baited",\n    "S5":')
    open(p, "w").write(s)
    return "S9" in open(p).read()

def drop_baseline(d):
    p = os.path.join(d, "lint", "baits_pair.baseline")
    if not os.path.exists(p):
        return False
    os.remove(p)
    # with no baseline, an unbaited check must still be caught
    return new_unbaited(d)

def no_checks_at_all(d):
    p = os.path.join(d, "gates", "01-ste", "checks.py")
    open(p, "w").write("CHECKS = {}\n")
    for f in ("baits.py",):
        q = os.path.join(d, "gates", "01-ste", f)
        if os.path.exists(q):
            os.remove(q)
    t = os.path.join(d, "test_gates.py")
    if os.path.exists(t):
        os.remove(t)
    for lf in os.listdir(os.path.join(d, "lint")):
        if lf.startswith("bait_"):
            os.remove(os.path.join(d, "lint", lf))
    return True

bait("BAIT B1 a NEW unbaited check fails", new_unbaited, 1, "with no bait")
bait("BAIT B1 deleting the baseline does NOT reset the ratchet", drop_baseline, 1, "with no bait")
bait("BAIT B1 no numbered check anywhere fails, not passes", no_checks_at_all, 1, "no numbered check")

bad = [l for l, ok in results if not ok]
print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL",
                       len(results) - len(bad), len(results)))
sys.exit(1 if bad else 0)
