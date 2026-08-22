#!/usr/bin/env python3
"""lint/baits_pair — every numbered check must have a bait with the same id.

The rule of this repo is that a gate is not done when it passes. It is done when
its bait has been SEEN TO FAIL.

The rule was enforced by remembering, and remembering failed three times in one
day. Each failure was found by somebody else:

  * gate 01 shipped a passive metric that was anti-correlated with passive voice.
  * gate 02 shipped a door ratio that was inverted, twice.
  * a mutation harness reported "13 of 13 caught" while 17 real mutations
    escaped, because its mutations were derived from its own tests.

The rule is mechanical now. This file is copied from spirals/lint/baits_pair.py,
which has a catch record. It is not a new invention. Three inventions were
refuted first.

WHAT IT CHECKS. In any file that calls check(...), a label starting with an id
like S1 or F4 is an assertion. A label starting with `BAIT <id>` is that
assertion's bait. Every id must have at least one bait.

WHAT IT DELIBERATELY DOES NOT CHECK. Whether the bait is any good. A weak bait
passes this lint. What it removes is the silent case, which is a check nobody
ever tried to break. That case reads exactly like a check somebody did.

Exceptions are written on the line and COUNTED:

    baits-pair: allow — <reason>

A rising exception count means the rule is being negotiated away.
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baits_pair.baseline")
# Both helpers count. A bait harness names its cases with bait(...), and an
# earlier version scanned only check(...) — so three real baits were invisible
# and the rule reported its own bait file as unbaited. It was right to fail.
# The scanner was reading the wrong call.
CALL = re.compile(r"""(?<![\w-])(?:check|bait)\s*\(\s*["']([^"']{3,200})["']""")
IDENT = re.compile(r"^([A-Z]{1,4}[0-9]{1,3}[a-z]?)\b")
BAIT = re.compile(r"^BAIT\s+([A-Z]{1,4}[0-9]{1,3}[a-z]?)\b", re.I)
ALLOW = re.compile(r"baits-pair:\s*allow")
DECL = re.compile(r'^\s*"([A-Z]{1,4}[0-9]{1,3}[a-z]?)":', re.M)

def scan():
    asserts, baits, allowed = {}, set(), 0
    files = sorted(glob.glob(ROOT + "/gates/*/*.py") + glob.glob(ROOT + "/lint/*.py"))
    for f in files:
        if os.path.basename(f).startswith("baits_pair"):
            continue
        for line in open(f, encoding="utf-8", errors="ignore"):
            if ALLOW.search(line):
                allowed += 1
                continue
            for label in CALL.findall(line):
                b = BAIT.match(label)
                if b:
                    baits.add(b.group(1).upper())
                    continue
                i = IDENT.match(label)
                if i:
                    asserts[i.group(1).upper()] = os.path.relpath(f, ROOT)
        # a checks.py DECLARES ids without calling check()
        if os.path.basename(f) == "checks.py":
            body = open(f, encoding="utf-8").read()
            for m in DECL.finditer(body):
                asserts.setdefault(m.group(1).upper(), os.path.relpath(f, ROOT))
    return asserts, baits, allowed, len(files)

def main():
    asserts, baits, allowed, nfiles = scan()
    if not asserts:
        print("RED  no numbered check was found in any file.")
        print("     A gate with no numbered checks cannot be baited, and this")
        print("     lint scanning nothing is not a pass.")
        return 1
    debt = set()
    if os.path.exists(BASELINE):
        debt = {l.strip().upper() for l in open(BASELINE)
                if l.strip() and not l.startswith("#")}
    unbaited = sorted(set(asserts) - baits)
    new = [u for u in unbaited if u not in debt]
    print("baits pair: %d check(s) across %d file(s), %d unbaited (%d in baseline)"
          % (len(asserts), nfiles, len(unbaited), len(unbaited) - len(new)))
    if allowed:
        print("   %d exception(s) written on the line. A RISING count means the"
              " rule is being negotiated away." % allowed)
    if new:
        print("RED  %d NEW check(s) with no bait:" % len(new))
        for u in new:
            print("     %-6s %s" % (u, asserts[u]))
        print("     Write BAIT %s and see it fail before this ships." % new[0])
        return 1
    gone = sorted(debt - set(unbaited))
    if gone:
        print("   DEBT PAID: %s now baited. Remove from the baseline." % ", ".join(gone))
    print("GREEN  every new check has a bait.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
