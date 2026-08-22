# CONTRACT — the discipline repo

> Per the derived-substrate rule: when a file becomes a DERIVED view of another
> source, ship a CONTRACT.md in the same pass. Manual edits to a derived side
> are overwritten.

## Source of truth

| path | role |
|---|---|
| `gates/NN-<name>/GATE.md` | **CANONICAL.** The read, the intent, the forms. Hand-written, reviewed by the operator before it lands. |
| `gates/NN-<name>/<form files>` | **CANONICAL.** The working artifact for each form. |
| `~/.claude/skills/<name>/SKILL.md` | **DEPLOYED COPY** of a skill form. Installed from here. Never edit the deployed copy alone. |
| `~/.claude/hooks/*`, `~/.claude/settings.json` | **DEPLOYED** hook registrations. Installed from here. |

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

- `~/.claude/skills/` on both machines is not yet a checkout of this repo.
  Until it is, deployment is manual and drift is possible.
- The second machine currently holds ONE installed skill. Most of the suite is not
  deployed there at all, which is why a skill-only form cannot be trusted to
  fire on that machine.
- `skill_share.sh`, the writer named by the old `skills-shareable/CONTRACT.md`,
  is registered nowhere and has not run since 2026-06-10. A derived artifact
  with a dead writer.
