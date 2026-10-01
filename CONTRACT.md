# CONTRACT — the discipline repo

> Per the derived-substrate rule: when a file becomes a DERIVED view of another
> source, ship a CONTRACT.md in the same pass. Manual edits to a derived side
> are overwritten.

## Where the working copy lives

**ONE editable clone, on the primary workstation — the machine the hooks, skills
and reviewer agents deploy to.** Moved there 2026-09-01 from the second machine,
which now holds only a `RETIRED.md` tombstone and is no longer a git repo.

The remote (`github.com/coywolffuturist/discipline`) is the backup and the
distribution. It is not a place work happens; git has no such place.

Why the move: everything this repo installs deploys to the primary workstation.
The repo was the only piece on the far side of an ssh hop, and that hop is where
the errors clustered — quoting failures in generated patch scripts, and twice a
forgotten install-outward step that left the deployed conductor stale while the
consistency checker reported green. The split also misled three independent
readers in one day, and left gate 14 permanently BLOCKED on the second machine
because its `cold-reader` agent never existed there.

**A second editable clone is forbidden.** If a scheduled job elsewhere ever needs
the gates, it clones READ-ONLY and only ever pulls. Two editable clones is the
exact failure named below.

## Source of truth

| path | role |
|---|---|
| `agents/` | DERIVED — a copy of `skills/agents/`, written by `scripts/install.sh`; edit `skills/agents/`, never this copy |
| `gates/NN-<name>/GATE.md` | **CANONICAL.** The read, the intent, the forms. Hand-written, reviewed by the operator before it lands. |
| `gates/NN-<name>/<form files>` | **CANONICAL.** The working artifact for each form. |
| `~/.claude/skills/<name>/SKILL.md` | **DEPLOYED COPY** of a skill form, on the machine that runs the agent. Installed from here. Never edit the deployed copy alone. |
| `~/.claude/hooks/*`, `~/.claude/settings.json` | **DEPLOYED** hook registrations. Installed from here. |
| `skills/` | **CANONICAL** (since 2026-10-01). Hand-edited here; installed as-is to `~/.claude/skills/` and `~/.claude/agents/` on every machine. `skills/discipline/SKILL.md` is written from `CONDUCTOR.md`. See `skills/README.md`. |
| `scripts/` | Standalone guards usable outside this repo. |

## The rule this repo exists to stop

Before 2026-08-22 the discipline suite lived in at least six places with no
git history and no path between them: two unversioned working copies on two
machines, two GitHub kits under different names, and two stale local clones of
those kits. An edit to one reached none of the others.

**Edit here. Install outward. Never the reverse.**

## Install discipline

1. Edit the canonical file in this repo.
2. Run the gate's own check, if it has one, and get it green.
3. Install to the deployed path.
4. Commit. The commit is the record that the deployed copy has a source.

## Known debt, recorded rather than hidden

- `~/.claude/skills/` is not a checkout of this repo; `scripts/install.sh` copies
  into it, and gate 13 reports any skill or agent whose installed copy differs.
- The suite spans TWO machines, and the deployed paths below resolve differently
  on each. The primary workstation runs the conductor and all 8 hooks. The second
  machine holds exactly ONE installed skill and no discipline hooks, which is why
  a skill-only form cannot be trusted to fire there. A reader who checks a
  `~/.claude/...` path on the wrong machine will correctly conclude the file is
  missing and incorrectly conclude the claim is false.
- RETIRED 2026-10-01: `skill_share.sh`, the scrubber that generated `skills/` from
  private masters. His order made the published copy the copy every machine runs,
  so nothing is generated and nothing needs scrubbing. Its protective job moved to
  gate 13: `nomess.py` scans the tree and the history for private words and real
  memory-page names, read from `~/.config/discipline` (never tracked).
