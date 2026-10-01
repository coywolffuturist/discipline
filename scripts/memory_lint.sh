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
# The overflow index (the lookup half of MEMORY.md) and the files this check skips
# are machine-specific names, kept OUT of the repo: ~/.config/discipline/
# memory_overflow_index and memory_lint_skip (one name per line). Neutral defaults.
OVERFLOW="${DISCIPLINE_OVERFLOW_INDEX:-$(cat "$HOME/.config/discipline/memory_overflow_index" 2>/dev/null)}"
OVERFLOW="${OVERFLOW:-OVERFLOW.md}"
SKIPS="${DISCIPLINE_MEMORY_SKIP:-$(cat "$HOME/.config/discipline/memory_lint_skip" 2>/dev/null)}"
SKIPS="${SKIPS:-TOPOLOGY.md}"
export OVERFLOW SKIPS
# THE LOADER HAS TWO CAPS, AND EITHER ONE CUTS. Read out of the CLI binary
# (versions/2.1.278), not inferred:
#
#   function HSt(e,n="index"){ let {trimmed:r,lineCount:s,byteCount:g}=LXe(e),
#       h = s>tL,      // tL = 200   LINES
#       y = g>ez;      // ez = 25000 BYTES  <- TRIGGERS the branch
#     if(!h&&!y) return {..., wasLineTruncated:h, wasByteTruncated:y};
#     let w = h ? r.split("\n").slice(0,tL).join("\n") : r;
#     if (w.length > ez) { let U = w.lastIndexOf("\n", ez); w = w.slice(0, U>0?U:ez); }
#                ^^^^^^^^ JS string length = UTF-16 CODE UNITS, not bytes.
#
# THE TRIGGER AND THE CUT USE DIFFERENT UNITS. `byteCount > 25000` decides
# whether to enter the branch; `w.length > 25000` decides whether anything is
# actually removed. For UTF-8 text UTF-16 units are always <= bytes (ASCII is
# 1:1, a 4-byte emoji is 2 units), so a byte gate can never fire LATE -- but on
# this emoji-dense router it fires ~730 units early, and a file can trip the
# byte trigger while nothing is cut at all. Both are reported below, because
# the byte number explains the harness warning and the UTF-16 number is the
# one that actually loses content.
#
# The byte cut is applied AFTER the line cut and trims back to a line boundary,
# so it removes WHOLE ENTRIES too.
#
# Two earlier models were both wrong, in opposite directions, and each gave
# confidently wrong advice:
#   bytes-only (50000 / 26481 / 24458) said "shorten your hooks" -- useless when
#     the LINE cap binds, because a shorter line is still a line.
#   lines-only (200) said "shortening a line DOES NOT HELP" -- false when the
#     BYTE cap binds, where shortening is the only thing that helps.
# The two harness message forms are the tell: "N lines and X KB" is emitted only
# when BOTH caps blew; "N lines (limit: 200)" is the line cap alone.
#
# Rule: feedback_private_rule_16.
LOADER_LINES=200     # tL, from the binary
LOADER_BYTES=25000   # ez, from the binary
WARN_BYTES=22500     # fire well before the lowest observed cut
MAX_CHARS=200      # harness guidance: index entries are one-line hooks

[ -f "$INDEX" ] || exit 0

warnings=""

# 1. BOTH CAPS. Either one truncates, and they need OPPOSITE remedies: a line
#    over the line cap must be REMOVED, while bytes over the byte cap can be
#    reduced by shortening. Saying only one of those is how this script gave
#    wrong advice twice.
nlines=$(wc -l < "$INDEX" | tr -d ' ')
bytes=$(wc -c < "$INDEX" | tr -d ' ')
if [ "$nlines" -gt "$(( LOADER_LINES - 5 ))" ]; then
  warnings+="  • MEMORY.md is ${nlines} lines; the loader takes the first ${LOADER_LINES}.\n"
  warnings+="      Shortening a line does NOT help here — only REMOVING one does. Blank lines\n"
  warnings+="      cost a slot and carry nothing; reference_/project_ pointers belong in $OVERFLOW.\n"
fi
u16=$(python3 - "$INDEX" <<'PYU' 2>/dev/null || echo 0
import io,sys
print(len(io.open(sys.argv[1],encoding="utf-8").read().encode("utf-16-le"))//2)
PYU
)
if [ "${u16:-0}" -gt "$(( LOADER_BYTES - 1500 ))" ] || [ "$bytes" -gt "$(( LOADER_BYTES - 1500 ))" ]; then
  warnings+="  • MEMORY.md is ${u16} UTF-16 units and ${bytes} bytes, against a ${LOADER_BYTES} cap.\n"
  warnings+="      The CUT is on UTF-16 units ($(( LOADER_BYTES - ${u16:-0} )) left); the BYTE count only\n"
  warnings+="      decides whether the loader enters its truncation branch ($(( LOADER_BYTES - bytes )) left).\n"
  warnings+="      This cap cuts back to a line boundary, so it drops WHOLE entries. Shortening\n"
  warnings+="      long hooks IS the fix here — unlike the line cap, where only removal helps.\n"
fi
# 1b. THE DEAD ZONE — name the entries that are ALREADY past the cut. Size alone
#     under-sells this: those lines cost bytes and deliver nothing, and a new
#     entry appended at the bottom lands among them. NAME them, so the warning
#     is actionable rather than a tidiness nag that gets appended past.
if { [ "$nlines" -gt "$LOADER_LINES" ] || [ "$bytes" -gt "$LOADER_BYTES" ]; } && command -v python3 >/dev/null 2>&1; then
  dz=$(python3 - "$INDEX" "$LOADER_LINES" "$LOADER_BYTES" <<'PYDZ'
import io,sys
p,lim,cap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
lines = io.open(p,encoding="utf-8").readlines()
kept = lines[:lim]                      # the LINE cap, first
run, cut = 0, len(kept)                 # then the size cap, to a line boundary
for i,l in enumerate(kept):
    # UTF-16 code units: the unit `w.length > ez` actually compares.
    run += len(l.encode("utf-16-le")) // 2
    if run > cap:
        cut = i
        break
dead=[]
for l in lines[cut:]:
    if l.startswith(">"):
        t=l.split("](")[0].replace("> ","").lstrip("*[ ")
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
    warnings+="      slot and earlier entries migrate back down. REMOVE LINES: blank lines first,\n"
    warnings+="      then reference_/project_ pointers to $OVERFLOW. WHICH memories stop firing is a\n"
    warnings+="      decision for the operator.\n"
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
for f in ("MEMORY.md", os.environ.get("OVERFLOW", "OVERFLOW.md")):
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
  | grep -v -x -F -e MEMORY.md -e "$OVERFLOW" $(printf -- '-e %s ' $SKIPS) \
  | while read -r f; do grep -q "($f)" "$INDEX" "$MEM_DIR/$OVERFLOW" 2>/dev/null || echo "$f"; done)   # OVERFLOW.md is the lookup half (split 2026-09-02); a pointer there is indexed
if [ -n "$orphans" ]; then
  n=$(echo "$orphans" | grep -c .)
  warnings+="  • ${n} topic file(s) on disk are not indexed in MEMORY.md or $OVERFLOW (add a one-line pointer or delete):\n"
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
    if b == 'MEMORY.md' or b in os.environ.get('SKIPS', 'TOPOLOGY.md').split():
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
