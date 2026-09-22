#!/bin/bash
# skill_share.sh — generate shareable variants of the private skill masters.
#
# DERIVED SUBSTRATE: the masters in ~/.claude/skills/ are the SINGLE source of
# truth. The shareable copies are GENERATED. Never hand-edit the output — edit a
# master and regenerate. See the emitted CONTRACT.md.
#
# Transforms (deterministic): drop the "## This environment" block (machine-
# specific commands), drop "Sources:" pointer lines and any line referencing a
# private memory slug (feedback_/reference_/project_), flatten [[wikilinks]] to
# plain text, strip private script paths, trim trailing rules/blanks.
#
# Usage: skill_share.sh [src_skills_dir] [out_dir]
set -u
SRC="${1:-$HOME/.claude/skills}"
OUT="${2:-$HOME/.claude/skills-shareable}"

# WHICH SKILLS SHIP — DERIVED, not hand-listed. This was a hardcoded string and
# it was wrong FIVE times: self-correcting-substrate (renamed months earlier,
# skipped silently for ~3 months), then ste and retrieval-economy (gates 01 and
# 02, the only two fully built gates, absent from every published bundle), then
# the cold-reader agent, then collapse-round-trips. Each was fixed as an
# instance. The comment that survived those fixes said it plainly — "a hardcoded
# list needs a checker, not a careful author" — and the list stayed hardcoded.
#
# So the gate list is now read from the DEPLOYED conductor, which is the thing
# that decides what a gate's deployed form is. Add a gate there and it ships
# here. No estate->repo dependency: the conductor is already an estate path.
CONDUCTOR="$SRC/discipline/SKILL.md"
if [ ! -f "$CONDUCTOR" ]; then
  echo "skill_share: no conductor at $CONDUCTOR — refusing to publish a list I cannot derive" >&2
  exit 1
fi
DERIVED="$(grep -oE 'skills/[a-z0-9-]+' "$CONDUCTOR" | cut -d/ -f2 | sort -u)"

# Skills that ship but are NOT gates, so the conductor never names them.
EXTRA="discipline grill-me ka123n adversarial-inverse"
# DELIBERATELY EXCLUDED: ask-dont-pour. It is the six-lever BUNDLE that gates
# 02-05 replaced, and this suite's central rule is that no gate may bundle.
# `agents` is the bundle's agent DIRECTORY, not a skill — it matches the same
# grep and would be reported as a missing master forever.
EXCLUDE="ask-dont-pour
agents"

SKILLS="$(printf '%s\n%s\n' "$DERIVED" "$EXTRA" | tr ' ' '\n' | grep -v '^$' | sort -u \
         | grep -vxF "$EXCLUDE")"

# Agents the skills reference. Also derived: any agent definition whose name the
# conductor mentions. cold-reader was missing here for the same reason.
AGENT_SRC="$(dirname "$SRC")/agents"
AGENTS="$(ls "$AGENT_SRC" 2>/dev/null | sed 's/\.md$//' \
          | while read -r a; do grep -qF "$a" "$CONDUCTOR" && echo "$a"; done)"

# Deterministic scrub: cut env block, flatten wikilinks, drop Sources/slug lines,
# genericize private paths, trim trailing rules/blanks.
scrub() {
  awk '/^## This environment/{exit} {print}' "$1" \
  | sed -E \
      -e 's/\[\[([^]]*)\]\]/\1/g' \
      -e '/^[[:space:]]*[-*]?[[:space:]]*Sources?:/d' \
      -e '/feedback_[a-z0-9_]+|reference_[a-z0-9_]+|project_[a-z0-9_]+/d' \
      -e 's#~/\.claude/scripts/##g' \
      -e 's#/Users/[a-zA-Z0-9_.-]+/#~/#g' \
      -e 's/coywolffuturist/coywolf/g' \
      -e 's/coywolf-mind/<corpus>/g' \
      -e 's/mind grep/corpus grep/g' \
      -e 's/mind check/corpus check/g' \
      -e 's/mind consult/corpus consult/g' \
      -e 's/mind moons/corpus rulings/g' \
      -e 's/mind page/corpus page/g' \
      -e 's/mind_grep/corpus_grep/g' \
      -e 's/mind_check/corpus_check/g' \
      -e 's/mind_consult/corpus_consult/g' \
      -e 's/the den host/a second machine/g' \
  | awk '{a[NR]=$0} END{ last=NR; while(last>0 && (a[last]=="" || a[last]=="---")) last--; for(i=1;i<=last;i++) print a[i] }'
}

mkdir -p "$OUT" "$OUT/agents"
count=0
MISSING=0
for s in $SKILLS; do
  in="$SRC/$s/SKILL.md"
  [ -f "$in" ] || { echo "skill_share: $s is referenced but has NO master at $in" >&2; MISSING=1; continue; }
  mkdir -p "$OUT/$s"
  scrub "$in" > "$OUT/$s/SKILL.md"
  count=$((count+1))
done
# Publish the agent definitions (same scrub; they carry no env blocks today).
for a in $AGENTS; do
  [ -f "$AGENT_SRC/$a.md" ] || { echo "skill_share: agent $a referenced but NO def" >&2; MISSING=1; continue; }
  scrub "$AGENT_SRC/$a.md" > "$OUT/agents/$a.md"
done

# CONTRACT.md — the derived-substrate rule, on disk in the same pass.
cat > "$OUT/CONTRACT.md" <<'EOF'
# CONTRACT — shareable skills are GENERATED, do not hand-edit

- **Source of truth:** the skill masters in `~/.claude/skills/<name>/SKILL.md`
  and the agent masters in `~/.claude/agents/<name>.md`.
- **Derived artifact:** this directory (`skills-shareable/`), including
  `agents/` (the custom agents the skills reference, so cross-refs resolve).
- **Writer that bridges them:** `~/.claude/scripts/skill_share.sh`.
- **Rule:** edits made directly to files here are OVERWRITTEN on the next run.
  To change a shareable skill or agent, edit its master and re-run the writer.

## Transforms applied (master → shareable)

1. The `## This environment` block (machine-specific commands) is removed.
2. `Sources:` pointer lines and any line referencing a private memory slug
   (`feedback_*` / `reference_*` / `project_*`) are removed.
3. `[[wikilinks]]` are flattened to plain text.
4. Private script paths (`~/.claude/scripts/`, `/Users/<name>/`) are genericized.
5. Trailing horizontal rules and blank lines are trimmed.

Cross-references between skills (e.g. `discipline`, `karsholto`) are PRESERVED —
share the whole bundle so they resolve. The legacy `chromeqa` alias on `vizcheck`
is harmless and left in place.

Regenerate: `skill_share.sh`
EOF

echo "generated $count shareable skill(s) → $OUT"

if [ "${MISSING:-0}" = "1" ]; then
  echo "skill_share: REFUSING to report success with a referenced skill or agent missing." >&2
  exit 1
fi
