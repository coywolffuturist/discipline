#!/usr/bin/env python3
"""retire-identifier — eliminate a deprecated identifier across a codebase.

The compile-it / cold-read tool. When you retire or replace an identifier (a
old address, an endpoint, a flag, a name), this sweeps EVERY occurrence and
neutralizes it — so no future agent reads the dead thing as live. Compiled from
a manual deprecation sweep done by hand.

Usage:
  retire-identifier.py --old STR [--new STR] [--marker STR]
                         --root DIR [--root DIR ...]
                         [--keep PATH ...] [--apply]

  --old      the deprecated string to eliminate (required)
  --new      replacement for CODE/CONFIG files (live identifier)
  --marker   replacement for PROSE files (e.g. "[DEPRECATED 2026-06-12 — see X]")
  --root     directory to sweep (repeatable; required)
  --keep     a path to leave untouched (the canonical tombstone; repeatable)
  --apply    actually write (default is DRY-RUN: shows what it would do)

Code/config (.html .js .mjs .cjs .ts .json .py .sh) → --new.
Prose/other (.md .txt …)                            → --marker.
A class is skipped if its replacement isn't given. Excludes .git, node_modules,
caches, worktrees, *.db, *.jsonl, *.bak. Reports every file it touches.
"""
import argparse, os, sys, subprocess

CODE_EXT = (".html", ".js", ".mjs", ".cjs", ".ts", ".json", ".py", ".sh")
EXCLUDE  = ("/.git/", "node_modules", "worktree", "repos-cache", ".db", ".jsonl", ".bak")

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--old", required=True)
    ap.add_argument("--new")
    ap.add_argument("--marker")
    ap.add_argument("--root", action="append", required=True)
    ap.add_argument("--keep", action="append", default=[])
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not a.new and not a.marker:
        sys.exit("refusing: give --new (code) and/or --marker (prose) — else nothing to do")
    keep  = {os.path.abspath(os.path.expanduser(k)) for k in a.keep}
    roots = [os.path.expanduser(r) for r in a.root]
    out = subprocess.run(["grep", "-rilF", a.old, *roots], capture_output=True, text=True).stdout
    files = [f for f in out.splitlines()
             if f and not any(x in f for x in EXCLUDE) and os.path.abspath(f) not in keep]
    code, prose, skip = [], [], []
    for f in files:
        if os.path.splitext(f)[1] in CODE_EXT:
            (code if a.new else skip).append(f if a.new else (f, "code, no --new"))
        else:
            (prose if a.marker else skip).append(f if a.marker else (f, "prose, no --marker"))
    mode = "APPLY" if a.apply else "DRY-RUN"
    print(f"[{mode}] deprecate {a.old!r}   code→{a.new!r}   prose→{a.marker!r}   kept={len(keep)}")
    for f in code:
        if a.apply:
            t = open(f, encoding="utf-8").read(); open(f, "w", encoding="utf-8").write(t.replace(a.old, a.new))
        print(f"  CODE  {'fixed' if a.apply else 'would fix'}: {f}")
    for f in prose:
        if a.apply:
            t = open(f, encoding="utf-8").read(); open(f, "w", encoding="utf-8").write(t.replace(a.old, a.marker))
        print(f"  PROSE {'redacted' if a.apply else 'would redact'}: {f}")
    for f, why in skip:
        print(f"  SKIP  ({why}): {f}")
    print(f"  total: {len(code)} code · {len(prose)} prose · {len(skip)} skipped"
          + ("" if a.apply else "   (dry-run — rerun with --apply to write)"))

if __name__ == "__main__":
    main()
