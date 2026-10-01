#!/bin/bash
# session_gate.sh — fire the gates that don't fire on their own.
#
# Written 2026-08-07. On 2026-08-06 the `discipline` skill existed from the first message of
# a long build session and was not invoked until the user asked for it, hours in. In between:
# three publishes that rendered dead backgrounds, four checkers that passed vacuously, and a
# machine loaded to 99% swap without anyone looking. Every one of those had a gate. None fired.
#
# The problem was never vocabulary. It was that nothing fired without the human.
#
# SILENT WHEN CLEAN — on purpose. A hook that speaks every session gets skimmed, and a gate
# that gets skimmed is a decoration. It only interrupts when it has something specific.
set -uo pipefail
OUT=""

# ── Is the Den safe to load? ─────────────────────────────────────────────────────────
# Blocking condition, not advice: >90% swap means render work will make things worse.
# The host name lives outside the repo (DISCIPLINE_DEN_HOST, or ~/.config/discipline/den_host);
# with neither set there is no second machine to check, and this block stays silent.
DEN_HOST="${DISCIPLINE_DEN_HOST:-$(cat "$HOME/.config/discipline/den_host" 2>/dev/null)}"
# The check COMMAND is machine-specific too (DISCIPLINE_DEN_CHECK, or
# ~/.config/discipline/den_check); with none set, nothing is checked.
DEN_CHECK="${DISCIPLINE_DEN_CHECK:-$(cat "$HOME/.config/discipline/den_check" 2>/dev/null)}"
if [ -n "$DEN_HOST" ] && [ -n "$DEN_CHECK" ] && command -v ssh >/dev/null 2>&1; then
  DEN=$(ssh -o ConnectTimeout=4 -o BatchMode=yes "$DEN_HOST" "$DEN_CHECK 2>/dev/null" 2>/dev/null)
  [ -n "$DEN" ] && OUT="${OUT}
⛔ HOST CHECK
${DEN}
   Restart it before any render/build work."
fi

# ── Is the RSI mechanism actually running? ───────────────────────────────────────────
# The project dir encodes $HOME with slashes as dashes. DERIVED, never
# written: this file lives in a repo with a remote, and the operator
# name belongs on no surface we publish (disclosure doctrine).
CC_PROJ="-$(printf %s "${HOME#/}" | tr / -)"
LEDGER_NAME="${DISCIPLINE_CHUNK_LEDGER:-$(cat "$HOME/.config/discipline/chunk_ledger" 2>/dev/null)}"
LEDGER="$HOME/.claude/projects/$CC_PROJ/memory/${LEDGER_NAME:-reference_chunk_ledger.md}"
if [ -f "$LEDGER" ]; then
  AGE=$(( ( $(date +%s) - $(stat -f %m "$LEDGER") ) / 86400 ))
  # Two bugs lived on this line. (1) grep -c exits 1 on no match, so `|| echo 0` appended a
  # SECOND 0 and the test below died on "0\n0" — take the first line, default only if empty.
  # (2) It counted '^|' TABLE ROWS. The ledger has never used a table; entries are '### 🔹'
  # headings. So it read 0 with 14 chunks on disk and would have cried "cold" forever —
  # a gate measuring something the file does not contain is indistinguishable from a broken
  # one. Caught only by running it against a FULL ledger and seeing it still fire.
  ENTRIES=$(grep -c '^### 🔹' "$LEDGER" 2>/dev/null | head -1); ENTRIES=${ENTRIES:-0}
  if [ "$AGE" -gt 7 ] || [ "$ENTRIES" -eq 0 ]; then
    OUT="${OUT}
📒 CHUNK LEDGER is cold — ${ENTRIES} entries, last touched ${AGE}d ago.
   His ruling: capture the breakthrough AT THE MOMENT, not in a handoff.
   If today produces a named move, append it before claiming done (discipline VERIFY #9)."
  fi
fi

# ── Is the off-machine mirror of the record still current? ────────────────────────────
# coywolf-mind holds 866 commits over 62 days and lived on ONE disk with zero
# remotes until 2026-09-21. His ruling that day: the Den stores our memory
# permanently, and nobody else can keep a well-ordered record of our growth.
# A record on one disk is not permanent.
#
# The mirror is refreshed hourly by com.coywolf.mirror-mind. THE STAMP IS WRITTEN
# ONLY AFTER A VERIFIED-GOOD UPDATE -- fsck clean AND head matching the Den -- so
# its age is the age of the last RESTORABLE copy, not the last time the job ran.
# That distinction is the whole point: a job that runs and produces a corrupt
# mirror must not look healthy.
STAMP="$HOME/.coywolf/state/mirror-mind.last_success"
if [ -f "$STAMP" ]; then
  AGE_H=$(( ( $(date -u +%s) - $(cat "$STAMP" 2>/dev/null || echo 0) ) / 3600 ))
  if [ "$AGE_H" -gt 72 ]; then
    OUT="${OUT}
🗄️  MIND MIRROR IS STALE — last verified-good copy ${AGE_H}h ago (refreshes hourly).
   The off-machine copy of 866 commits is drifting. Check:
     launchctl list com.coywolf.mirror-mind ; tail ~/.coywolf/cache/mirror-mind.log"
  fi
else
  OUT="${OUT}
🗄️  MIND MIRROR HAS NEVER SUCCEEDED — no stamp at $STAMP.
   The record has NO verified off-machine copy. This is the dead-disk exposure."
fi

# ── The two MCP levers — UNCONDITIONAL ──────────────────────────────────────────────
# These print every session, with or without other findings, because the failure
# mode is not ignorance. On 2026-08-19 two sessions each read files by hand for
# hundreds of turns with both levers live and callable, while the canon naming
# them sat indexed at the top of MEMORY.md. Canon existing and not being consulted
# is the single most expensive failure mode on record.
cat <<'LEVERS'
🔑 THE TWO MCP LEVERS — use them BEFORE reading files (canon: decision_private_ruling_01)
   1. THE MIND      mind_grep <term>   0 model calls · ~400 bytes · 0.04s   ← cheapest
                    mind_check <x>     0 model calls · retired/current
                    mind_consult <q>   1 OPUS CALL — the most EXPENSIVE door, not the first
   2. CODEBASE-MEMORY  search_code — repo as query, ~99% fewer tokens than reading.
                    Pass the full project key; never list_projects (54k chars).
   Reading a file by hand is the poured path wearing a shell prompt.
LEVERS

# ── CONDUCTOR + KA123N: ON BY DEFAULT ───────────────────────────────────────────────
# Operator ruling 2026-09-21: the conductor and ka123n are ON, not invoked.
#
# What this block replaced, and why every line of it was wrong:
#   1. It was CONDITIONAL on $OUT -- the discipline reminder appeared only when
#      something ELSE was already broken. On a clean session it never printed,
#      which is exactly the session where nothing else would catch a missing gate.
#   2. It said "discipline is the conductor; it does not self-invoke." That was a
#      true description of a defect, printed as if it were an instruction.
#   3. Its gate list was STALE: it taught `ask-dont-pour`, the six-lever bundle
#      that gates 02-05 REPLACED and that the conductor says must not be
#      reinstated under any name. It listed 15 gates where there are 20.
#
# It stays SHORT on purpose. Line 11 of this file warns that a hook which speaks
# every session gets skimmed -- and on 2026-09-20 that came true on the LEVERS
# block below: it printed, and the session made zero mind_grep calls all night.
# A print cannot enforce. The enforcement is hooks/hook_conductor_pre.py, which
# fires once before the first build action. This block only sets the frame.
cat <<'CONDUCTOR'
🎼 CONDUCTOR IS ON (operator ruling 2026-09-21) — discipline + ka123n by default.
   ka123n is the OUTER loop: SELECT the #1 step by EV-per-byte and SHOW the
   three-row window (each row carries WHY IT IS FIRST) before design work;
   SLIDE and re-rank after commit. Execute #1 -- never offer it.
   DESIGN 00-09 fire BEFORE building · VERIFY 10-19 before any claim of done.
   States are FIRED (name the artifact) · N/A (cite the trigger) · BLOCKED.
   There is no fourth state; PARTIAL, FAILED and SKIPPED are not states.
   Gate reads come from THE MIND (mind_grep / mind_check), never by reading
   files -- a gate satisfied by pouring context costs more than the gate saves.
CONDUCTOR

# ── Unread alerts on THIS machine ─────────────────────────────────────────────────────
# A job raises an alert by writing $ALERT_DIR/ALERT-<name>. On the den a relay sends each one to the
# operator; a job on this machine also copies its alert there. When that copy fails (the den is down,
# the usual reason a backup fails) this is the only reader, so it speaks at session start. Added
# 2026-09-23 after a refuter found the den-backup alert had no reader at all.
ALERT_DIR="${ALERT_DIR:-$HOME/.coywolf}"
for a in "$ALERT_DIR"/ALERT-*; do
  [ -f "$a" ] || continue
  OUT="${OUT}
🚨 ALERT $(basename "$a" | sed 's/^ALERT-//'): $(head -c 300 "$a")"
done

# ── The standing findings, only alongside something actionable ───────────────────────
if [ -n "$OUT" ]; then
  cat <<EOF
${OUT}

  If you build a CHECK, break what it detects and watch it go red before trusting it.
EOF
fi
exit 0
