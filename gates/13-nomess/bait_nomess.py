#!/usr/bin/env python3
"""bait_nomess.py — nomess.py, seen to go red, and seen to SKIP rather than pass.

Gate 13's own file says: bait it after any change to what it looks for. This
copies the real nomess.py into a throwaway repo (it derives REPO from its own
location) under a private HOME, so the deployed-copy check compares nothing and
must say so — a clean control is rc 2 SKIP here, never rc 0.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FORM = os.path.join(HERE, "nomess.py")
GIT_ENV = dict(GIT_AUTHOR_NAME="bait", GIT_AUTHOR_EMAIL="bait@example",
               GIT_COMMITTER_NAME="bait", GIT_COMMITTER_EMAIL="bait@example")

bad = []
total = 0


def repo():
    d = tempfile.mkdtemp(prefix="nomess-bait-")
    home = os.path.join(d, "acctzq7home")   # the account name the tool will derive
    os.makedirs(home)
    r = os.path.join(d, "repo")
    os.makedirs(os.path.join(r, "gates", "13-nomess"))
    shutil.copy(FORM, os.path.join(r, "gates", "13-nomess", "nomess.py"))
    open(os.path.join(r, "README.md"), "w").write("clean\n")
    git(r, "init", "-q")
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "x", "--no-verify")
    return d, home, r


def git(r, *a):
    subprocess.run(["git", "-C", r] + list(a), env=dict(os.environ, **GIT_ENV),
                   capture_output=True, check=True)


def run(home, r, *flags):
    env = dict(os.environ, HOME=home, NOMESS_ACCOUNT="acctzq7home")
    env.pop("COYWOLF_REMOTE_HOST", None)
    p = subprocess.run([sys.executable, os.path.join(r, "gates", "13-nomess", "nomess.py")] + list(flags),
                       capture_output=True, text=True, env=env, timeout=60)
    return p.returncode, p.stdout + p.stderr


def bait(label, want_rc, want_text, setup=None, flags=("--repo",)):
    global total
    total += 1
    d, home, r = repo()
    if setup:
        setup(r, home)
    rc, out = run(home, r, *flags)
    shutil.rmtree(d, ignore_errors=True)
    ok = rc == want_rc and want_text.lower() in out.lower()
    print("  %s %-62s rc=%s" % ("ok " if ok else "XX ", label, rc))
    if not ok:
        bad.append(label)
        print("      wanted rc=%s containing %r\n      got: %s" % (want_rc, want_text, out.strip()[:240]))


def dead_link(r, home):
    os.symlink("/nonexistent/target", os.path.join(r, "gone"))


def debris(r, home):
    open(os.path.join(r, "notes.md.bak"), "w").write("x\n")


def private_name(r, home):
    open(os.path.join(r, "doc.md"), "w").write("built on acctzq7home yesterday\n")
    git(r, "add", "doc.md")


def duplicate(r, home):
    os.makedirs(os.path.join(r, "hooks")); os.makedirs(os.path.join(r, "gates", "01-x"))
    open(os.path.join(r, "hooks", "h.py"), "w").write("x\n")
    open(os.path.join(r, "gates", "01-x", "h.py"), "w").write("x\n")


def untracked(r, home):
    open(os.path.join(r, "loose.txt"), "w").write("x\n")


def modified(r, home):
    open(os.path.join(r, "README.md"), "a").write("more\n")


bait("BAIT N0 a clean repo with no install is SKIP (rc 2), not PASS", 2, "compared NOTHING")
bait("BAIT N1 a dead symlink is red", 1, "dead symlink", dead_link)
bait("BAIT N2 a .bak file is red", 1, "debris", debris)
bait("BAIT N3 the account name in a tracked file is red", 1, "PUBLISHES A PRIVATE NAME", private_name)
bait("BAIT N4 a hook existing twice as plain files is red", 1, "DUPLICATE", duplicate)
bait("BAIT N5 --remote with no host configured is SKIP, not clean", 2, "COYWOLF_REMOTE_HOST is unset",
     flags=("--remote",))
bait("BAIT N6 --done with an untracked file is red", 1, "untracked", untracked, flags=("--done",))
bait("BAIT N7 --done with an uncommitted edit is red", 1, "uncommitted", modified, flags=("--done",))
bait("BAIT N8 --done on a committed tree is clean (rc 0)", 0, "clean", flags=("--done",))


# A reviewer's mutations on 2026-09-02 left every bait above green while the
# deployed-copy check, the debris list, the duplicate rule and the name scan
# were each neutered. These bait what those baits did not.
def staged_only(r, home):
    open(os.path.join(r, "new_form.py"), "w").write("x\n")
    git(r, "add", "new_form.py")


def with_install(r, home, drift=True):
    # a HOME that HAS an install, so the deployed-copy check runs
    os.makedirs(os.path.join(home, ".claude", "hooks"))
    os.makedirs(os.path.join(r, "hooks"))
    open(os.path.join(r, "hooks", "h.py"), "w").write("print(1)\n")
    if drift:
        open(os.path.join(home, ".claude", "hooks", "h.py"), "w").write("print(2)\n")
    open(os.path.join(r, "CONDUCTOR.md"), "w").write("c\n")
    os.makedirs(os.path.join(home, ".claude", "skills", "discipline"))
    open(os.path.join(home, ".claude", "skills", "discipline", "SKILL.md"), "w").write("c\n")


def not_deployed(r, home):
    with_install(r, home, drift=False)


def orig_and_tilde(r, home):
    open(os.path.join(r, "a.orig"), "w").write("x\n")
    open(os.path.join(r, "b.py~"), "w").write("x\n")


def one_twin_linked(r, home):
    os.makedirs(os.path.join(r, "hooks")); os.makedirs(os.path.join(r, "gates", "01-x")); os.makedirs(os.path.join(r, "gates", "02-x"))
    open(os.path.join(r, "hooks", "h.py"), "w").write("x\n")
    open(os.path.join(r, "gates", "01-x", "h.py"), "w").write("x\n")
    os.symlink("../../hooks/h.py", os.path.join(r, "gates", "02-x", "h.py"))


def upper_name(r, home):
    open(os.path.join(r, "doc.md"), "w").write("built on ACCTZQ7HOME yesterday\n")
    git(r, "add", "doc.md")


bait("BAIT N9 --done with a file staged but never committed is red", 1, "staged but not committed",
     staged_only, flags=("--done",))


def staged_delete(r, home):
    git(r, "rm", "-q", "README.md")


def staged_rename(r, home):
    git(r, "mv", "README.md", "READ.md")


def unstaged_delete(r, home):
    os.remove(os.path.join(r, "README.md"))


bait("BAIT N16 --done with a staged delete is red", 1, "deleted but not committed", staged_delete, flags=("--done",))
bait("BAIT N17 --done with a staged rename is red", 1, "renamed but not committed", staged_rename, flags=("--done",))
bait("BAIT N18 --done with an unstaged delete is red", 1, "deleted but not committed", unstaged_delete, flags=("--done",))
bait("BAIT N10 a deployed copy that differs from the repo copy is DRIFT", 1, "DRIFT", with_install)
bait("BAIT N11 an install with no copy of a hook is NOT DEPLOYED", 1, "NOT DEPLOYED", not_deployed)
bait("BAIT N12 .orig and ~ files are debris too", 1, "b.py~", orig_and_tilde)
bait("BAIT N13 one twin linked and one real is still a DUPLICATE", 1, "DUPLICATE", one_twin_linked)
bait("BAIT N14 the account name in UPPER CASE is still published", 1, "PUBLISHES A PRIVATE NAME", upper_name)


def fresh_word(r, home):
    open(os.path.join(r, "doc.md"), "w").write("a fresh start\n")
    git(r, "add", "doc.md")


total += 0
_env_backup = os.environ.get("NOMESS_ACCOUNT")
# HOME's basename must NOT be treated as the account name
d0, home0, r0 = repo(); fresh_word(r0, home0)
env = dict(os.environ, HOME=home0); env.pop("NOMESS_ACCOUNT", None); env.pop("COYWOLF_REMOTE_HOST", None)
home_fresh = os.path.join(d0, "fresh"); os.rename(home0, home_fresh)
p0 = subprocess.run([sys.executable, os.path.join(r0, "gates", "13-nomess", "nomess.py"), "--repo"],
                    capture_output=True, text=True, env=dict(env, HOME=home_fresh), timeout=60)
total += 1
ok0 = "fresh" not in (p0.stdout + p0.stderr).split("PUBLISHES")[-1] and "PUBLISHES A PRIVATE NAME" not in p0.stdout + p0.stderr
print("  %s %-62s rc=%s" % ("ok " if ok0 else "XX ", "BAIT N19 a HOME named 'fresh' is not an account name to hunt for", p0.returncode))
if not ok0:
    bad.append("N19"); print("      got: %s" % (p0.stdout + p0.stderr).strip()[:200])
shutil.rmtree(d0, ignore_errors=True)


import socket
HOST = socket.gethostname().split(".")[0]


def host_name(r, home):
    open(os.path.join(r, "doc.md"), "w").write("deployed on %s last night\n" % HOST)
    git(r, "add", "doc.md")


if len(HOST) > 3:
    bait("BAIT N15 the machine's own host name in a tracked file is published", 1,
         "PUBLISHES A PRIVATE NAME", host_name)
else:
    # Under the tool's own 4-character floor, so it cannot protect this name
    # either. Said loudly, not counted: a bait that cannot run here is not a
    # bait that failed. (This laptop's host name is three characters.)
    print("  --  BAIT N15 SKIPPED: host name %r is under the 4-char floor, so nomess "
          "cannot protect it on this machine and the bait cannot run" % HOST)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
