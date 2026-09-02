#!/usr/bin/env python3
"""lint/run_baits — every code form's baits RUN, and are SEEN to go red.

Gate 09's rule: a check with no bait that was seen to fail is an assertion, not
evidence. `lint/baits_pair.py` is the REGISTRY half of that rule — it pairs a
check label with a bait label and executes nothing. A refuter proved on
2026-09-01 that a bait file whose first statement kills the interpreter passes
the registry. This is the RUNNING half, the half with a verb in it.

WHAT IT DOES.

1. DISCOVERS the code forms. A form is any tracked `.py` or `.sh` file that is
   not itself a bait, a test, or the build door. Discovery is `git ls-files`,
   never a directory list: the registry once globbed `gates/`, `lint/` and not
   `hooks/`, and a check in `hooks/` reported GREEN. A file git tracks cannot
   be missed by being written in a directory nobody enumerated.

2. RUNS every bait file and reads its summary. A bait file passes only when it
   exits 0 AND prints a `PASS n/m` line with n == m >= 1. A file that exits 0
   silently, prints 0/0, or crashes is RED. That is the hole this closes: a
   bait that never ran reads exactly like a bait that ran.

3. MAPS baits to forms by EXECUTION, not by mention. Every bait runs with a
   `sitecustomize` on PYTHONPATH (and a BASH_ENV for shell forms) that appends
   the real path of every python entry point and every imported module under
   this tree to a trace file. A form is covered when some bait's trace holds
   its path, or the path of a byte-identical copy. The first version mapped by
   basename MENTION in the bait's source; a docstring that names a file would
   have covered it. No manifest either way: `skill_share.sh`'s hardcoded list
   was wrong five times.

4. REFUSES an uncovered form, unless it is listed in `run_baits.baseline`. The
   baseline is debt. It may only SHRINK: the count is pinned in code below, so
   appending a line fails until a human lowers the number.

WHAT IT DELIBERATELY DOES NOT CHECK, stated after a reviewer showed each:
- whether a bait is any GOOD. Executing a form with `--help` counts as
  coverage; a `PASS` line that lies passes. What this removes is the silent
  case. Bait quality is what a mutation pass measures, and the reviewer's
  first pass left 33 mutations green — those baits were then strengthened.
- the INDEX. It reads the worktree, as `git ls-files` names files and the
  disk supplies content; a staged change that differs from the worktree is
  not what was certified. Run it on a clean tree before committing.
- `#!/bin/sh` scripts. The shell trace rides BASH_ENV, which sh ignores.
  Every shell form here is `#!/bin/bash`.
- the baseline entries. They are DEBT and the GREEN line says so.

    RUN_BAITS_ROOT=<dir>   scan another checkout (used by bait_run_baits.py)
"""
import hashlib, os, re, shutil, subprocess, sys, tempfile

ROOT = os.environ.get("RUN_BAITS_ROOT") or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(ROOT, "lint", "run_baits.baseline")

# THE BASELINE MAY ONLY SHRINK. Lower this when debt is paid; never raise it.
BASELINE_MAX = 8

FORM_EXT = (".py", ".sh", ".bash")
BAIT_NAME = re.compile(r"^(bait_.*\.py|baits\.py|test_gates\.py)$")
# The door, this runner, and this runner's own bait are not forms and not
# baits: the bait runs this file in temp checkouts, so including it here would
# recurse.
NOT_A_FORM = {"lint/all.sh", "lint/run_baits.py"}
NOT_A_BAIT = {"lint/bait_run_baits.py"}
SUMMARY = re.compile(r"^\s*(?:BAITS?|TESTS)\s*:?\s+PASS\s+(\d+)/(\d+)\s*$", re.M)


def tracked():
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True)
    if r.returncode != 0:
        print("RED  git ls-files failed under %s; nothing was discovered." % ROOT)
        sys.exit(1)
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def is_form(rel):
    """A form is a tracked .py/.sh/.bash file, OR a tracked executable, OR a
    tracked file that begins with a shebang. Extension alone missed
    `scripts/discipline` (python, shebang, +x, no extension) on 2026-09-02."""
    low = rel.lower()
    if low.endswith(FORM_EXT):
        return True
    p = os.path.join(ROOT, rel)
    try:
        if os.access(p, os.X_OK) and os.path.isfile(p):
            return True
        with open(p, "rb") as fh:
            return fh.read(2) == b"#!"
    except OSError:
        return False


def discover():
    forms, baits = [], []
    for rel in tracked():
        base = os.path.basename(rel)
        if BAIT_NAME.match(base):
            if rel not in NOT_A_BAIT:
                baits.append(rel)
        elif rel not in NOT_A_FORM and is_form(rel):
            forms.append(rel)
    return sorted(forms), sorted(baits)


# THE HASH IS TAKEN AT TRACE TIME, while the file still exists. Several baits
# copy the form into a throwaway checkout, run the copy, and delete the
# checkout; a trace holding only the PATH could not be matched afterwards, and
# nomess, quotes and baits_pair all read as unexecuted on the first run.
SITECUSTOMIZE = r'''
import atexit, hashlib, os, sys
_p = os.environ.get("RUN_BAITS_TRACE")
_root = os.environ.get("RUN_BAITS_ROOT_REAL", "")
def _dump():
    if not _p:
        return
    seen = set()
    if sys.argv and sys.argv[0] and sys.argv[0] not in ("-c", "-m", "-"):
        seen.add(os.path.realpath(sys.argv[0]))
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f:
            f = os.path.realpath(f)
            if f.startswith(_root + os.sep) or f.startswith("/private/var/") or f.startswith("/var/") or f.startswith("/tmp/"):
                seen.add(f)
    lines = []
    for s in sorted(seen):
        try:
            h = hashlib.sha256(open(s, "rb").read()).hexdigest()
        except Exception:
            continue
        lines.append(h + " " + s)
    try:
        with open(_p, "a") as fh:
            for l in lines:
                fh.write(l + "\n")
    except Exception:
        pass
atexit.register(_dump)
'''
# While BASH_ENV is being sourced, `$0` is still "bash": the script has not
# started. A DEBUG trap fires on the script's FIRST command, where
# BASH_SOURCE[1] is the script, then removes itself. Verified on bash 3.2,
# including a script that calls another script.
BASH_TRACE = r'''
_rb_trace() {
  local f="${BASH_SOURCE[1]:-}"
  if [ -n "${RUN_BAITS_TRACE:-}" ] && [ -n "$f" ] && [ -f "$f" ]; then
    local h
    if command -v shasum >/dev/null 2>&1; then h=$(shasum -a 256 "$f" 2>/dev/null | cut -d' ' -f1)
    else h=$(sha256sum "$f" 2>/dev/null | cut -d' ' -f1); fi
    [ -n "$h" ] && printf '%s %s/%s\n' "$h" "$(cd "$(dirname "$f")" 2>/dev/null && pwd -P)" "$(basename "$f")" >> "$RUN_BAITS_TRACE" 2>/dev/null
  fi
}
trap '_rb_trace; trap - DEBUG' DEBUG
'''


def trace_env(tmpdir, trace_file):
    open(os.path.join(tmpdir, "sitecustomize.py"), "w").write(SITECUSTOMIZE)
    open(os.path.join(tmpdir, "bash_trace.sh"), "w").write(BASH_TRACE)
    env = dict(os.environ)
    env["PYTHONPATH"] = tmpdir + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["BASH_ENV"] = os.path.join(tmpdir, "bash_trace.sh")
    env["RUN_BAITS_TRACE"] = trace_file
    env["RUN_BAITS_ROOT_REAL"] = os.path.realpath(ROOT)
    return env


def digest(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError:
        return None


def coverage(forms, traces):
    """forms: rel paths. traces: {bait rel: set("<sha256> <real path>")}."""
    by_real, by_hash = {}, {}
    for f in forms:
        p = os.path.join(ROOT, f)
        by_real.setdefault(os.path.realpath(p), []).append(f)
        h = digest(p)
        if h:
            by_hash.setdefault(h, []).append(f)
    covered, orphans = {}, []
    for b, rows in traces.items():
        hit = set()
        for row in rows:
            h, _, p = row.partition(" ")
            for f in by_real.get(p, []):
                hit.add(f)
            for f in by_hash.get(h, []):
                hit.add(f)
        if not hit:
            orphans.append(b)
        for f in hit:
            covered.setdefault(f, []).append(b)
    return covered, orphans


def run_bait(rel, env, trace_file):
    path = os.path.join(ROOT, rel)
    cmd = [sys.executable, path] if rel.endswith(".py") else ["bash", path]
    # Its own session, so a timeout kills the whole tree: a reviewer left a
    # grandchild `sleep` alive past the kill.
    p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, env=env, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=600)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, 9)
        except OSError:
            pass
        p.communicate()
        return False, "timed out after 600s; its process group was killed", 0, 0

    class R:
        returncode = p.returncode
        stdout = out
        stderr = ""
    r = R()
    out = (r.stdout or "") + (r.stderr or "")
    m = None
    for m in SUMMARY.finditer(out):
        pass
    if r.returncode != 0:
        return False, "rc=%d\n%s" % (r.returncode, out.strip()[-600:]), 0, 0
    if not m:
        return False, "exit 0 but NO `PASS n/m` summary line — did it run anything?", 0, 0
    n, total = int(m.group(1)), int(m.group(2))
    if n < 1 or n != total:
        return False, "summary %d/%d — a bait file must see every bait red and at least one" % (n, total), n, total
    return True, "", n, total


def main():
    forms, baits = discover()
    if not forms:
        print("RED  no code form was discovered under %s." % ROOT)
        print("     A runner scanning nothing is not a pass.")
        return 1
    debt = set()
    if os.path.exists(BASELINE):
        debt = {l.strip() for l in open(BASELINE) if l.strip() and not l.startswith("#")}

    red = False
    ran = 0
    seen = 0
    traces = {}
    tmpdir = tempfile.mkdtemp(prefix="run-baits-")
    try:
        for b in baits:
            trace_file = os.path.join(tmpdir, "trace-%d" % len(traces))
            ok, why, n, total = run_bait(b, trace_env(tmpdir, trace_file), trace_file)
            ran += 1
            seen += n
            paths = set()
            if os.path.exists(trace_file):
                paths = {l.strip() for l in open(trace_file) if l.strip()}
            traces[b] = paths
            print("  %s %-44s %s" % ("ok " if ok else "XX ", b,
                                     ("%d/%d red, %d file(s) executed" % (n, total, len(paths))) if ok else ""))
            if not ok:
                red = True
                print("      " + why.replace("\n", "\n      "))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    covered, orphans = coverage(forms, traces)

    uncovered = [f for f in forms if f not in covered]
    new = [f for f in uncovered if f not in debt]
    print("run baits: %d form(s), %d bait file(s) ran, %d bait(s) seen red, "
          "%d form(s) uncovered (%d in baseline)"
          % (len(forms), ran, seen, len(uncovered), len(uncovered) - len(new)))
    for o in orphans:
        print("   orphan bait: %s executed no form. A bait for nothing baits nothing." % o)
    if new:
        red = True
        print("RED  %d form(s) that NO bait file executed:" % len(new))
        for f in new:
            print("     %s" % f)
        print("     Write a bait_<name>.py that RUNS %s and sees it go red." % os.path.basename(new[0]))
    if len(debt) > BASELINE_MAX:
        red = True
        print("RED  the baseline holds %d entr(ies); the pinned maximum is %d."
              % (len(debt), BASELINE_MAX))
        print("     A baseline may only SHRINK. Lower BASELINE_MAX in lint/run_baits.py"
              " when debt is paid; never raise it to silence a new form.")
    paid = sorted(debt - set(uncovered))
    if paid:
        print("   DEBT PAID: %s now baited. Remove from the baseline." % ", ".join(paid))
    if red:
        return 1
    if uncovered:
        print("GREEN  every form outside the baseline was executed by a bait that passed;"
              " %d form(s) in the baseline are DEBT, not baited." % len(uncovered))
    else:
        print("GREEN  every form was executed by a bait that passed, and the baseline is empty.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
