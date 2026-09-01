#!/bin/bash
# nomess.sh — deterministic repo-hygiene scan. The MECHANICAL half of the
# /nomess gate; the judgment half (semantic orphans, doc-drift, label-store
# pollution, end-to-end smoke) stays in the skill, where a model is required.
#
# Usage: nomess.sh [repo-path]   (defaults to cwd)
# Exit:  0 = no hard mess   1 = hard mess (lint failure or broken symlink)
# Soft findings (untracked, stale branches, unpushed, empty dirs) are REPORTED
# for the model to classify, and do NOT set exit 1 on their own.
#
# Portable: drop into your scripts dir; the `nomess` skill calls it.
set -u
cd "${1:-.}" 2>/dev/null || { echo "nomess: cannot cd to ${1:-.}"; exit 2; }
git rev-parse --git-dir >/dev/null 2>&1 || { echo "nomess: not a git repo ($(pwd))"; exit 2; }

hard=0
say() { printf '%-22s %s %s\n' "$1" "$2" "$3"; }
OK="✓"; WARN="⚠"; BAD="✗"

# 0. Lint changed files (cheap-fail-fast). Scope = files touched in this
# workstream: working tree + staged + untracked-not-ignored + unpushed commits.
# Tempfiles (not process substitution) keep this portable across bash/zsh/sh.
flist=$(mktemp); lerr=$(mktemp); efile=$(mktemp)
{
  git diff --name-only --diff-filter=AM HEAD 2>/dev/null
  git diff --cached --name-only --diff-filter=AM 2>/dev/null
  git ls-files --others --exclude-standard 2>/dev/null
  git rev-parse --abbrev-ref @{u} >/dev/null 2>&1 && \
    git diff --name-only --diff-filter=AM @{u}..HEAD 2>/dev/null
} 2>/dev/null | sort -u > "$flist"
while IFS= read -r f; do
  [ -z "$f" ] && continue; [ -f "$f" ] || continue
  case "$f" in
    *.js|*.cjs|*.mjs) node --check "$f" 2>"$efile" || { echo "  js: $f"; sed 's/^/    /' "$efile"; } >> "$lerr" ;;
    *.py) python3 -m py_compile "$f" 2>"$efile" || { echo "  py: $f"; sed 's/^/    /' "$efile"; } >> "$lerr" ;;
  esac
done < "$flist"
if [ -s "$lerr" ]; then say "0 lint" "$BAD" "syntax errors in changed files:"; cat "$lerr"; hard=1
else say "0 lint" "$OK" "changed files parse"; fi
rm -f "$flist" "$lerr" "$efile"

# 1. Untracked / unstaged surfaces
untracked=$(git status --porcelain 2>/dev/null)
if [ -n "$untracked" ]; then n=$(printf '%s\n' "$untracked" | grep -c .); say "1 untracked" "$WARN" "$n line(s) — classify each (gitignore / add / note):"; printf '%s\n' "$untracked" | sed 's/^/    /'
else say "1 untracked" "$OK" "working tree clean"; fi

# 2. Stale merged branches
cur=$(git branch --show-current 2>/dev/null)
merged=$(git branch --merged 2>/dev/null | grep -vE "^\*|^\+| (main|master|develop)$" | sed 's/^ *//' | grep -v "^$cur$" || true)
if [ -n "$merged" ]; then say "2 stale branches" "$WARN" "merged, not deleted:"; printf '%s\n' "$merged" | sed 's/^/    /'
else say "2 stale branches" "$OK" "none merged-but-unpruned"; fi

# 3. Dead symlinks + unexpected empty dirs
dead=$(find . -path ./.git -prune -o -type l ! -exec test -e {} \; -print 2>/dev/null)
if [ -n "$dead" ]; then say "3 dead symlinks" "$BAD" "targets missing:"; printf '%s\n' "$dead" | sed 's/^/    /'; hard=1
else say "3 dead symlinks" "$OK" "all symlinks resolve"; fi
empty=$(find . -path ./.git -prune -o -type d -empty -print 2>/dev/null)
[ -n "$empty" ] && { say "3b empty dirs" "$WARN" "empty directories:"; printf '%s\n' "$empty" | sed 's/^/    /'; }

# 4. Unpushed commits (single-point-of-failure check — push is part of "done")
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null)
  if [ "${ahead:-0}" -gt 0 ]; then say "4 unpushed" "$WARN" "$ahead commit(s) ahead of upstream — push is part of done"
  else say "4 unpushed" "$OK" "in sync with upstream"; fi
else say "4 unpushed" "$WARN" "no upstream set — new branch never pushed, or no remote"; fi

echo
if [ "$hard" -eq 1 ]; then echo "nomess: HARD MESS — fix ✗ items before claiming done."; else echo "nomess: no hard mess. Classify ⚠ items, then run the JUDGMENT checks (skill §semantic-orphans, doc-drift, label-stores, smoke)."; fi
exit $hard
