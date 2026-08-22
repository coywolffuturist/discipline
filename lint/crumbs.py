#!/usr/bin/env python3
"""crumbs.py — read the breadcrumb stream. The first EDGE.

The stream is the coordination substrate. Gates WRITE events; readers like this
one JOIN them. Below a threshold of readers the stream is eleven write-only
logs. Above it, one gate can respond to another without anyone wiring them
together. This is the first reader that exists to be joined to.

WHAT IT DETECTS. A commit is a matched PAIR of crumbs sharing a tree hash: one
from pre-commit, one from post-commit. `--no-verify` skips pre-commit but NOT
post-commit. So a tree with a post crumb and no pre crumb PROVES the gates were
bypassed. Nothing here is a judgement. A tree hash either matches or it does not.

SCANNING NOTHING IS RED. An empty or missing log means the hooks are not
deployed, which is a finding, not health.
"""
import json, os, sys, collections

LOG = os.path.expanduser("~/.coywolf/state/git-hooks/log.jsonl")

def main():
    if not os.path.exists(LOG):
        print("RED  no breadcrumb log at %s" % LOG)
        print("     The hooks are not deployed, so nothing was recorded.")
        return 1
    trees = collections.defaultdict(dict)
    n = 0
    for line in open(LOG, encoding="utf-8", errors="ignore"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        t = d.get("tree") or ""
        if not t:
            continue
        n += 1
        trees[t][d.get("hook", "?")] = d
    if not n:
        print("RED  the log holds 0 usable crumbs. Nothing measured is not a pass.")
        return 1

    bypassed = [(t, v["post-commit"]) for t, v in trees.items()
                if "post-commit" in v and "pre-commit" not in v]
    paired = sum(1 for v in trees.values() if "pre-commit" in v and "post-commit" in v)
    print("crumbs: %d events · %d trees · %d fully paired · %d bypassed"
          % (n, len(trees), paired, len(bypassed)))
    if bypassed:
        print("  commits that skipped the gates (post crumb, no pre crumb):")
        for t, d in sorted(bypassed, key=lambda x: x[1].get("ts", ""))[-5:]:
            print("    %s  %-22s %s" % (d.get("ts", "?"), d.get("repo", "?"),
                                        (d.get("sha") or "")[:12]))
        print("  A bypass is not an error. It is a CHOICE that must stay visible.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
