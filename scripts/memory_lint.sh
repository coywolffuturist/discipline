#!/usr/bin/env bash
# memory_lint.sh — WARN-ONLY hygiene check for the Coywolf memory index.
# Root-cause guard for MEMORY.md re-bloat (the prose "one line ≤200 chars" rule
# failed silently and the index grew to 62KB, past the harness load cap, so only
# part loaded each session). Per feedback_private_rule_05.md the
# fix lives in code, not another .md rule.
#
# Contract: READ-ONLY. NEVER edits memory (a script must not rewrite my memory —
# it races the live appender and could clobber facts). It only prints warnings.
# Always exits 0 so it can never block a session. Prints NOTHING when clean, so
# it only surfaces when an action of mine is actually warranted.
set -u

# The project dir encodes $HOME with slashes as dashes. DERIVED, never
# written: this file lives in a repo with a remote, and the operator
# name belongs on no surface we publish (disclosure doctrine).
CC_PROJ="-$(printf %s "${HOME#/}" | tr / -)"
MEM_DIR="$HOME/.claude/projects/$CC_PROJ/memory"
INDEX="$MEM_DIR/MEMORY.md"
# THE LOADER REACH, MEASURED — not guessed. 2026-09-21: the harness reported
# "211 lines and 28.3KB. Only part of it was loaded: 17 of 211 lines were cut
# off, starting at line 195", and head -194 of that file was 26,481 BYTES.
# This constant was 50000 with a comment claiming truncation began at ~59KB.
# That was wrong by 2x, so the guard stayed silent while MEMORY.md sat at
# 34,842 B — 8KB deep in the dead zone — and every index line written on
# 2026-09-20 was never loaded. A guard calibrated to the wrong constant is
# worse than no guard: it certifies clean.
# MEASURED TWICE, HOURS APART, AND THEY DISAGREE:
#   28.3KB file -> 26,481 B loaded (cut at line 195)
#   25.0KB file -> 24,458 B loaded (cut at line 201)
# A 2,023 B spread (7.6%). So the reach is NOT a byte constant — it behaves
# like a TOKEN budget, and emoji-dense hooks cost more tokens per byte. The
# first version of this fix hardcoded 26481 from ONE observation, which is the
# same error as the 50000 it replaced, just smaller. Use the LOWEST observed
# reach and keep headroom. Re-measure whenever the harness reports a cut: the
# warning names the line, and head -<line-1> | wc -c is the new datapoint.
LOADER_REACH=24458   # lowest OBSERVED, 2026-09-21 — not a guarantee
WARN_BYTES=22500     # fire well before the lowest observed cut
MAX_CHARS=200      # harness guidance: index entries are one-line hooks

[ -f "$INDEX" ] || exit 0

warnings=""

# 1. Total size — the thing that actually causes truncated loads.
bytes=$(wc -c < "$INDEX" | tr -d ' ')
if [ "$bytes" -gt "$WARN_BYTES" ]; then
  warnings+="  • MEMORY.md is ${bytes} bytes (loader reaches ~${LOADER_REACH}). Move reference_/project_ lines to OVERFLOW.md.\n"
fi
# 1b. THE DEAD ZONE — name the entries that are ALREADY past the cut. Size alone
#     under-sells this: those lines cost bytes and deliver nothing, and a new
#     entry appended at the bottom lands among them. NAME them, so the warning
#     is actionable rather than a tidiness nag that gets appended past.
if [ "$bytes" -gt "$LOADER_REACH" ] && command -v python3 >/dev/null 2>&1; then
  dz=$(python3 - "$INDEX" "$LOADER_REACH" <<'PYDZ'
import io,sys
p,reach=sys.argv[1],int(sys.argv[2])
run=0; dead=[]
for ln in io.open(p,encoding="utf-8"):
    run += len(ln.encode("utf-8"))
    if run > reach and ln.startswith(">"):
        t=ln.split("](")[0].replace("> ","").lstrip("*[ ")
        dead.append(t[:58])
print(len(dead))
for t in dead[:6]: print("      - "+t)
PYDZ
)
  n=$(echo "$dz" | head -1)
  if [ "${n:-0}" -gt 0 ]; then
    warnings+="  • 🚨 ${n} index entr(ies) are PAST THE LOADER CUT and are never loaded.\n"
    warnings+="      A write-back below the cut is a no-op: correct page, correct index line, never loaded.\n"
    warnings+="      Inserting at the TOP does not fix this — with two writers the top is one contested\n"
    warnings+="      slot and earlier entries migrate back down. SHRINK the file: move reference_/project_\n"
    warnings+="      lines to OVERFLOW.md. WHICH memories stop firing is a decision for the operator.\n"
    warnings+="$(echo "$dz" | tail -n +2)\n"
  fi
fi

# 2. Over-length index lines (char count, not bytes — macOS awk length() is bytes,
#    which false-positives on emoji lines, so use python3 codepoint count).
if command -v python3 >/dev/null 2>&1; then
  longn=$(python3 -c "import sys;print(sum(1 for l in open(sys.argv[1]) if len(l.rstrip(chr(10)))>${MAX_CHARS}))" "$INDEX")
else
  longn=$(awk -v m="$MAX_CHARS" 'length($0)>m{c++} END{print c+0}' "$INDEX")
fi
if [ "$longn" -gt 0 ]; then
  warnings+="  • ${longn} index line(s) exceed ${MAX_CHARS} chars — move detail into the linked topic file.\n"
fi

# 3a. LINK ACCOUNTING — every opener is well-formed or SKIPPED, and a skip is a
#     finding. The dead-link check below searches for WELL-FORMED links, so a
#     link truncated mid-path is invisible to it: it is not a dead link, it is
#     not a link, and the pattern never fires. That is how the section 166 route
#     stayed broken across two repairs.
#     Rule: decision_private_ruling_02.
#     Logic lives in link_scan.py because inline python with backticks breaks the
#     shell no matter how the heredoc is quoted.
SCAN="$HOME/.claude/scripts/link_scan.py"
if [ -x "$SCAN" ] || [ -f "$SCAN" ]; then
  scanout=$(python3 "$SCAN" "$INDEX" 2>/dev/null)
  skipped=$(printf '%s' "$scanout" | head -1 | awk '{print $3+0}')
  opens=$(printf '%s' "$scanout" | head -1 | awk '{print $1+0}')
  if [ "${skipped:-0}" -gt 0 ]; then
    warnings+="  • LINK SCAN SKIPPED ${skipped} of ${opens} opener(s) — the dead-link check did NOT examine them:\n"
    while IFS= read -r l; do
      [ -n "$l" ] && warnings+="      $l\n"
    done <<< "$(printf '%s' "$scanout" | tail -n +2)"
  fi
fi

# 3. Dead links: a (file.md) link whose target is missing → broken pointer.
dead=$(grep -oE '\(([A-Za-z0-9_./-]+\.md)\)' "$INDEX" | tr -d '()' | sort -u \
  | while read -r f; do [ -f "$MEM_DIR/$f" ] || echo "$f"; done)
if [ -n "$dead" ]; then
  warnings+="  • Dead link(s) in MEMORY.md (target file missing):\n"
  while read -r f; do [ -n "$f" ] && warnings+="      - $f\n"; done <<< "$dead"
fi

# 3b. MALFORMED links — a "](" that never closes. INVISIBLE to check 3, which
#     searches for (name.md): a link truncated mid-path does not match that
#     pattern at all, so it is not a dead link, it is not a link. Found 2 on
#     2026-09-21, one of them a live tax page trimmed mid-filename by a
#     hook-length cap that cut the URL instead of the prose.
if command -v python3 >/dev/null 2>&1; then
  mal=$(python3 - "$MEM_DIR" <<'PYML'
import io,os,re,sys
mem=sys.argv[1]
for f in ("MEMORY.md","OVERFLOW.md"):
    p=os.path.join(mem,f)
    if not os.path.exists(p): continue
    for i,ln in enumerate(io.open(p,encoding="utf-8",errors="replace"),1):
        for m in re.finditer(r"\]\(", ln):
            if not re.match(r"[^)]*\)", ln[m.end():]):
                print("%s:%d  ...%s" % (f,i,ln.rstrip()[-52:]))
PYML
)
  if [ -n "$mal" ]; then
    warnings+="  • MALFORMED link(s) — an opening ]( with no closing ). A truncated link is INVISIBLE to the dead-link check:\n"
    while read -r l; do [ -n "$l" ] && warnings+="      - $l\n"; done <<< "$mal"
  fi
fi

# 4. Orphan topic files: a *.md on disk that nothing in the index links to.
#    Ignore the index itself, TOPOLOGY.md, and backups.
orphans=$(cd "$MEM_DIR" && ls -1 *.md 2>/dev/null \
  | grep -v -e '^MEMORY.md$' -e '^TOPOLOGY.md$' \
  | while read -r f; do grep -q "($f)" "$INDEX" "$MEM_DIR/OVERFLOW.md" 2>/dev/null || echo "$f"; done)   # OVERFLOW.md is the lookup half (split 2026-09-02); a pointer there is indexed
if [ -n "$orphans" ]; then
  n=$(echo "$orphans" | grep -c .)
  warnings+="  • ${n} topic file(s) on disk are not indexed in MEMORY.md or OVERFLOW.md (add a one-line pointer or delete):\n"
  while read -r f; do [ -n "$f" ] && warnings+="      - $f\n"; done <<< "$orphans"
fi

# 5. Stale graduation: a memory whose recall surface (the frontmatter description —
#    the field recall actually matches on) still markets a rule as a "candidate to
#    become a skill". Once skill-ified, the description MUST point to the skill, or the
#    always-on memory out-competes the on-demand skill it graduated into (2026-06-12:
#    a stale description made a session cite feedback_private_rule_19 instead of the
#    `completer` skill). READ-ONLY flag — never edits the memory.
if command -v python3 >/dev/null 2>&1; then
  stale=$(python3 - "$MEM_DIR" <<'PY'
import sys, os, re, glob
mem = sys.argv[1]
pat = re.compile(r'candidate.{0,40}skill|could become a skill|should become a skill', re.I)
for f in sorted(glob.glob(os.path.join(mem, '*.md'))):
    b = os.path.basename(f)
    if b in ('MEMORY.md', 'TOPOLOGY.md'):
        continue
    t = open(f, encoding='utf-8', errors='replace').read()
    parts = t.split('---', 2)
    front = parts[1] if len(parts) >= 3 else ''
    m = re.search(r'(?ms)^description:\s*(.*?)(?=^\S+:|\Z)', front)
    desc = m.group(1) if m else ''
    if pat.search(desc):
        print(b)
PY
)
  if [ -n "$stale" ]; then
    warnings+="  • Stale graduation — memory description still calls a rule a 'candidate to become a skill'; if the skill now exists, point the description AT it (else the always-on memory out-competes the on-demand skill):\n"
    while read -r f; do [ -n "$f" ] && warnings+="      - $f\n"; done <<< "$stale"
  fi
fi

if [ -n "$warnings" ]; then
  printf "⚠️  memory hygiene (memory_lint.sh):\n"
  printf "%b" "$warnings"
fi
exit 0
