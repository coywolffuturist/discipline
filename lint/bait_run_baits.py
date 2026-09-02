#!/usr/bin/env python3
"""bait_run_baits.py — the bait runner, seen to fail.

The rule cannot exempt itself. `lint/run_baits.py` exists because a registry
that executes nothing reported GREEN over a bait that had never run. So this
builds small checkouts with exactly those defects and asserts the runner goes
RED on each — and GREEN on the clean control, so a red is a verdict and not a
crash.
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "lint", "run_baits.py")

# A good bait EXECUTES the form. Naming it is not enough — see BAIT R6.
GOOD_BAIT = ('import os, subprocess, sys\n'
             'p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thing.py")\n'
             'r = subprocess.run([sys.executable, p, "--poison"])\n'
             'print("BAIT: PASS  1/1" if r.returncode == 1 else "BAIT: FAIL  0/1")\n')
FORM = "import sys\nsys.exit(1 if '--poison' in sys.argv else 0)\n"


def repo(files, runner_src=None):
    d = tempfile.mkdtemp(prefix="run-baits-bait-")
    for rel, body in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body)
    env = dict(os.environ, GIT_AUTHOR_NAME="bait", GIT_AUTHOR_EMAIL="bait@example",
               GIT_COMMITTER_NAME="bait", GIT_COMMITTER_EMAIL="bait@example")
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "commit", "-q", "-m", "bait", "--no-verify"]):
        subprocess.run(cmd, cwd=d, env=env, capture_output=True, check=True)
    if runner_src is not None:
        os.makedirs(os.path.join(d, "lint"), exist_ok=True)
        open(os.path.join(d, "lint", "run_baits.py"), "w").write(runner_src)
    return d


def run(d, runner=RUNNER):
    r = subprocess.run([sys.executable, runner], cwd=d,
                       env=dict(os.environ, RUN_BAITS_ROOT=d),
                       capture_output=True, text=True, timeout=120)
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, r.stdout + r.stderr


bad = []
total = 0


def bait(label, files, want_rc, want_text, runner_src=None):
    global total
    total += 1
    d = repo(files, runner_src)
    rc, out = run(d, os.path.join(d, "lint", "run_baits.py") if runner_src else RUNNER)
    ok = rc == want_rc and want_text.lower() in out.lower()
    print("  %s %-58s rc=%s" % ("ok " if ok else "XX ", label, rc))
    if not ok:
        bad.append(label)
        print("      wanted rc=%s containing %r\n      got: %s" % (want_rc, want_text, out.strip()[:300]))


base = {"gates/09-x/thing.py": FORM, "gates/09-x/bait_thing.py": GOOD_BAIT}

bait("BAIT R0 the clean control is GREEN", base, 0, "GREEN")
OTHER = "print('a different form')\n"
bait("BAIT R1 a form in a directory nobody listed, with no bait, is RED",
     dict(base, **{"hooks/other.py": OTHER}), 1, "hooks/other.py")
bait("BAIT R2 a bait that exits 0 and prints nothing is RED",
     dict(base, **{"gates/09-x/bait_thing.py": "x = 'thing.py'\n"}), 1, "NO `PASS n/m`")
bait("BAIT R3 a bait whose first statement kills the interpreter is RED",
     dict(base, **{"gates/09-x/bait_thing.py": "import sys; sys.exit(1)  # thing.py\n"}), 1, "rc=1")
bait("BAIT R4 a bait reporting 0/0 is RED",
     dict(base, **{"gates/09-x/bait_thing.py": "print('thing.py'); print('BAIT: PASS  0/0')\n"}), 1, "0/0")
bait("BAIT R5 a bait reporting FAIL is RED",
     dict(base, **{"gates/09-x/bait_thing.py": "print('thing.py'); print('BAIT: FAIL  0/1')\n"}), 1, "NO `PASS n/m`")
bait("BAIT R6 a bait that NAMES thing.py but never runs it does NOT cover it",
     dict(base, **{"gates/09-x/bait_thing.py": "print('I test thing.py, honest'); print('BAIT: PASS  1/1')\n"}),
     1, "gates/09-x/thing.py")
bait("BAIT R6b a bait that IMPORTS the form covers it",
     dict(base, **{"gates/09-x/bait_thing.py":
                   "import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
                   "import thing\nprint('BAIT: PASS  1/1')\n",
                   "gates/09-x/thing.py": "def f():\n    return 1\n"}), 0, "GREEN")
bait("BAIT R6c a byte-identical copy of an executed form is covered too",
     dict(base, **{"hooks/thing.py": FORM}), 0, "GREEN")
bait("BAIT R6d a shell form executed by a bait is covered",
     dict(base, **{"scripts/s.sh": "#!/bin/bash\nexit 3\n",
                   "scripts/bait_s.py":
                   "import os, subprocess\n"
                   "p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's.sh')\n"
                   "print('BAIT: PASS  1/1' if subprocess.run(['bash', p]).returncode == 3 else 'BAIT: FAIL  0/1')\n"}),
     0, "GREEN")
bait("BAIT R7 a checkout with no form at all is RED, not empty-green",
     {"README.md": "x\n"}, 1, "no code form")
bait("BAIT R8 an uncovered form in the baseline is debt, not red",
     dict(base, **{"hooks/other.py": OTHER, "lint/run_baits.baseline": "hooks/other.py\n"}), 0, "1 in baseline")

src = open(RUNNER).read()
assert re.search(r"^BASELINE_MAX = \d+$", src, re.M), "the pin must exist to be baited"
pinned0 = re.sub(r"^BASELINE_MAX = \d+$", "BASELINE_MAX = 0", src, flags=re.M)
bait("BAIT R9 a baseline above the pinned maximum is RED",
     dict(base, **{"hooks/other.py": OTHER, "lint/run_baits.baseline": "hooks/other.py\n"}),
     1, "pinned maximum", runner_src=pinned0)
bait("BAIT R10 a baseline entry that is now covered is reported as DEBT PAID",
     dict(base, **{"lint/run_baits.baseline": "gates/09-x/thing.py\n"}), 0, "DEBT PAID")
bait("BAIT R11 an extensionless executable with a shebang is a form, and unbaited is RED",
     dict(base, **{"scripts/discipline": "#!/usr/bin/env python3\nprint('tool')\n"}), 1, "scripts/discipline")
bait("BAIT R12 a .PY file in upper case is a form", dict(base, **{"hooks/UPPER.PY": OTHER}), 1, "hooks/UPPER.PY")
bait("BAIT R13 a GREEN over a baseline says DEBT, not 'every form is baited'",
     dict(base, **{"hooks/other.py": OTHER, "lint/run_baits.baseline": "hooks/other.py\n"}), 0, "DEBT, not baited")

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
