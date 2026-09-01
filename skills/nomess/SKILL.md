---
name: nomess
description: Before claiming "done / ready / deployed / merged / clean" — and after any structural change — leave no mess. Run nomess.sh for the deterministic repo-hygiene scan (lint, untracked, stale branches, dead symlinks, unpushed); then run the JUDGMENT checks a script can't do (semantic orphans, stale config gates, doc-vs-runtime drift, label-store pollution, end-to-end smoke). Shorthand "/nomess".
---

# /nomess — leave no semantic, structural, or operational mess

Cleanup IS the work; a half-state is the mess. Two halves: a script
does the mechanical scan, you do the judgment. If any check fails, fix
it BEFORE claiming done — partial-done is the mess.

## 1. Mechanical scan — run the script

`nomess.sh [repo-path]` (defaults to cwd). It reports
✓/⚠/✗ for: changed-file lint (js/py), untracked surfaces, stale merged
branches, dead symlinks, empty dirs, unpushed commits. Exit 1 = hard
mess (lint failure or broken symlink) — fix before done. ⚠ items
(untracked, stale, unpushed) you must classify, not ignore:
gitignore / add / delete / push, with the reason noted.

Lint failures are real mess: a missing semicolon caught by eslint
`no-unexpected-multiline` can silently kill a feature for weeks while
passing every pixel-QA and smoke test. What a linter catches must
never wait for a human to notice. If a touched repo has no linter
config, note that substrate gap rather than skipping silently.

## 2. Judgment checks — what the script can't do

These need a model reading meaning, not a pattern. Each is ✓ / ⚠ noted
residue / ✗ fix now.

### 2a. Semantic orphans (the structural heart)

For anything you removed, repurposed, or relabeled this workstream,
grep every reference and reconcile — code, docs, memory, config:

```
grep -rn '<old-symbol-or-concept>' src/ docs/ scripts/ memory/ 2>/dev/null
```

Each hit: update / annotate-as-legacy / remove. Document any hit left
in place and why. A removed primitive whose references survive is a
trap for the next reader.

### 2b. Config gates that no longer mean something

For every `if cfg.X` / `if flag.Y` / `if stage.Z` in the touched
modules: does this gate still mean what it meant before your change?
A gate whose meaning silently flipped (e.g. a stage guard that now
gates "do nothing" instead of "do the old behavior") routes live
control flow on a lie — the loudest semantic orphan. Remove,
repurpose, or document the new meaning.

### 2c. Doc / runtime divergence

For the load-bearing docs of the touched area (README, the repo's
canonical file, the relevant CONTRACT.md, related memory): does
runtime match each present-tense claim? `status: active`, "cron
loaded", "loop closed" must be verified against runtime evidence
(process list, log mtime, ledger growth), not believed. Update the
doc in THIS workstream, or annotate as planned.

### 2d. Daemon / runtime state files

If the workstream touched a long-running daemon, check its state
files for references to a code path you removed, positions/state for a
structure that no longer exists, or field names the new code doesn't
write. Migrate, delete, or annotate.

### 2e. Test artifacts in label stores (KPI ground-truth pollution)

Any status/state field a KPI, scorer, grader, or fitness function
reads is a LABEL STORE — entries are training signal, not storage. For
every test/QA artifact this workstream created, check its disposition:
parked in a user-semantic state (`archived`, `accepted`, `done`)? That
is a fake label. Export to a backup file, then DELETE the row —
"archived as cleanup" is the canonical violation, because archive
feels like hygiene while writing noise into ground truth. Ask per
artifact: does anything grade on the bucket I'm putting this in?

### 2f. End-to-end smoke (the deployment-ready gate)

Before "deployed" or "ready," exercise the actual user-visible outcome
path — not just the parts you changed. State the outcome in one
sentence; build the smallest executable path that demonstrates it
(paper mode / dry-run counts); run it; confirm the expected log line.
Can't smoke it without going live? Say so explicitly and let the user
decide — subsystem evidence is not user-outcome evidence (the 95% Rule
in operational form).

## The report

One line per check, status ✓ / ⚠ / ✗. Any ✗ → fix before claiming
done. All ✓, or ⚠ with documented reasons → done, and the documented
residue goes in the user-facing report too.

## Cross-references

- `95-percent-rule` — sibling: nomess is the cleanup audit, .95 the
  readiness predicate. Often run both before claiming deployed.
- `substrate-search` — the mirror at the START (no duplicate built);
  nomess is the mirror at the END (no orphan left behind).
