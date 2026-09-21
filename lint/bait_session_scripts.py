#!/usr/bin/env python3
"""bait_session_scripts.py — scripts/session_gate.sh and scripts/memory_lint.sh, seen to fire.

Two SessionStart-class scripts. Neither can block anything, so the only way
they fail is SILENTLY: saying nothing when there is something to say, or
saying it about the wrong directory.

memory_lint is baited against a FAKE $HOME. That is not a convenience --
it is the test. Its MEM_DIR is DERIVED (`-Users-<name>` is the home path with
slashes turned to dashes) because the literal path carried the operator name
into a repo with a remote and the leak gate refused the commit. A derivation
that resolves wrongly is indistinguishable from a clean scan, so the bait
builds a home from scratch and checks the script finds the planted defects
inside it.

The dead-zone and malformed-link checks are baited with PLANTED defects rather
than trusted: on 2026-09-21 this script's own WARN_BYTES was wrong by 2x and it
had certified MEMORY.md clean through 8 KB of unread entries, and its dead-link
check could not see a link truncated mid-path because a truncated link does not
match the pattern it searches for.

LABELS ARE SG-PREFIXED, NOT S, AND MUST STAY THAT WAY. baits_pair.py reads
the identifier after "BAIT " as a repo-GLOBAL check id:
    BAIT = re.compile(r"^BAIT\s+([A-Z]{1,4}[0-9]{1,3}[a-z]?)\b", re.I)
These were S1..S10 for one commit and silently claimed coverage of gate 01's
ste checks S1-S7, which this file tests nothing about -- a FALSE coverage
claim, caught only because bait_baits_pair plants a check called S9 and its
planted defect stopped being detected. A bait label is not a local name.
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT = os.path.join(ROOT, "scripts", "memory_lint.sh")
GATE = os.path.join(ROOT, "scripts", "session_gate.sh")

bad = []
total = 0


def bait(label, cond, detail=""):
    global total
    total += 1
    print("  %s %-60s %s" % ("ok " if cond else "XX ", label, str(detail).replace("\n", " ")[:36]))
    if not cond:
        bad.append(label)


def fake_home():
    """A $HOME with the Claude Code project dir the script DERIVES, not one we
    hand it. If the derivation is wrong, nothing below is found."""
    h = tempfile.mkdtemp(prefix="bait-home-")
    proj = "-" + h.lstrip("/").replace("/", "-")
    mem = os.path.join(h, ".claude", "projects", proj, "memory")
    os.makedirs(mem)
    return h, mem


def run_lint(home):
    r = subprocess.run(["bash", LINT], capture_output=True, text=True,
                       env=dict(os.environ, HOME=home), timeout=60)
    return r.returncode, r.stdout + r.stderr


# ------------------------------------------------- memory_lint: derivation
home, mem = fake_home()
open(os.path.join(mem, "MEMORY.md"), "w").write("# Router\n> ok **[A](b.md)** — hook\n")
open(os.path.join(mem, "b.md"), "w").write("x\n")
rc, out = run_lint(home)
bait("BAIT SG1 memory_lint: a tiny clean store is SILENT", rc == 0 and out.strip() == "", out[:36])
shutil.rmtree(home, ignore_errors=True)

# ------------------------------------------------- memory_lint: dead link
home, mem = fake_home()
open(os.path.join(mem, "MEMORY.md"), "w").write("# Router\n> x **[A](missing_page.md)** — hook\n")
rc, out = run_lint(home)
bait("BAIT SG2 memory_lint: a DEAD link is named", "missing_page.md" in out, out[:36])
shutil.rmtree(home, ignore_errors=True)

# ------------------------------------ memory_lint: link truncated mid-path
# INVISIBLE to the dead-link check: it searches for (name.md), and a truncated
# link does not match that pattern, so it is not a dead link, it is not a link.
home, mem = fake_home()
open(os.path.join(mem, "MEMORY.md"), "w").write(
    "# Router\n> x **[A](decision_something_long_that_got_cut_mid_pa\n")
rc, out = run_lint(home)
bait("BAIT SG3 memory_lint: a MALFORMED link is caught", "MALFORMED" in out.upper(), out[:36])
shutil.rmtree(home, ignore_errors=True)

# ------------------------------------------- memory_lint: the loader cut
home, mem = fake_home()
line = "> x **[ENTRY %03d](b.md)** — %s\n"
pad = "".join(line % (i, "y" * 120) for i in range(1, 260))
open(os.path.join(mem, "MEMORY.md"), "w").write("# Router\n" + pad)
open(os.path.join(mem, "b.md"), "w").write("x\n")
rc, out = run_lint(home)
bait("BAIT SG4 memory_lint: entries PAST THE LOADER CUT are named",
     "LOADER CUT" in out.upper() or "PAST THE" in out.upper(), out[:36])
bait("BAIT SG5 memory_lint: it says a write-back below the cut is a no-op",
     "no-op" in out or "never loaded" in out)
shutil.rmtree(home, ignore_errors=True)

# ------------------------------------------------------------ session_gate
r = subprocess.run(["bash", GATE], capture_output=True, text=True, timeout=90)
g = r.stdout + r.stderr
bait("BAIT SG6 session_gate: exits 0 so it can never block a session", r.returncode == 0)
bait("BAIT SG7 session_gate: the CONDUCTOR block is UNCONDITIONAL",
     "CONDUCTOR IS ON" in g, g[:36])
bait("BAIT SG8 session_gate: ka123n is named as the outer loop", "ka123n" in g)
bait("BAIT SG9 session_gate: the two MCP levers still print", "mind_grep" in g)
bait("BAIT SG10 session_gate: it does NOT teach the retired ask-dont-pour bundle",
     "ask-dont-pour" not in g)

print()
if bad:
    print("BAIT: FAIL  %d/%d" % (total - len(bad), total))
    for b in bad:
        print("   failed: %s" % b)
    sys.exit(1)
print("BAIT: PASS  %d/%d" % (total, total))
