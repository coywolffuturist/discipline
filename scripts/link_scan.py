#!/usr/bin/env python3
"""link_scan.py — enumerate EVERY link opener in an index file and account for each.

WHY THIS IS A SEPARATE FILE. It lived inline in memory_lint.sh for one edit and
broke the script: backticks inside a command substitution are parsed by the
shell no matter how the heredoc is quoted. Complex content goes in a file --
the same rule that has bitten three times in two days.

WHY IT EXISTS AT ALL. The dead-link check searches for WELL-FORMED links,
`](name.md)`. A link truncated mid-path is therefore invisible to it: it is not
a dead link, it is not a link, and the pattern never fires. That is how the
section 166 route stayed broken across two repairs.

    A validator that matches a SHAPE is blind to the MALFORMED case,
    and malformation is exactly what a truncation produces.

So this does not report matches. It reports the ACCOUNTING: every `](` in the
file is either well-formed or skipped, and a nonzero skip count is a finding.
Rule: decision_private_ruling_02.

Inline code spans are stripped first. The router legitimately contains the
literal `[text](url)` in the entry about giving him bare URLs, and counting it
would make this warn every session -- a check that cries wolf every session
gets skimmed, which is the failure the whole lint exists to avoid.

Prints: "<opens> <wellformed> <skipped>" and one line per skipped opener.
"""
import io
import re
import sys

WELLFORMED = re.compile(r"\]\(([A-Za-z0-9_./-]+\.md)\)")
OPENER = re.compile(r"\]\(")
CODE_SPAN = re.compile(r"`[^`\n]*`")


def main():
    if len(sys.argv) < 2:
        print("0 0 0")
        return 0
    try:
        raw = io.open(sys.argv[1], encoding="utf-8", errors="replace").read()
    except Exception:
        print("0 0 0")
        return 0

    # Blank code spans rather than delete them, so byte offsets and therefore
    # reported line numbers stay true to the original file.
    text = CODE_SPAN.sub(lambda m: " " * len(m.group(0)), raw)

    wf_starts = [m.start() for m in WELLFORMED.finditer(text)]
    skipped = []
    for m in OPENER.finditer(text):
        if not any(abs(m.start() - w) < 2 for w in wf_starts):
            line = text[: m.start()].count("\n") + 1
            frag = text[m.start(): m.start() + 60].replace("\n", " ").rstrip()
            skipped.append((line, frag))

    opens = len(OPENER.findall(text))
    print("%d %d %d" % (opens, len(wf_starts), len(skipped)))
    for line, frag in skipped[:6]:
        print("line %d: %s" % (line, frag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
