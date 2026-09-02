#!/usr/bin/env python3
"""bait_gate18.py — the gate 18 code form (the estate pre-push hook), seen to refuse and to pass.

The review record is a git NOTE on the reviewed commit (ref `reviews`),
written by the reviewer as its last act. The push gate reads the pushed
tip's note: no note, or a verdict that is not SURVIVED, refuses. There was no
bait for this block before 2026-09-02; every "verified" on the page was the
author's word. This builds guarded scratch repos and real bare remotes and
pushes through the REAL hook that `core.hooksPath` registers, with TMPDIR
pointed away from the live one.

SKIPS (rc 2) where the estate hook is not registered — a stranger's machine
must not go red for not owning it.
"""
import os, shutil, subprocess, sys, tempfile

HOOK = os.path.expanduser("~/.git-hooks/pre-push")
r = subprocess.run(["git", "config", "--global", "core.hooksPath"], capture_output=True, text=True)
if not os.path.exists(HOOK) or os.path.expanduser(r.stdout.strip()) != os.path.dirname(HOOK):
    print("SKIP  the estate pre-push hook is not registered on this machine; nothing to bait")
    sys.exit(2)

GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="bait", GIT_AUTHOR_EMAIL="bait@example",
               GIT_COMMITTER_NAME="bait", GIT_COMMITTER_EMAIL="bait@example")
bad = []
total = 0


def git(cwd, *a, env=None, check=True):
    p = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, text=True, env=env or GIT_ENV)
    if check and p.returncode != 0:
        raise RuntimeError("git %s: %s" % (a[0], p.stderr.strip()[:200]))
    return p


def repo(guarded=True):
    d = tempfile.mkdtemp(prefix="gate18-bait-")
    bare = os.path.join(d, "remote.git"); w = os.path.join(d, "w")
    git(d, "init", "-q", "--bare", bare)
    git(d, "init", "-q", w)
    if guarded:
        open(os.path.join(w, ".gate18-guarded"), "w").close()
    open(os.path.join(w, "README.md"), "w").write("clean\n")
    git(w, "add", "-A"); git(w, "commit", "-q", "-m", "base", "--no-verify")
    git(w, "remote", "add", "origin", bare)
    return d, w, bare


def push(d, w, *refspec, env_extra=None):
    env = dict(GIT_ENV, TMPDIR=d)
    env.pop("GATE18_BYPASS", None)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(["git", "-C", w, "push", "origin"] + list(refspec or ("HEAD:main",)),
                       capture_output=True, text=True, env=env, timeout=120)
    return p.returncode, p.stdout + p.stderr


def note(w, sha, text):
    git(w, "notes", "--ref=reviews", "add", "-f", "-m", text, sha)


def head(w):
    return git(w, "rev-parse", "HEAD").stdout.strip()


def bait(label, cond, detail=""):
    global total
    total += 1
    print("  %s %-66s %s" % ("ok " if cond else "XX ", label, detail.strip().replace("\n", " ")[:50]))
    if not cond:
        bad.append(label)


d, w, bare = repo()
rc, out = push(d, w)
bait("BAIT G1 a guarded tip with NO note is refused", rc != 0 and "GATE 18" in out, out)
note(w, head(w), "SURVIVED refuter 2026-09-02 bait")
rc, out = push(d, w)
bait("BAIT G2 a SURVIVED note on the tip licenses the push", rc == 0 and "licensed by the note" in out, out)
bait("BAIT G3 ...and the licence names the note", "SURVIVED" in out, out)
rc, out = push(d, w)
bait("BAIT G4 the same commit pushes again — a note is not consumed", rc == 0, out)
open(os.path.join(w, "more.md"), "w").write("x\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "after", "--no-verify")
rc, out = push(d, w)
bait("BAIT G5 a new commit whose PARENT has the note is refused", rc != 0 and "GATE 18" in out, out)
git(w, "commit", "-q", "--amend", "-m", "after, amended", "--no-verify")
note(w, head(w), "SURVIVED refuter 2026-09-02")
sha_before = head(w)
git(w, "commit", "-q", "--amend", "-m", "amended again after review", "--no-verify")
rc, out = push(d, w)
bait("BAIT G6 an amend after the note voids it — the sha moved", rc != 0 and head(w) != sha_before, out)
note(w, head(w), "REFUTED refuter 2026-09-02 a real failure")
rc, out = push(d, w)
bait("BAIT G7 a REFUTED note refuses, and says so", rc != 0 and "REFUTED" in out, out)
note(w, head(w), "LANDMINES cold-reader 2026-09-02")
rc, out = push(d, w)
bait("BAIT G8 a LANDMINES note refuses", rc != 0, out)
note(w, head(w), "CLEAN cold-reader 2026-09-02")
rc, out = push(d, w, env_extra={"TMPDIR": ""})
bait("BAIT G9 a CLEAN note is a licence, and nothing depends on TMPDIR", rc == 0, out)
rc, out = push(d, w, env_extra={"GATE18_BYPASS": "1"})
bait("BAIT G10 GATE18_BYPASS still says so out loud", rc == 0 and "bypassed" in out, out)
# two remotes, one reviewed commit
bare2 = os.path.join(d, "remote2.git"); git(d, "init", "-q", "--bare", bare2)
git(w, "remote", "add", "second", bare2)
p = subprocess.run(["git", "-C", w, "push", "second", "HEAD:main"], capture_output=True, text=True, env=dict(GIT_ENV, TMPDIR=d))
bait("BAIT G11 the same reviewed commit is licensed to a SECOND remote", p.returncode == 0, p.stdout + p.stderr)
# a lightweight tag at a blob: the gate passes it to the scan
blob = git(w, "hash-object", "-w", "--stdin", env=GIT_ENV) if False else None
p = subprocess.run(["git", "-C", w, "hash-object", "-w", "--stdin"], input="just a blob\n", capture_output=True, text=True, env=GIT_ENV)
git(w, "tag", "blobtag", p.stdout.strip())
rc, out = push(d, w, "refs/tags/blobtag")
bait("BAIT G12 a tag at a blob is not gated (the scan still runs)", rc == 0, out)
shutil.rmtree(d, ignore_errors=True)

d, w, bare = repo()
note(w, head(w), "HARDENED mechanism-auditor 2026-09-02")
rc, out = push(d, w)
bait("BAIT G15 a HARDENED note is a licence", rc == 0, out)
mid = head(w)   # noted, pushed below as part of main
open(os.path.join(w, "n.md"), "w").write("x\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "n", "--no-verify")
unnoted = head(w)
open(os.path.join(w, "n2.md"), "w").write("x\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "n2", "--no-verify")
note(w, head(w), "SURVIVED refuter 2026-09-02"); push(d, w)
git(w, "tag", "legacy", unnoted)
rc, out = push(d, w, "--tags")
bait("BAIT G16 a tag at an UNNOTED commit the remote already holds is not gated", rc == 0 and "🛑" not in out and "licensed by" not in out, out)
rc, out = push(d, w, unnoted + ":refs/heads/old")
bait("BAIT G16b the same commit under a new branch name is not gated", rc == 0 and "🛑" not in out and "licensed by" not in out, out)
bait("BAIT G17 an up-to-date push is not gated and burns nothing", rc == 0 and "🛑" not in out and "licensed by" not in out, out)
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G18 the record itself can be published: pushing refs/notes/reviews is not gated", rc == 0 and "🛑" not in out and "licensed by" not in out, out)
rc, out = push(d, w, "--mirror")
bait("BAIT G19 --mirror of a reviewed repo is licensed, notes ref and all", rc == 0, out)
# the record travels: a clone with no local notes reads the remote's
c = os.path.join(d, "clone"); subprocess.run(["git", "clone", "-q", bare, c], env=GIT_ENV, check=True)
open(os.path.join(c, "c.md"), "w").write("x\n"); git(c, "add", "-A"); git(c, "commit", "-q", "-m", "c", "--no-verify")
rc, out = push(d, c)
bait("BAIT G20 a clone's new commit still needs its own note", rc != 0, out)
git(c, "reset", "-q", "--hard", "HEAD~1")
bare3 = os.path.join(d, "remote3.git"); git(d, "init", "-q", "--bare", bare3); git(c, "remote", "add", "third", bare3)
p = subprocess.run(["git", "-C", c, "push", "third", "HEAD:main"], capture_output=True, text=True, env=dict(GIT_ENV, TMPDIR=d))
bait("BAIT G21 a clone pushing a commit reviewed elsewhere finds the note on ITS remote", p.returncode == 0, p.stdout + p.stderr)
shutil.rmtree(d, ignore_errors=True)

d, w, bare = repo()
blob = subprocess.run(["git", "-C", w, "hash-object", "-w", "--stdin"], input="\n\n   SURVIVED refuter 2026-09-02 after two blank lines\n", capture_output=True, text=True, env=GIT_ENV).stdout.strip()
git(w, "notes", "--ref=reviews", "add", "-f", "-C", blob, head(w))
rc, out = push(d, w)
bait("BAIT G22 a note whose verdict sits after blank lines and spaces is read", rc == 0, out)
git(w, "checkout", "-q", "-b", "b2"); open(os.path.join(w, "b2.md"), "w").write("x\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "b2", "--no-verify")
git(w, "checkout", "-q", "-b", "b3"); open(os.path.join(w, "b3.md"), "w").write("x\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "b3", "--no-verify")
rc, out = push(d, w, "b2", "b3")
bait("BAIT G23 two unlicensed refs are BOTH named in one refusal", rc != 0 and "b2" in out and "b3" in out, out)
shutil.rmtree(d, ignore_errors=True)

d, w, bare = repo(guarded=False)
rc, out = push(d, w)
bait("BAIT G13 an unmarked repo is not gated and prints no gate line", rc == 0 and "🛑" not in out and "licensed by" not in out, out)
shutil.rmtree(d, ignore_errors=True)

d, w, bare = repo()
d2, w2, bare2 = repo()
note(w2, head(w2), "SURVIVED refuter 2026-09-02")
rc, out = push(d, w)
bait("BAIT G14 a review in ANOTHER repo licenses nothing here", rc != 0, out)
shutil.rmtree(d, ignore_errors=True); shutil.rmtree(d2, ignore_errors=True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
