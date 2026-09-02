#!/usr/bin/env python3
"""bait_hook_completer.py — hooks/hook_completer.py, seen to fire.

Gate 12. The hook reads the LAST assistant text in the transcript for deferral
language. The failures it must not have: firing on the user's words, on tool
output, or on an earlier turn's text — any of those trains it into noise.
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "hook_completer.py")

bad = []
total = 0


def transcript(lines):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for kind, text in lines:
        if kind == "assistant":
            f.write(json.dumps({"type": "assistant", "message": {
                "role": "assistant", "content": [{"type": "text", "text": text}]}}) + "\n")
        elif kind == "tool":
            f.write(json.dumps({"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "content": text}]}}) + "\n")
        else:
            f.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
    f.close()
    return f.name


def run(lines, path=None):
    p = path if path is not None else transcript(lines)
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"transcript_path": p}),
                       capture_output=True, text=True, timeout=30)
    if path is None:
        os.unlink(p)
    ctx = ""
    if r.stdout.strip():
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    return r.returncode, ctx


def bait(label, lines, want, path=None):
    global total
    total += 1
    rc, ctx = run(lines, path)
    ok = rc == 0 and ((want.lower() in ctx.lower()) if want else ctx == "")
    print("  %s %-62s %s" % ("ok " if ok else "XX ", label, "fired" if ctx else "quiet"))
    if not ok:
        bad.append(label)
        print("      rc=%s ctx=%r" % (rc, ctx[:120]))


bait("BAIT C1 'follow-up' in the last assistant text fires gate 12",
     [("user", "do it"), ("assistant", "Done. The rest is a follow-up.")], "follow-up")
bait("BAIT C2 the phrase is NAMED in the reminder",
     [("assistant", "I will revisit later.")], "'revisit later'")
bait("BAIT C3 the user's own deferral does not fire",
     [("user", "leave it for a follow-up"), ("assistant", "Done, all of it.")], "")
bait("BAIT C4 deferral in tool output does not fire",
     [("tool", "TODO: separate pass"), ("assistant", "Done, all of it.")], "")
bait("BAIT C5 an EARLIER turn's deferral does not fire on a clean last turn",
     [("assistant", "Out of scope for now."), ("user", "ok"), ("assistant", "Finished.")], "")
bait("BAIT C6 'TODO' fires", [("assistant", "TODO: the rest")], "todo")
bait("BAIT C7 'out of scope for now' fires", [("assistant", "That is out of scope for now.")], "out of scope for now")
bait("BAIT C8 a missing transcript is quiet, not a crash", [], "", path="/nonexistent/t.jsonl")
bait("BAIT C9 a transcript with no assistant text is quiet", [("user", "hi")], "")

# Every phrase, and the case rule. A reviewer deleted phrases one at a time
# and dropped re.I; the baits above stayed green.
for phrase in ("follow-up", "follow up", "next session", "separate pass", "deferred",
               "later pass", "for now", "TODO", "revisit later", "leave that for", "leave this for",
               "leave it for", "out of scope for now", "out of scope for today"):
    bait("BAIT C10 %r fires" % phrase, [("assistant", "Done. %s, the rest." % phrase)], phrase.lower())
bait("BAIT C11 'Follow-up' capitalised fires (case-insensitive)", [("assistant", "Follow-up: the rest.")], "follow-up")


# A user line whose content is a LIST holding a text block: the assistant-only
# filter is what keeps it out. Without the filter it parses like a turn.
def user_list_transcript():
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.write(json.dumps({"type": "assistant", "message": {"role": "assistant",
                        "content": [{"type": "text", "text": "Finished, all of it."}]}}) + "\n")
    f.write(json.dumps({"type": "user", "message": {"role": "user",
                        "content": [{"type": "text", "text": "do the rest in a follow-up"}]}}) + "\n")
    f.close()
    return f.name


p = user_list_transcript()
bait("BAIT C12 a user text block after the last assistant turn does not fire", [], "", path=p)
os.unlink(p)

print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
for l in bad:
    print("   failed: %s" % l)
sys.exit(1 if bad else 0)
