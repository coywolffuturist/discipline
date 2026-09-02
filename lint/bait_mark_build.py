#!/usr/bin/env python3
"""bait_mark_build.py — hooks/mark_build.py, seen to fire and seen to stay quiet.

mark_build.py writes the three flags every Stop hook reads. It has two failure
modes and both were hit in one day: firing on a read-only turn (trained into
noise, then ignored) and staying quiet on a build (no table asked for). Each
case below runs the real hook with a private TMPDIR and reads the flags back.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "mark_build.py")
FLAGS = ("coywolf-build-turn.flag", "coywolf-prior-owed.flag", "coywolf-posterior-owed.flag")

bad = []
total = 0


def fire(payload):
    d = tempfile.mkdtemp(prefix="mark-build-bait-")
    r = subprocess.run([sys.executable, HOOK], input=payload, capture_output=True, text=True,
                       env=dict(os.environ, TMPDIR=d), timeout=30)
    present = [f for f in FLAGS if os.path.exists(os.path.join(d, f))]
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, present


def bait(label, payload, want_flags):
    global total
    total += 1
    rc, present = fire(payload)
    ok = rc == 0 and (sorted(present) == sorted(FLAGS) if want_flags else not present)
    print("  %s %-62s %s" % ("ok " if ok else "XX ", label, "flags" if present else "quiet"))
    if not ok:
        bad.append(label)
        print("      rc=%s flags=%s wanted %s" % (rc, present, "all three" if want_flags else "none"))


def bash(cmd):
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})


def edit(tool, path):
    return json.dumps({"tool_name": tool, "tool_input": {"file_path": path}})


# SCOPE, stated. On 2026-09-02 the operator ruled the reminder REPO/BUILD ONLY
# ("tables are only for when we're touching a repo or pushing a build"), and the
# deployed copy was narrowed the same morning while the repo copy lagged. These
# baits hold under BOTH: version control, service management and package
# installs mark a build; quoted verbs, sinks and notes paths do not. Whether a
# plain `rm` or a Write marks a build is exactly what the ruling changed, so it
# is NOT baited here — add those baits with the hook version that decides them.
bait("BAIT M1 `git commit` at the start of a command marks a build", bash("git commit -m x"), True)
bait("BAIT M2 `git push` after `&&` marks a build", bash("cd /x && git push origin main"), True)
bait("BAIT M3 a package install marks a build", bash("brew install jq"), True)
bait("BAIT M4 a verb quoted as DATA does not", bash('grep "git commit" file.txt'), False)
bait("BAIT M5 a read-only pipeline with a /dev/null sink does not",
     bash("cat f | sort >/dev/null"), False)
bait("BAIT M6 a scratch-buffer redirect does not", bash("ls -la > /tmp/nv.txt"), False)
bait("BAIT M7 a bare `ls` does not", bash("ls -la"), False)
bait("BAIT M8 Edit to a notes path is not a build", edit("Edit", "/x/memory/feedback_x.md"), False)
bait("BAIT M9 a git call on a notes path is STILL a build",
     bash("git commit -m x MEMORY.md"), True)
bait("BAIT M10 Read is never a build", edit("Read", "/x/src/a.py"), False)
bait("BAIT M11 malformed stdin exits 0 and marks nothing", "{not json", False)
bait("BAIT M12 every flag is written — one consumer cannot silence another",
     bash("launchctl kickstart -k x"), True)
# Each verb family the ruling KEPT, one by one: a reviewer dropped them one
# family at a time and the baits above stayed green.
bait("BAIT M13 `git add` marks a build", bash("git add -A"), True)
bait("BAIT M14 `git rebase` marks a build", bash("git rebase main"), True)
bait("BAIT M15 `pip install` marks a build", bash("pip install requests"), True)
bait("BAIT M16 `npm install` marks a build", bash("npm install"), True)
bait("BAIT M17 `launchctl load` marks a build", bash("launchctl load ~/Library/LaunchAgents/x.plist"), True)
bait("BAIT M18 a `sudo` prefix does not hide the verb", bash("sudo git commit -m x"), True)
bait("BAIT M19 the verb is a whole word: `git commitx` does not", bash("git commitx"), False)
bait("BAIT M20 a verb after a newline marks a build", bash("ls\ngit push"), True)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
