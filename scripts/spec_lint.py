#!/usr/bin/env python3
"""spec_lint — the mechanical half of spec-driven development.

A spec written as prose rots: a test is defined and never scheduled, a phase
names a ruling that was never made, a ruling row is left blank, a code is used
that the glossary never defines. Each of these was found by a refuter on
2026-09-22 in one spec, by hand, in two passes. A checker finds them in one
second, every time, so the refuter can spend its judgment on what a checker
cannot see.

The spec shape it reads (see the spec-driven skill's template):
  - frontmatter with `status:` and `as_of:`
  - tests defined as list items starting with a test ID:   `- SELF-T1 ...`
  - a rulings table whose FIRST column is the ruling ID (R0, R7b, A1, ...)
    and whose LAST column is the ruling (empty / "—" = unruled)
  - an OPEN table whose first column is OPEN-n
  - a phases table whose first column starts with P0..Pn and whose last
    column lists the rulings it needs, and whose 'done when' column names tests
  - a glossary table

Usage:
  spec_lint.py check  SPEC.md   exit 0 clean · 1 defects (printed) · 2 unreadable
  spec_lint.py window SPEC.md   the next steps DERIVED from the spec: which phases
                                can start (all their rulings made) and which rulings
                                block the rest. The ka123n window is drawn from this.
"""
import re
import sys

TEST_DEF = re.compile(r"^\s*-\s+(?:\*\*)?([A-Z]+-T\d+)\b", re.M)
TEST_REF = re.compile(r"\b([A-Z]+-T\d+)\b")
TEST_RANGE = re.compile(r"\b([A-Z]+)-T(\d+)\s*(?:\.\.|to)\s*T?(\d+)\b")
RULING_ID = re.compile(r"^(R[A-Z]?\d+[a-z]?|A\d+)$")   # R3, R7b, a child spec's RM7
OPEN_ID = re.compile(r"^OPEN-[A-Z]?\d+$")      # OPEN-3 and a child spec's OPEN-M3
NEED = re.compile(r"\b(R[A-Z]?\d+[a-z]?|A\d+|OPEN-[A-Z]?\d+)\b")
UNRULED = {"", "—", "-", "–", "tbd", "TBD"}


def rows(text):
    """Every markdown table row, as a list of stripped cells."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and not re.match(r"^\|[\s\-:|]+\|$", s):
            out.append([c.strip() for c in s.strip("|").split("|")])
    return out


def clean(cell):
    return re.sub(r"[*`]", "", cell).strip()


def expand_refs(text):
    """Test IDs referenced, with ranges like BODY-T1..T4 expanded."""
    refs = set(TEST_REF.findall(text))
    for fam, a, b in TEST_RANGE.findall(text):
        for n in range(int(a), int(b) + 1):
            refs.add("%s-T%d" % (fam, n))
    return refs


def parse(text):
    tests = set(TEST_DEF.findall(text))
    rulings, opens, phases = {}, set(), []
    for r in rows(text):
        head = clean(r[0])
        if RULING_ID.match(head) and len(r) >= 2:
            rulings[head] = clean(r[-1])
        elif OPEN_ID.match(head):
            opens.add(head)
        # A phase row is a short code followed by a NAME ("P0 Stop the bleeding", "M0 Record").
        # Requiring the name keeps invariant rows ("I1", no name) from being read as phases.
        # ...and has the four columns of a phases table (delivers · done when · needs):
        # an invariant row like "I4 (reconciled)" has a name too, but only three columns.
        elif re.match(r"^[A-Z]{1,2}\d+\s+\S", head) and len(r) >= 4:
            phases.append({"id": head.split()[0], "row": r,
                           "needs": set(NEED.findall(clean(r[-1]))),
                           "tests": expand_refs(" ".join(r[1:-1]))})
    return tests, rulings, opens, phases


def check(text):
    bad = []
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        bad.append("no frontmatter")
    else:
        for key in ("status", "as_of"):
            if not re.search(r"^%s:\s*\S" % key, fm.group(1), re.M):
                bad.append("frontmatter lacks %s:" % key)
    tests, rulings, opens, phases = parse(text)
    if not phases:
        bad.append("no phases table found (rows like \"P0 Name\" or \"M0 Name\")")
    scheduled = set().union(*[p["tests"] for p in phases]) if phases else set()
    for t in sorted(tests - scheduled):
        bad.append("test %s is defined but no phase's 'done when' schedules it" % t)
    for p in phases:
        for t in sorted(p["tests"] - tests):
            bad.append("phase %s needs test %s, which is never defined" % (p["id"], t))
        for n in sorted(p["needs"]):
            if n.startswith("OPEN-"):
                if n not in opens:
                    bad.append("phase %s needs %s, which is not in the OPEN table" % (p["id"], n))
            elif n not in rulings:
                bad.append("phase %s needs %s, which is not in the rulings table" % (p["id"], n))
    for rid, val in sorted(rulings.items()):
        if val in UNRULED:
            bad.append("ruling %s has no ruling recorded" % rid)
    needed = set().union(*[p["needs"] for p in phases]) if phases else set()
    for o in sorted(opens - needed):
        bad.append("%s blocks no phase: either schedule it or it is not open" % o)
    # The heading is found with MULTILINE only; the body is the slice after it. A single
    # regex with DOTALL let `.*` swallow the whole file and the glossary read as empty.
    gl = re.search(r"^## [^\n]*glossary[^\n]*$", text, re.M | re.I)
    if not gl:
        bad.append("no glossary section")
    else:
        g = text[gl.end():]
        fams = {t.split("-T")[0] for t in tests}
        for fam in sorted(fams):
            if fam + "-" not in g:
                bad.append("test family %s-T is not in the glossary" % fam)
    return bad


def window(text):
    tests, rulings, opens, phases = parse(text)
    unruled = {r for r, v in rulings.items() if v in UNRULED} | opens
    ready, blocked = [], []
    for p in phases:
        missing = sorted(n for n in p["needs"] if n in unruled)
        (blocked if missing else ready).append((p["id"], missing))
    return ready, blocked


def main(argv):
    if len(argv) != 3 or argv[1] not in ("check", "window"):
        print(__doc__.strip().splitlines()[-6])
        return 2
    try:
        text = open(argv[2], encoding="utf-8").read()
    except OSError as e:
        print("spec_lint: cannot read %s: %s" % (argv[2], e))
        return 2
    if argv[1] == "check":
        bad = check(text)
        for b in bad:
            print("DEFECT  " + b)
        print("spec_lint: %s" % ("clean" if not bad else "%d defect(s)" % len(bad)))
        return 1 if bad else 0
    ready, blocked = window(text)
    for pid, _ in ready:
        print("READY    %s" % pid)
    for pid, missing in blocked:
        print("BLOCKED  %s  waiting on %s" % (pid, ", ".join(missing)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
