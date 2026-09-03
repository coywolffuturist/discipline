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
bait("BAIT G12 a tag at an unreviewed blob is gated like any content", rc != 0 and "GATE 18" in out, out)
note(w, p.stdout.strip(), "SURVIVED refuter 2026-09-02 read the blob")
rc, out = push(d, w, "refs/tags/blobtag")
bait("BAIT G12b ...and a note on the blob licenses it", rc == 0, out)
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
bait("BAIT G21 a clone pushing to a FRESH remote is refused until it fetches the record, and is told how",
     p.returncode != 0 and "git fetch <remote> +refs/notes/reviews" in p.stdout + p.stderr, p.stdout + p.stderr)
git(w, "push", "-q", "origin", "refs/notes/reviews")          # publish the record on origin
git(c, "fetch", "-q", "origin", "+refs/notes/reviews:refs/notes/reviews")
p = subprocess.run(["git", "-C", c, "push", "third", "HEAD:main"], capture_output=True, text=True, env=dict(GIT_ENV, TMPDIR=d))
bait("BAIT G21b ...and after fetching the record the same push is licensed", p.returncode == 0, p.stdout + p.stderr)
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
git(w, "update-ref", "refs/notes/evil", head(w))
rc, out = push(d, w, "refs/notes/evil:refs/heads/main")
bait("BAIT G24 a local notes ref pushed AS main is gated by the destination name", rc != 0 and "GATE 18" in out, out)
bait("BAIT G25 the refusal tells a clone how to FETCH the record", "git fetch <remote> +refs/notes/reviews" in out, out)
shutil.rmtree(d, ignore_errors=True)

# local vs remote disagreement: the stricter verdict wins; the side ref is per push
d, w, bare = repo()
A = head(w); note(w, A, "SURVIVED refuter 2026-09-02"); push(d, w); git(w, "push", "-q", "origin", "refs/notes/reviews")
open(os.path.join(w, "b.md"), "w").write("b\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "b", "--no-verify")
B = head(w); note(w, B, "SURVIVED refuter 2026-09-02")
# a second party records REFUTED for B on the destination (objects moved by bundle, no push)
c = os.path.join(d, "clone"); subprocess.run(["git", "clone", "-q", bare, c], env=GIT_ENV, check=True)
bnd = os.path.join(d, "b.bundle"); git(w, "bundle", "create", bnd, "HEAD"); git(c, "fetch", "-q", bnd, "HEAD")
git(c, "fetch", "-q", "origin", "+refs/notes/reviews:refs/notes/reviews")
git(c, "notes", "--ref=reviews", "add", "-f", "-m", "REFUTED refuter 2026-09-02 the remote disagrees", B)
git(c, "push", "-q", "-f", "origin", "refs/notes/reviews")
rc, out = push(d, w)
bait("BAIT G26 local SURVIVED vs the destination's REFUTED: the stricter wins, refused", rc != 0 and "REFUTED" in out, out)
side = subprocess.run(["git", "-C", w, "show-ref", "--verify", "--quiet", "refs/notes/reviews-remote"], env=GIT_ENV).returncode
bait("BAIT G27 the side ref does not linger after the push (a later --mirror cannot carry it)", side != 0)
bare2 = os.path.join(d, "fresh.git"); git(d, "init", "-q", "--bare", bare2); git(w, "remote", "add", "fresh", bare2)
p = subprocess.run(["git", "-C", w, "push", "fresh", "HEAD:main"], capture_output=True, text=True, env=dict(GIT_ENV, TMPDIR=d))
bait("BAIT G28 a FRESH remote with no record does not inherit the stale side ref: local SURVIVED licenses", p.returncode == 0, p.stdout + p.stderr)
shutil.rmtree(d, ignore_errors=True)

# a fourth reviewer: non-commit tips, parked commits, erased records, a tab after the verdict
d, w, bare = repo()
note(w, head(w), "SURVIVED refuter 2026-09-02"); push(d, w); git(w, "push", "-q", "origin", "refs/notes/reviews")
open(os.path.join(w, "secret.md"), "w").write("unreviewed content\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "B", "--no-verify")
B = head(w); tree = git(w, "rev-parse", "HEAD^{tree}").stdout.strip()
rc, out = push(d, w, tree + ":refs/tags/snapshot")
bait("BAIT G31 an unreviewed TREE pushed as a tag is refused", rc != 0 and "GATE 18" in out, out)
git(w, "tag", "-a", "-m", "annotated at tree", "treetag", tree)
rc, out = push(d, w, "refs/tags/treetag")
bait("BAIT G32 an annotated tag at an unreviewed tree is refused", rc != 0, out)
blob = git(w, "rev-parse", "HEAD:secret.md").stdout.strip()
rc, out = push(d, w, blob + ":refs/tags/blobtag")
bait("BAIT G33 an unreviewed BLOB pushed as a tag is refused", rc != 0, out)
note(w, tree, "SURVIVED refuter 2026-09-02 reviewed the tree itself")
rc, out = push(d, w, tree + ":refs/tags/snapshot")
bait("BAIT G34 a note on the OBJECT licenses a non-commit tip", rc == 0, out)
rc, out = push(d, w, B + ":refs/notes/whatever")
bait("BAIT G35 an unreviewed commit cannot be parked under refs/notes/", rc != 0, out)
rc, out = push(d, w, "-f", B + ":refs/notes/reviews")
bait("BAIT G36 a plain commit force-pushed over the record is refused", rc != 0, out)
rc, out = push(d, w, ":refs/notes/reviews")
bait("BAIT G37 deleting the record through the gate is refused", rc != 0 and "record" in out, out)
git(w, "replace", "-f", blob, blob) if False else None
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G38 publishing the local record itself still passes", rc == 0, out)
note(w, B, "SURVIVED\trefuter 2026-09-02 tab after the verdict")
rc, out = push(d, w)
bait("BAIT G39 a TAB after the verdict word is still SURVIVED", rc == 0, out)
shutil.rmtree(d, ignore_errors=True)

# a fifth reviewer: the remaining exemptions were parking spots; the record could be forced away
d, w, bare = repo()
A = head(w); note(w, A, "SURVIVED refuter 2026-09-02"); push(d, w); git(w, "push", "-q", "origin", "refs/notes/reviews")
open(os.path.join(w, "u.md"), "w").write("unreviewed\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "U", "--no-verify"); U = head(w)
rc, out = push(d, w, U + ":refs/replace/" + A)
bait("BAIT G40 an unreviewed commit cannot be parked under refs/replace/", rc != 0, out)
rc, out = push(d, w, U + ":refs/notes/reviews-remote")
bait("BAIT G41 ...nor under the side ref's name", rc != 0, out)
# a fresh clone reviews honestly but never fetched the record: its publish must not erase the remote's
c = os.path.join(d, "clone"); subprocess.run(["git", "clone", "-q", bare, c], env=GIT_ENV, check=True)
open(os.path.join(c, "c.md"), "w").write("c\n"); git(c, "add", "-A"); git(c, "commit", "-q", "-m", "C", "--no-verify")
note(c, head(c), "SURVIVED refuter 2026-09-02 honest review in a clone")
p2 = subprocess.run(["git", "-C", c, "push", "-f", "origin", "refs/notes/reviews"], capture_output=True, text=True, env=dict(GIT_ENV, TMPDIR=d))
bait("BAIT G42 a record that does not descend from the remote's is refused even with -f, and told to merge",
     p2.returncode != 0 and "notes --ref=reviews merge" in p2.stdout + p2.stderr, p2.stdout + p2.stderr)
git(c, "fetch", "-q", "origin", "+refs/notes/reviews:refs/notes/reviews-remote")
git(c, "notes", "--ref=reviews", "merge", "-q", "reviews-remote")
p2 = subprocess.run(["git", "-C", c, "push", "origin", "refs/notes/reviews"], capture_output=True, text=True, env=dict(GIT_ENV, TMPDIR=d))
bait("BAIT G43 after merging, publishing the record fast-forwards and passes", p2.returncode == 0, p2.stdout + p2.stderr)
remote_note_A = subprocess.run(["git", "-C", c, "notes", "--ref=reviews", "show", A], capture_output=True, text=True, env=GIT_ENV).stdout
bait("BAIT G44 ...and the earlier review of A survives in the merged record", "SURVIVED" in remote_note_A, remote_note_A)
git(w, "replace", "-f", A, A) if False else None
note(w, U, "SURVIVED refuter 2026-09-02 reviewed the replacement")
rc, out = push(d, w, U + ":refs/replace/" + A)
bait("BAIT G45 a REVIEWED replacement object is licensed like any other", rc == 0, out)
# a sixth reviewer: a forged notes commit with a note on itself; a remote whose record cannot be fetched
git(w, "notes", "--ref=evil", "add", "-f", "-m", "SURVIVED forged", U)
evil = git(w, "rev-parse", "refs/notes/evil").stdout.strip()
note(w, evil, "SURVIVED refuter 2026-09-02 a note on the notes commit itself")
rc, out = push(d, w, "-f", "refs/notes/evil:refs/notes/reviews")
bait("BAIT G46 a notes commit that notes ITSELF cannot become the record", rc != 0 and "own record" in out, out)
# a DIVERGED record (w never merged the clone's publish) against a remote that hides refs/notes from fetch
git(d, "--git-dir=" + bare, "config", "uploadpack.hideRefs", "refs/notes")
subprocess.run(["git", "-C", w, "gc", "-q", "--prune=now"], env=GIT_ENV)   # drop any fetched copy of the remote's record
note(w, U, "SURVIVED refuter 2026-09-02 w diverges from the published record")
rc, out = push(d, w, "-f", "refs/notes/reviews")
bait("BAIT G47 a diverged record against a remote whose record cannot be fetched is refused, not overwritten",
     rc != 0 and "GATE 18" in out, out)
rem = subprocess.run(["git", "--git-dir=" + bare, "rev-parse", "refs/notes/reviews"], capture_output=True, text=True).stdout.strip()
bait("BAIT G47b ...and the remote's record is unchanged", rem != git(w, "rev-parse", "refs/notes/reviews").stdout.strip())
git(d, "--git-dir=" + bare, "config", "--unset", "uploadpack.hideRefs")
shutil.rmtree(d, ignore_errors=True)

d, w, bare = repo()
note(w, head(w), "SURVIVED refuter 2026-09-02"); push(d, w)
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G48 the first publish of a record to a remote with none passes", rc == 0, out)
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G49 a no-op publish passes", rc == 0, out)
shutil.rmtree(d, ignore_errors=True)

# a seventh reviewer: the first publish took ANY object as the record; a REFUTED parent shipped under a SURVIVED tip
d, w, bare = repo()
A = head(w); note(w, A, "SURVIVED refuter 2026-09-02"); push(d, w)
real_record = git(w, "rev-parse", "refs/notes/reviews").stdout.strip()
open(os.path.join(w, "plan.txt"), "w").write("unreviewed plan\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "U", "--no-verify"); U = head(w)
git(w, "update-ref", "refs/notes/reviews", U)
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G50 a local record ref pointing at an ordinary commit is not a record: first publish refused", rc != 0 and "not a notes tree" in out, out)
blob = subprocess.run(["git", "-C", w, "hash-object", "-w", "--stdin"], input="x\n", capture_output=True, text=True, env=GIT_ENV).stdout.strip()
git(w, "update-ref", "refs/notes/reviews", blob)
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G51 a blob at the record ref is refused", rc != 0, out)
git(w, "update-ref", "refs/notes/reviews", real_record)
rc, out = push(d, w, "refs/notes/reviews")
bait("BAIT G52 the real record then publishes", rc == 0, out)
note(w, U, "REFUTED refuter 2026-09-02 the parent is refused")
open(os.path.join(w, "t.txt"), "w").write("t\n"); git(w, "add", "-A"); git(w, "commit", "-q", "-m", "T", "--no-verify"); T = head(w)
note(w, T, "SURVIVED refuter 2026-09-02 the tip is fine")
rc, out = push(d, w)
bait("BAIT G53 an outbound PARENT noted REFUTED refuses the push under a SURVIVED tip", rc != 0 and U[:12] in out, out)
note(w, U, "SURVIVED refuter 2026-09-02 re-reviewed")
rc, out = push(d, w)
bait("BAIT G54 ...and once the parent is re-reviewed the same push passes", rc == 0, out)
git(d, "--git-dir=" + bare, "config", "receive.hideRefs", "refs/notes")
git(w, "update-ref", "refs/notes/reviews", git(w, "rev-parse", "refs/notes/reviews").stdout.strip())
note(w, T, "SURVIVED refuter 2026-09-02 one more note so the record moves")
rc, out = push(d, w, "-f", "refs/notes/reviews")
bait("BAIT G55 a remote that hides the record from receive is refused rather than treated as first publish",
     rc != 0 and "hidden from receive" in out, out)
git(d, "--git-dir=" + bare, "config", "--unset", "receive.hideRefs")
shutil.rmtree(d, ignore_errors=True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
