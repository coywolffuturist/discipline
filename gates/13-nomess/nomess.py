#!/usr/bin/env python3
"""nomess — the sweep, as a command.

Gate 13. Run it before claiming done. Exit 0 clean, 1 mess.

WHY A COMMAND AND NOT A HABIT. Across one day this gate recorded 37 encounters
and went N/A zero times, which is the signature of a standard too easy to meet:
if a gate can never fail to apply and always passes, it is not running. In the
same day it missed a browser lock held for 25 minutes on another machine, caught
only while listing residue by hand.

TWO SCOPES, deliberately separate:

  --repo    hygiene that must ALWAYS hold. Wired into lint/all.sh, so it fails
            the build. Cheap, local, no network.
  --remote  state on other machines: locks held, scratch directories, processes
            started. NOT wired into the build — it needs the network and a
            build must not depend on another host being up. Run it before
            claiming done.

Default runs both and reports separately.
"""
import argparse, io, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# The remote host is CONFIGURABLE, not hardcoded. This repo is public and the
# prose in it carefully says "the second machine"; the code named the host.
# With nothing set, the remote sweep reports UNCONFIGURED rather than pretending
# a clean result for a host it never contacted.
DEN = os.environ.get("COYWOLF_REMOTE_HOST", "")
findings = []


SKIP_DEPLOY = False


def bad(scope, msg):
    findings.append((scope, msg))


def sh(cmd, timeout=25):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def repo_sweep():
    os.chdir(REPO)

    # 1. dead symlinks. A link to nothing reads as a live path.
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files + dirs:
            p = os.path.join(root, f)
            if os.path.islink(p) and not os.path.exists(p):
                bad("repo", "dead symlink: %s -> %s" % (p, os.readlink(p)))

    # 2. debris. Backup copies are what a repo exists to replace; leaving them
    #    means the next reader cannot tell which file is live.
    DEBRIS = re.compile(r"\.(bak|orig|rej|tmp|swp)$|\.pre-[a-z0-9-]+$|~$|\.VERIFIED$")
    tracked = set(sh("git ls-files").splitlines())
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            p = os.path.relpath(os.path.join(root, f))
            if DEBRIS.search(f):
                bad("repo", "debris file: %s (a repo replaces backup copies)" % p)

    # 3. deployed-copy drift. The CONTRACT says install outward, never edit the
    #    deployed copy alone — and twice in one day the deployed conductor went
    #    stale while the consistency checker read green.
    pairs = [("CONDUCTOR.md", "~/.claude/skills/discipline/SKILL.md")]
    for f in sorted(os.listdir("hooks")) if os.path.isdir("hooks") else []:
        if f.endswith(".py"):
            pairs.append((os.path.join("hooks", f), "~/.claude/hooks/" + f))
    for src, dst in pairs:
        d = os.path.expanduser(dst)
        if not os.path.exists(d):
            # NOT a failure on a machine that has no install. This check
            # asserts THIS estate's deployed state; for anyone else it is
            # unknowable, and refusing their build for it is a false denial.
            if not os.path.isdir(os.path.expanduser("~/.claude/hooks")):
                global SKIP_DEPLOY
                SKIP_DEPLOY = True
                continue
            bad("repo", "NOT DEPLOYED: %s has no copy at %s" % (src, dst))
        elif open(src, "rb").read() != open(d, "rb").read():
            bad("repo", "DRIFT: %s differs from its deployed copy %s — install outward" % (src, dst))

    # A repo-internal DUPLICATE is a drift source the deployed-copy check above
    # cannot see: that one compares repo to INSTALLED, never repo to repo. Four
    # hook files existed twice — once under hooks/, once beside their GATE.md —
    # and two had already diverged, with the REGISTERED copy carrying a sentence
    # its own gate file declares false. They are symlinks now; this refuses a
    # plain copy so the class cannot come back.
    import glob
    for h in sorted(glob.glob(os.path.join(REPO, "hooks", "*.py"))):
        b = os.path.basename(h)
        twins = glob.glob(os.path.join(REPO, "gates", "*", b))
        if twins and not os.path.islink(h) and not all(os.path.islink(t) for t in twins):
            bad("repo", "DUPLICATE: hooks/%s and %s are both real files; one must "
                        "be a symlink or they will drift"
                        % (b, os.path.relpath(twins[0], REPO)))


    # NO MACHINE OR ACCOUNT NAMES IN A PUBLIC TREE. The prose here was scrubbed
    # and the CODE was not: a reviewer found the host name in three files and
    # the operator's account name hardcoded in a fourth. `skill_share.sh` scrubs
    # `skills/` and never touched the gate-directory copies, so two sources
    # diverged again.
    import glob as _g
    # DERIVED FROM THE ENVIRONMENT, never written down. Two earlier attempts
    # failed: writing the names literally made this file itself the leak, and
    # splitting them across a `+` did not help, because the substring is still
    # in the source. Exempting the detector was never an option — that is how a
    # checker goes blind exactly where it matters.
    #
    # So it asks the machine who it belongs to. That leaks nothing, and it
    # generalises: it protects WHOEVER runs it, not one account this file names.
    import socket
    NAMES = set()
    acct = os.path.basename(os.path.expanduser("~"))
    if len(acct) > 3:
        NAMES.add(acct.lower())
    host = socket.gethostname().split(".")[0]
    if len(host) > 3:
        NAMES.add(host.lower())
    # ONLY WHAT GIT TRACKS. "Published" means tracked, not present: the first
    # version scanned the whole tree and flagged a gitignored .pyc that can
    # never reach the remote. Scanning what will actually be pushed is both
    # correct and faster.
    for rel in sh("git -C %s ls-files" % REPO).splitlines():
        f = os.path.join(REPO, rel)
        if not os.path.isfile(f) or os.path.islink(f):
            continue
        try:
            txt = io.open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for nm in NAMES:
            if nm in txt.lower():
                bad("repo", "PUBLISHES A PRIVATE NAME: %s contains %r" % (rel, nm))


def done_sweep():
    """Single-copy work. NOT a build check — see below.

    On 2026-09-01 a critical guard fix lived as a modified-but-uncommitted file
    on one machine that was about to be retired: one disk failure from gone. So
    this is worth checking. But it is NOT a repo invariant, and putting it in the
    build deadlocked instantly — the pre-commit hook runs the build, the build
    failed because work was uncommitted, so nothing could ever be committed.
    Uncommitted work is the normal state of working. It is only a defect when you
    are about to claim done."""
    os.chdir(REPO)
    # NOT fixed offsets: sh() strips its output, which eats the leading space of
    # the first porcelain line and shifts every column by one. That produced
    # "ONTRACT.md" on this tool's own first run.
    for line in sh("git status --porcelain").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2:
            continue
        code, path = parts[0], parts[1]
        if code == "??":
            bad("done", "untracked, so it exists in one place only: %s" % path)
        elif "M" in code:
            bad("done", "uncommitted change, so the EDIT exists in one place only: %s" % path)


SKIP_REMOTE = False


def remote_sweep():
    # UNCONFIGURED IS NOT DIRTY, AND IT IS NOT CLEAN EITHER. With no host set
    # this used to report "cannot reach  — remote state UNSWEPT", a FAILURE for
    # anyone who simply has no second machine. Same false-denial class the repo
    # sweep just had.
    global SKIP_REMOTE
    if not DEN:
        SKIP_REMOTE = True
        return

    if sh("ssh -o ConnectTimeout=8 -o BatchMode=yes %s 'echo up' 2>/dev/null" % DEN) != "up":
        bad("remote", "cannot reach %s — remote state UNSWEPT, not clean" % DEN)
        return

    lock = sh("ssh %s '~/.coywolf/scripts/gui-browser-lock who 2>/dev/null'" % DEN)
    if lock and "free" not in lock.lower():
        bad("remote", "browser lock still held: %s" % lock[:90])

    # List plainly, filter HERE. Two failures taught this in one sitting:
    # the remote shell is zsh, which ERRORS on a glob with no matches and aborts
    # the whole command, so one stale pattern silently disabled every other one;
    # then a `find` with nested quotes was mangled passing through python, the
    # local shell, ssh and the remote shell. Both reported CLEAN while scratch
    # sat there. Send no quotes, and do the matching where there is no shell.
    SCRATCH = re.compile(r"^(audit|sb\d|sbv|sbd|g1[0-9]|verify_pub|pubcheck|nm|probe_)")
    listing = sh("ssh %s ls -1 /tmp" % DEN)
    for s in listing.splitlines():
        if SCRATCH.match(s.strip()):
            bad("remote", "scratch left behind: /tmp/%s" % s.strip())

    # A window opened for a one-off task and never closed is remote state too.
    wins = sh("ssh %s 'osascript -e \"tell application \\\"Google Chrome\\\" to count windows\" 2>/dev/null'" % DEN)
    if wins.isdigit() and int(wins) > 0:
        bad("remote", "%s Chrome window(s) open on the remote host" % wins)


def main():
    ap = argparse.ArgumentParser(description="gate 13 nomess — the sweep, as a command")
    ap.add_argument("--repo", action="store_true", help="repo hygiene only — build-safe, no network")
    ap.add_argument("--remote", action="store_true", help="state on other machines")
    ap.add_argument("--done", action="store_true", help="single-copy work, before claiming done")
    a = ap.parse_args()
    picked = a.repo or a.remote or a.done
    scopes = []
    if a.repo or not picked:
        repo_sweep(); scopes.append("repo")
    if a.remote or not picked:
        remote_sweep(); scopes.append("remote")
    if a.done or not picked:
        done_sweep(); scopes.append("done")

    if not findings:
        # SKIPPED IS NOT PASSED. `SKIP_DEPLOY` was set when ~/.claude/hooks is
        # absent and then read NOWHERE, so on a machine with no install this
        # printed "PASS — no stale deployed copy" having compared zero copies.
        # That is the exact failure this repo exists to name: a check reporting
        # health it does not have. lint/all.sh already documents that this
        # should skip; the code never did it.
        if SKIP_REMOTE and "remote" in scopes:
            print("\033[33mSKIP\033[0m  nomess — %s clean, but the REMOTE sweep "
                  "ran nothing:" % " + ".join(s for s in scopes if s != "remote"))
            print("      COYWOLF_REMOTE_HOST is unset, so no second machine was "
                  "contacted. Remote state is UNKNOWN, not clean.")
            return 2
        if SKIP_DEPLOY:
            print("\033[33mSKIP\033[0m  nomess — repo hygiene passed, but the "
                  "deployed-copy check compared NOTHING:")
            print("      no ~/.claude/hooks on this machine. Install state is "
                  "UNKNOWN here, not clean.")
            return 2
        print("\033[32mPASS\033[0m  nomess — %s clean" % " + ".join(scopes))
        return 0
    print("\033[31mFAIL\033[0m  nomess — %d item(s):" % len(findings))
    w = max(len(s) for s, _ in findings)
    for s, m in findings:
        print("      %-*s  %s" % (w, s, m))
    return 1


if __name__ == "__main__":
    sys.exit(main())
