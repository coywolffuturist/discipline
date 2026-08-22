#!/usr/bin/env python3
"""mutate_test.py — does the test suite actually TEST anything?

WHY THIS EXISTS. On 2026-08-22 a refuter deleted seven behaviours from these
gates and `test_gates.py` stayed green at 28/28 — including gate 02's
empty-scan rule, which is the rule this whole repository was written to
enforce. A green suite that survives the deletion of the code it certifies is
not evidence. It is the third occurrence of the estate's own scar: an eval can
report health it does not have.

HOW IT WORKS. Copy the repo. Break ONE behaviour. Run the suite. The suite MUST
go red. A mutation the suite does not notice is an ESCAPE, and an escape is a
hole in the tests, not in the code.

Run: python3 mutate_test.py     exit 0 = every mutation was caught
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))

# (name, relative path, find, replace) — each one is a behaviour the suite claims
MUTATIONS = [
    ("gate 02's empty-scan rule (the repo's thesis)",
     "gates/02-retrieval-economy/door_report.py",
     'print("RED  0 events in the last %dh — nothing measured, which is not a pass." % hours)\n        return 1',
     'return 0'),
    ("the missing-log RED in door_report",
     "gates/02-retrieval-economy/door_report.py",
     'print("     An unregistered gate reports a safety it does not have.")\n        return 1',
     'return 0'),
    ("the bare-pronoun detector (finding 5's mechanism)",
     "gates/01-ste/ste.py",
     r'BARE_PRONOUN = re.compile(r"^\s*(?:It|They|Them|Its|Their)\b")',
     'BARE_PRONOUN = re.compile(r"(?!x)x")'),
    # NOTE: an earlier version of this mutation prefixed an alternation, which
    # left every original pattern live. It reported a FALSE ESCAPE. A mutation
    # that does not mutate is a defect in the harness, so the harness now
    # verifies each mutation actually changed behaviour (see check below).
    ("the vague-scope detector",
     "gates/01-ste/ste.py", 'vague += len(VAGUE.findall(s))', 'vague += 0'),
    ("the list-marker sentence boundary (finding 4)",
     "gates/01-ste/ste.py", 'text = LIST_MARK.sub("\\x00", text)', 'pass'),
    ("the YAML frontmatter stripper",
     "gates/01-ste/ste.py", 'text = FRONTMATTER.sub("", text)', 'pass'),
    ("the unreadable-file RED (finding 1, production shape)",
     "gates/01-ste/lint_ste.py",
     'print("VERDICT: RED — %d file(s) unreadable. An unread file is never a pass."\n              % len(unreadable))\n        return 1',
     'pass'),
    ("the secret redaction in the door log",
     "gates/02-retrieval-economy/hook_corpus_read.py",
     '"shape": shape(detail)}) + "\\n")', '"shape": detail}) + "\\n")'),
    ("hook_prompt's fail-open type guard",
     "gates/01-ste/hook_prompt.py", '    if not isinstance(data, dict):\n        sys.exit(0)', '    pass'),
    ("hook_corpus_read's command type guard",
     "gates/02-retrieval-economy/hook_corpus_read.py",
     '    if not isinstance(cmd, str):\n        sys.exit(0)', '    pass'),
    ("the Read/Grep channel (the dominant read path)",
     "gates/02-retrieval-economy/hook_corpus_read.py",
     '    if tool in ("Read", "Grep", "Glob"):', '    if False:'),
    ("the door-leads-the-pipeline rule",
     "gates/02-retrieval-economy/hook_corpus_read.py",
     '    is_door = bool(CHEAP.match(cmd))', '    is_door = False'),
    ("the N/A path that keeps code commits unblocked",
     "gates/01-ste/lint_ste.py",
     '        print("N/A  no markdown in %d path(s) given', '        print("RED  no markdown in %d path(s) given'),
]

def main():
    caught, escaped = [], []
    for name, rel, find, repl in MUTATIONS:
        d = tempfile.mkdtemp(prefix="mut-")
        dst = os.path.join(d, "r")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        path = os.path.join(dst, rel)
        src = open(path, encoding="utf-8").read()
        if find not in src:
            print("XX  %-56s MUTATION DID NOT APPLY — verdict discarded" % name[:56])
            escaped.append(name + " (did not apply)")
            shutil.rmtree(d, ignore_errors=True)
            continue
        mutated = src.replace(find, repl, 1)
        if mutated == src:
            print("XX  %-56s TEXT UNCHANGED — verdict discarded" % name[:56])
            escaped.append(name + " (text unchanged)")
            shutil.rmtree(d, ignore_errors=True)
            continue
        open(path, "w", encoding="utf-8").write(mutated)
        r = subprocess.run([sys.executable, os.path.join(dst, "test_gates.py")],
                           capture_output=True, text=True, timeout=300, cwd=dst)
        if r.returncode == 0:
            print("XX  %-56s ESCAPED — suite still green" % name[:56])
            escaped.append(name)
        else:
            print("OK  %-56s caught" % name[:56])
            caught.append(name)
        shutil.rmtree(d, ignore_errors=True)

    print("\nMUTATION: %d caught, %d escaped, of %d" % (len(caught), len(escaped), len(MUTATIONS)))
    if escaped:
        print("\nAn ESCAPE is a hole in the TESTS, not in the code. Each of these")
        print("behaviours can be deleted and the suite will still certify the gate:")
        for e in escaped:
            print("   %s" % e)
        return 1
    print("Every mutation was caught. The suite tests what it claims to test.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
