# Gate 13 — nomess

    order:  13. VERIFY, after completer and before cold-read. Sweep once the
            work is finished, before anyone reads it.
    forms:  skill · tool · code
    ruled:  the operator, 2026-09-01 — full moon. The sweep includes REMOTE
            state. Linters where they help.
    where:  the tool runs from the primary workstation and reaches the second
            machine over ssh. The `--repo` scope needs no network; `--remote`
            does, and says so rather than reporting clean when it cannot look.

---

## The read

**Leave nothing behind that a later reader will mistake for live.** Orphans,
dead links, debris files, doc-vs-runtime drift — and state on machines you are
not looking at.

The failure that produced this gate is not untidiness. It is that this gate
recorded 37 encounters in one day and went N/A **zero times**. A gate that can
never fail to apply and always passes is not running; it is a row. In that same
day it missed a browser lock held for 25 minutes on the other machine, caught
only while listing residue by hand.

The remote half is the half that gets missed, because it is the half you cannot
see from where you are working.

## The intent

Finish the work everywhere it touched, so the next reader inherits a clean
surface rather than debris that reads as current.

## The forms

| form | what it is | when |
|---|---|---|
| **tool** | `nomess.py` — the sweep as a command. `--repo`, `--remote`, `--done`, or all three | before claiming done |
| **code** | `nomess.py --repo` wired into `lint/all.sh` | every build |
| **skill** | the read: what counts as mess, and that a class is swept rather than an instance | every ship |

**Three scopes, and the split is load-bearing.** `--repo` is invariant hygiene:
dead symlinks, debris files, deployed-copy drift. It runs in the build, needs no
network, and must always hold. `--remote` reaches the other machine and cannot be
in the build, because a build must not fail when another host is asleep.
`--done` catches single-copy work — untracked files and uncommitted edits.

`--done` is deliberately NOT in the build. Putting it there deadlocked instantly:
the pre-commit hook runs the build, the build failed because work was
uncommitted, so nothing could ever be committed. Uncommitted work is the normal
state of working; it is a defect only when you are about to claim done.

## Disproof

Refuted if the sweep reports clean and a reader then finds debris, drift or
remote state it had the access to see.

**That has already happened, twice, to this tool on its first day**, which is why
it is trusted only where it has been baited:

- The remote scope reported clean while four scratch files sat on the other
  machine. The remote shell is zsh, which *errors* on a glob with no matches and
  aborts the whole command — one stale pattern silently disabled every pattern.
- The replacement `find` was mangled passing through Python, the local shell, ssh
  and the remote shell, and reported clean again.

Both were caught by planting a known-positive, not by reading the output. The
current version lists plainly and matches in Python, where there is no shell.

**A clean result from this tool means nothing unless the tool has been seen to go
red.** Bait it after any change to what it looks for.

**REVISIT** when the second machine stops holding state worth sweeping, or when
a linter is added — the ruling allows linters and none is wired yet.
