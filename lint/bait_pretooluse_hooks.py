#!/usr/bin/env python3
"""bait_pretooluse_hooks.py — hooks/hook_prior_pre.py and hooks/hook_conductor_pre.py, seen to fire.

The two PreToolUse forms. Both exist because a DESIGN obligation wired to an
END event can only ever report the miss it exists to prevent: gate 08's Stop
hook literally says "a prior was owed BEFORE it". These fire while the action
is still pending.

Both WARN and never deny, so the bait's job is to prove three things that are
easy to get wrong in opposite directions:
  - it speaks when it should (a build action),
  - it is SILENT when it should be (reads, wrong tool, repeat within the
    self-limit) -- a guard trained into noise gets switched off, which is the
    failure these hooks exist to prevent,
  - it FAILS OPEN on malformed input. A gate that raises blocks everything.

They differ in channel, deliberately, and the bait pins that: hook_prior_pre
emits a JSON envelope on stdout; hook_conductor_pre writes plain text to
stderr. A reviewer swapping either would leave the harness silent.

TMPDIR is redirected per case so _flags.path() lands in a scratch dir and no
real session flag is read or clobbered.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIOR = os.path.join(ROOT, "hooks", "hook_prior_pre.py")
COND = os.path.join(ROOT, "hooks", "hook_conductor_pre.py")

BUILD = "git commit -m x"
READ = "ls -la /tmp"

bad = []
total = 0


def bait(label, cond, detail=""):
    global total
    total += 1
    print("  %s %-60s %s" % ("ok " if cond else "XX ", label, str(detail)[:38]))
    if not cond:
        bad.append(label)


def run(hook, d, tool="Bash", cmd=BUILD, session="baitsess", raw=None):
    payload = raw if raw is not None else json.dumps(
        {"session_id": session, "tool_name": tool,
         "tool_input": ({"command": cmd} if tool == "Bash"
                        else {"file_path": "/tmp/x.md", "content": "hi"})})
    r = subprocess.run([sys.executable, hook], input=payload, capture_output=True,
                       text=True, env=dict(os.environ, TMPDIR=d), timeout=30)
    return r.returncode, r.stdout, r.stderr


# ---------------------------------------------------------------- gate 08 PRE
d = tempfile.mkdtemp(prefix="bait-priorpre-")
rc, out, err = run(PRIOR, d)
spoke = False
env_ok = False
if out.strip():
    try:
        o = json.loads(out)
        env_ok = o.get("suppressOutput") is True
        spoke = "GATE 08" in json.dumps(o)
    except Exception as e:
        bait("BAIT P0 prior-pre: stdout is JSON", False, e)
bait("BAIT P1 prior-pre: a build command is asked for the prior", rc == 0 and spoke, out[:38])
bait("BAIT P2 prior-pre: the envelope sets suppressOutput", env_ok)
rc, out2, _ = run(PRIOR, d)
bait("BAIT P3 prior-pre: second build in the same session is quiet", out2.strip() == "")
shutil.rmtree(d, ignore_errors=True)

d = tempfile.mkdtemp(prefix="bait-priorpre-")
rc, out, _ = run(PRIOR, d, cmd=READ)
bait("BAIT P4 prior-pre: a plain read is NOT a build", rc == 0 and out.strip() == "", out[:38])
rc, out, _ = run(PRIOR, d, tool="Write")
bait("BAIT P5 prior-pre: a non-Bash tool is ignored", rc == 0 and out.strip() == "")
rc, out, _ = run(PRIOR, d, raw="not json at all")
bait("BAIT P6 prior-pre: malformed payload FAILS OPEN", rc == 0)
shutil.rmtree(d, ignore_errors=True)

# ------------------------------------------------------------- conductor PRE
d = tempfile.mkdtemp(prefix="bait-cond-")
rc, out, err = run(COND, d, session="condsess")
bait("BAIT C1 conductor: first build action announces the conductor",
     rc == 0 and "CONDUCTOR ENTRY" in err, err[:38])
bait("BAIT C2 conductor: it names ka123n SELECT", "ka123n" in err)
bait("BAIT C3 conductor: it routes gate reads to THE MIND, not files",
     "mind_grep" in err or "MIND" in err)
rc, out2, err2 = run(COND, d, session="condsess")
bait("BAIT C4 conductor: ONCE per session, the second build is quiet", err2.strip() == "")
shutil.rmtree(d, ignore_errors=True)

d = tempfile.mkdtemp(prefix="bait-cond-")
rc, out, err = run(COND, d, cmd=READ, session="condsess2")
bait("BAIT C5 conductor: a plain read does not arm it", rc == 0 and err.strip() == "", err[:38])
rc, out, err = run(COND, d, tool="Write", session="condsess3")
bait("BAIT C6 conductor: Write DOES arm it (authoring is building)",
     rc == 0 and "CONDUCTOR ENTRY" in err)
rc, out, err = run(COND, d, raw="{not json", session="condsess4")
bait("BAIT C7 conductor: malformed payload FAILS OPEN, silently", rc == 0 and err.strip() == "")
shutil.rmtree(d, ignore_errors=True)

print()
if bad:
    print("BAIT: FAIL  %d/%d" % (total - len(bad), total))
    for b in bad:
        print("   failed: %s" % b)
    sys.exit(1)
print("BAIT: PASS  %d/%d" % (total, total))
