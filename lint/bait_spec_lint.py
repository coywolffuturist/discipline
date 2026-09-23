#!/usr/bin/env python3
"""bait_spec_lint.py — scripts/spec_lint.py, seen to go red on every defect it claims to catch.

A checker that goes green must be baited: a clean result from an instrument never
shown to register a positive means nothing. Each case plants ONE defect into an
otherwise clean minimal spec and requires exit 1 with the matching DEFECT line; the
clean control must exit 0. The window mode must mark a phase BLOCKED on an unruled
item and READY once it is ruled.
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT = os.path.join(ROOT, "scripts", "spec_lint.py")

CLEAN = """---
name: SPEC-bait
status: DRAFT
as_of: 2026-09-22
---

# Bait spec

## Tests
- SELF-T1 the eval blocks a commit.
- BODY-T1 our code is in git.

## Rulings
| # | question | ruling |
|---|---|---|
| R1 | brain | D, 2026-09-22 |
| A1 | source | den |

## OPEN
| # | question | recommendation |
|---|---|---|
| OPEN-1 | where gates live | den hooks |

## Build order
| phase | delivers | done when | needs |
|---|---|---|---|
| P0 First | eval | SELF-T1 | R1 |
| P1 Second | code | BODY-T1 | A1, OPEN-1 |

## 9. Glossary
| term | meaning |
|---|---|
| SELF-, BODY- | test families |
"""

CASES = [
    ("clean control", CLEAN, 0, None),
    ("test defined, never scheduled", CLEAN.replace("- BODY-T1 our code is in git.",
        "- BODY-T1 our code is in git.\n- BODY-T2 orphan test."), 1, "BODY-T2 is defined but no phase"),
    ("phase needs undefined test", CLEAN.replace("| SELF-T1 |", "| SELF-T1, SELF-T9 |"), 1, "needs test SELF-T9"),
    ("phase needs unknown ruling", CLEAN.replace("| R1 |\n", "| R1, R7 |\n"), 1, "needs R7, which is not in the rulings table"),
    ("ruling left blank", CLEAN.replace("| A1 | source | den |", "| A1 | source | — |"), 1, "ruling A1 has no ruling recorded"),
    ("open item blocks nothing", CLEAN.replace("| A1, OPEN-1 |", "| A1 |"), 1, "OPEN-1 blocks no phase"),
    ("phase needs missing OPEN", CLEAN.replace("| A1, OPEN-1 |", "| A1, OPEN-1, OPEN-2 |"), 1, "needs OPEN-2, which is not in the OPEN table"),
    ("family missing from glossary", CLEAN.replace("| SELF-, BODY- |", "| SELF- |"), 1, "test family BODY-T is not in the glossary"),
    ("no frontmatter status", CLEAN.replace("status: DRAFT\n", ""), 1, "frontmatter lacks status"),
    ("child-spec phase ids (M0) parse", CLEAN.replace("| P0 First |", "| M0 First |").replace("| P1 Second |", "| M1 Second |"), 0, None),
    ("named invariant row is not a phase", CLEAN.replace("## Rulings", "## Invariants\n| # | invariant | source |\n|---|---|---|\n| I4 (reconciled) | forget by key | 09-22 |\n\n## Rulings"), 0, None),
    ("lettered ruling id RM7 counts as ruled", CLEAN.replace("| A1 | source | den |", "| A1 | source | den |\n| RM7 | forgetting | a and c |").replace("| A1, OPEN-1 |", "| A1, RM7, OPEN-1 |"), 0, None),
    ("invariant rows are not phases", CLEAN.replace("## Rulings", "## Invariants\n| # | invariant | source |\n|---|---|---|\n| I1 | the record is the truth | 09-22 |\n\n## Rulings"), 0, None),
]

bad, total = [], 0


def run(mode, text):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    f.write(text); f.close()
    r = subprocess.run([sys.executable, LINT, mode, f.name], capture_output=True, text=True, timeout=30)
    os.unlink(f.name)
    return r.returncode, r.stdout


for name, text, want_rc, want_line in CASES:
    total += 1
    rc, out = run("check", text)
    if rc != want_rc or (want_line and want_line not in out):
        bad.append("%s: rc=%s want %s; output: %s" % (name, rc, want_rc, out.strip()[:200]))

total += 1
kid = CLEAN.replace("OPEN-1", "OPEN-M1")
rc, out = run("window", kid)
if "BLOCKED  P1  waiting on OPEN-M1" not in out:
    bad.append("window: a child spec's OPEN-M1 must block P1; got: %s" % out.strip())

total += 1
rc, out = run("window", CLEAN)
if "READY    P0" not in out or "BLOCKED  P1  waiting on OPEN-1" not in out:
    bad.append("window: expected P0 READY and P1 BLOCKED on OPEN-1; got: %s" % out.strip())

total += 1
rc, out = run("check", "/nonexistent")
rc2 = subprocess.run([sys.executable, LINT, "check", "/nonexistent/spec.md"], capture_output=True, text=True).returncode
if rc2 != 2:
    bad.append("unreadable file: rc=%s want 2" % rc2)

for b in bad:
    print("  RED   " + b)
print("\n%s  %d/%d" % ("BAIT: PASS" if not bad else "BAIT: FAIL", total - len(bad), total))
sys.exit(1 if bad else 0)
