#!/usr/bin/env python3
r"""bait_session_scripts.py — scripts/session_gate.sh and scripts/memory_lint.sh, seen to fire.

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

# ── scripts/link_scan.py — memory_lint's link ACCOUNTING ──────────────────────
# Split out of memory_lint.sh because inline python with backticks breaks the
# shell however the heredoc is quoted. It belongs here rather than in a bait of
# its own: it is the third script in this family, and the defect it exists for
# is the one this file's docstring already names -- the dead-link check searches
# for WELL-FORMED links, so a link truncated mid-path is invisible to it. Not a
# dead link, not a link, the pattern never fires.
LINK_SCAN = os.path.realpath(os.path.join(ROOT, "scripts", "link_scan.py"))


def scan(body):
    """Run the real script the way the shell runs it, and parse its accounting."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(body)
        p = f.name
    try:
        out = subprocess.run([sys.executable, LINK_SCAN, p],
                             capture_output=True, text=True).stdout
    finally:
        os.unlink(p)
    head = out.strip().splitlines()[0].split()
    return int(head[0]), int(head[1]), int(head[2]), out


# CONTROL FIRST. A scanner that reports zero skips on a planted defect and one
# that never read the file print the same three numbers.
o, w, k, _ = scan("- [One](one.md) hook\n- [Two](sub/two.md) hook\n")
bait("BAIT LS1 link_scan: CONTROL — a clean index has ZERO skipped",
     (o, w, k) == (2, 2, 0), "opens=%d wf=%d skipped=%d" % (o, w, k))

o, w, k, out = scan("- [Good](good.md)\n- [Cut](truncated-mid-pa\n")
bait("BAIT LS2 link_scan: a TRUNCATED opener is counted as skipped", k == 1, "skipped=%d" % k)
bait("BAIT LS3 link_scan: and the skip is NAMED, not just tallied",
     "line 2" in out, out.replace("\n", " ")[:50])

o, w, k, _ = scan("- [A](a.md)\n- [B](b.md)\n- [C](cut\n- [D](also-cut\n")
bait("BAIT LS4 link_scan: the accounting balances, opens == wellformed + skipped",
     o == w + k, "opens=%d wf=%d skipped=%d" % (o, w, k))

# The router legitimately contains a literal [text](url) inside a code span, in
# the entry about giving him bare URLs. Counting it would warn every session,
# and a check that cries wolf every session gets skimmed.
o, w, k, _ = scan("- `[text](url)` does not render\n- [Real](real.md)\n")
bait("BAIT LS5 link_scan: a link inside a CODE SPAN is not counted",
     (o, w, k) == (1, 1, 0), "opens=%d wf=%d skipped=%d" % (o, w, k))

# Code spans are BLANKED, not deleted, so line numbers stay true to the file
# the reader will actually open.
_, _, k, out = scan("`[a](b)`\n\n\n- [Cut](truncated\n")
bait("BAIT LS6 link_scan: line numbers survive code-span blanking",
     k == 1 and "line 4" in out, out.replace("\n", " ")[:50])

for label, argv in (("a missing file", [LINK_SCAN, "/nonexistent/nope.md"]),
                    ("no argument", [LINK_SCAN])):
    r2 = subprocess.run([sys.executable] + argv, capture_output=True, text=True)
    bait("BAIT LS%d link_scan: %s prints 0 0 0 rather than crashing"
         % (7 if "missing" in label else 8, label),
         r2.returncode == 0 and r2.stdout.strip() == "0 0 0",
         "rc=%d %r" % (r2.returncode, r2.stdout.strip()))

# PINNED, not fixed: "well-formed" means a .md target, so a plain URL link is
# reported as skipped. Right for the router, where every real entry points at a
# page; wrong anywhere URL links are ordinary. Pinned so a change is noticed.
o, w, k, _ = scan("- [Site](https://example.com) hook\n")
bait("BAIT LS9 link_scan: PINNED — a URL target counts as skipped, not well-formed",
     k == 1, "skipped=%d (pinned)" % k)

# ── scripts/skill_share.sh — THE SCRUBBER ────────────────────────────────────
# Adopted 2026-09-22. It was tracked in no repo, and install.sh CALLED it at
# line ~45 without ever copying it, so a fresh machine invoked a missing file.
# It is the thing that strips machine-specific blocks, private memory slugs,
# [[wikilinks]] and private script paths out of the skill masters before they
# become shareable. Baiting "does it run" would be worthless: the property that
# matters is that private references DO NOT SURVIVE it.
SHARE = os.path.join(ROOT, "scripts", "skill_share.sh")
_sd = tempfile.mkdtemp(prefix="share-bait-")
_src, _out = os.path.join(_sd, "skills", "demo"), os.path.join(_sd, "out")
os.makedirs(_src)
# It DERIVES the publishable list from the conductor and refuses without one --
# "refusing to publish a list I cannot derive". A fixture with no conductor
# makes it exit 1, and then every "private string is absent" row below passes
# against an empty directory. That is what the SS1 control caught.
os.makedirs(os.path.join(_sd, "skills", "discipline"))
open(os.path.join(_sd, "skills", "discipline", "SKILL.md"), "w",
     encoding="utf-8").write("# Conductor\n\nsee skills/demo for the demo gate\n")
open(os.path.join(_src, "SKILL.md"), "w", encoding="utf-8").write(
    "# Demo skill\n\n"
    "KEEPME the public rule survives.\n\n"
    "See [[feedback_private_rule_11]] for the reasoning.\n"
    "Sources: reference_a_private_page_that_must_not_ship\n"
    # A literal /Users/<someone>/ path, not this machine's $HOME: the bait must pass on
    # any checkout, including one run under a temporary HOME outside /Users.
    "Run /Users/someone/.coywolf/scripts/private_thing.sh first.\n\n" +
    "Ask PRIVHOSTFIXTURE before you render.\n\n" +
    "## This environment\n\n"
    "PRIVATEBLOCK machine-specific command here.\n")
# The private rules live OUTSIDE the repo (~/.config/discipline/scrub.sed). The
# bait brings its own fixture, so it passes on a clean checkout and never reads
# the maintainer's real rules.
_priv = os.path.join(_sd, "scrub.sed")
open(_priv, "w", encoding="utf-8").write("s/PRIVHOSTFIXTURE/a second machine/g\n")
_env = dict(os.environ, DISCIPLINE_PRIVATE_SCRUB=_priv)
_r = subprocess.run(["bash", SHARE, os.path.join(_sd, "skills"), _out],
                    capture_output=True, text=True, env=_env)
# Read the SCRUBBED SKILL only. The emitted CONTRACT.md documents the transform
# and therefore contains the literal "Sources:" -- scanning it made a row fail
# against the contract's own description of what it strips.
_txt = open(os.path.join(_out, "demo", "SKILL.md"), encoding="utf-8",
            errors="replace").read() if os.path.exists(
            os.path.join(_out, "demo", "SKILL.md")) else ""

# CONTROL FIRST: it must have produced output at all, or every "absent" row
# below passes against an empty directory.
bait("BAIT SS1 skill_share PRODUCED shareable output", len(_txt) > 20,
     "rc=%d bytes=%d %s" % (_r.returncode, len(_txt), _r.stderr[:40]))
bait("BAIT SS2 public content SURVIVES", "KEEPME" in _txt, _txt[:40])
bait("BAIT SS3 the private memory slug is GONE",
     "feedback_private_rule_11" not in _txt, "slug leaked")
bait("BAIT SS4 the Sources: pointer line is GONE", "Sources:" not in _txt, "pointer leaked")
# PINNED, NOT FIXED. The header claims it strips private script paths. It does
# not: it HOME-ANONYMISES them, /Users/<name>/.coywolf/... -> ~/.coywolf/...
# so the operator's identity goes but the private script's existence and name
# are published. Whether that is acceptable is his disclosure call, not mine,
# so this row records the real behaviour rather than asserting the claim.
bait("BAIT SS5 PINNED: the private path is home-anonymised, NOT stripped",
     "~/.coywolf/scripts/private_thing.sh" in _txt
     and "/Users/" not in _txt, "behaviour changed — re-read the header claim")
bait("BAIT SS6 the machine-specific block is GONE",
     "PRIVATEBLOCK" not in _txt, "environment block leaked")
bait("BAIT SS7 a PRIVATE rule (kept outside the repo) fires",
     "PRIVHOSTFIXTURE" not in _txt and "Ask a second machine" in _txt, "private rule did not apply")
_out2 = os.path.join(_sd, "out-norules")
_r2 = subprocess.run(["bash", SHARE, os.path.join(_sd, "skills"), _out2], capture_output=True, text=True,
                     env=dict(os.environ, DISCIPLINE_PRIVATE_SCRUB=os.path.join(_sd, "absent.sed")))
bait("BAIT SS8 with NO private rules it REFUSES, says why, and writes nothing",
     _r2.returncode != 0 and "no private scrub rules" in _r2.stderr and not os.path.exists(os.path.join(_out2, "demo")),
     "rc=%d %s" % (_r2.returncode, _r2.stderr[:60]))
shutil.rmtree(_sd, ignore_errors=True)

print()
if bad:
    print("BAIT: FAIL  %d/%d" % (total - len(bad), total))
    for b in bad:
        print("   failed: %s" % b)
    sys.exit(1)
print("BAIT: PASS  %d/%d" % (total, total))
