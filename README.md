# Discipline

A gate suite for agents that build things. Nineteen checks, each firing at one
moment and producing one artifact. A build is not done until every gate has a
row in a completion table, and every row reads FIRED, N/A or BLOCKED.

This one link is the whole thing. Start with the conductor.

## Start here

| read | what it is |
|---|---|
| [CONDUCTOR.md](CONDUCTOR.md) | the 19-gate table: which gate fires at which phase, the three legal states, the completion rule |
| [skills/ka123n](skills/ka123n) | the outer loop: before any work, rank the next three steps and show them; after any work, re-rank |
| [skills/grill-me](skills/grill-me) | the design interview: one question per turn, the next chosen from the last answer |
| [gates/](gates) | one folder per gate, `NN-<name>/GATE.md`: the read, the intent, the forms |
| [agents/](agents) | the four reviewers: `refuter`, `cold-reader`, `mechanism-auditor`, `vizcheck-reader` (a copy of `skills/agents/`) |
| [skills/](skills) | the deployed skills, written by the maintainer's install script from private masters (see CONTRACT.md); a plugin install ships them as they are; gates 16 and 17 have no skill by ruling, gate 19 ships as `95-percent-rule` |
| [hooks/](hooks) | the eight hooks that make the table fire unprompted |
| [lint/](lint) | the suite's own checks; `bash lint/all.sh` |

## Install

The repo is a Claude Code plugin.

    /plugin marketplace add coywolffuturist/discipline
    /plugin install discipline@coywolffuturist-discipline

That installs the conductor (`/discipline:discipline`), seventeen gate skills
(gates 16 and 17 have no skill by ruling; gate 19's is `95-percent-rule`),
`adversarial-inverse` (which `think-3x` and `root-cause` invoke), `ka123n`,
`grill-me`, the four reviewer agents and the eight hooks.

To use only the skills: copy `skills/` into your agent's skills directory and
`skills/agents/` into its agents directory. Take the whole bundle; the skills
cross-reference each other.

## Declare your suite

Write the gates you adopt, one per line, to `~/.claude/discipline-suite`:

    01 ste
    07 think-3x
    09 disprove-first
    18 adversarial-pass

The table renders the declared gates and only those. Gates 12 and 19 are always
in, because they define "complete". With no file, the suite is all nineteen.

## The gates

| # | gate | phase | fires when |
|---|---|---|---|
| 01 | ste | DESIGN | you write a prompt, page, plan or message |
| 02 | retrieval-economy | DESIGN | you are about to read a corpus, grep a repo, brief a subagent, or fire a model in a loop |
| 03 | collapse-round-trips | DESIGN | a sequence of calls could have been one |
| 04 | no-collision | DESIGN | you are about to touch shared substrate |
| 05 | substrate-search | DESIGN | you propose anything that survives the session |
| 06 | compile-it | DESIGN | you derive something for the second time |
| 07 | think-3x | DESIGN | there is a real fork with a second option worth naming |
| 08 | set-the-prior | DESIGN | before building: the outcome and a numeric prior |
| 09 | disprove-first | DESIGN | before code: name the refuting observation and run it |
| 10 | root-cause | VERIFY | something failed: how many distinct faults |
| 11 | karsholto | VERIFY | the change adds substrate: what a reader must hold |
| 12 | completer | VERIFY | you are about to write "follow-up" or "deferred" |
| 13 | nomess | VERIFY | orphans, dead links, stale state, remote state left open |
| 14 | cold-read | VERIFY | you ship something another agent reads cold |
| 15 | vizcheck | VERIFY | an interface you authored |
| 16 | chunk-it | VERIFY | a named move was produced, or something went wrong |
| 17 | write-back | VERIFY | a fact was derived that would cost more than one cheap call to re-derive |
| 18 | adversarial-pass | VERIFY | money, irreversibility, or anything outward-facing: a refuter runs or it does not ship |
| 19 | state-the-posterior | VERIFY | last: any claim of done, ready, verified or sure, one number per criterion |

The full triggers, the forms each gate takes, and where each read lives are in
[CONDUCTOR.md](CONDUCTOR.md).

## Three states, no fourth

- **FIRED**: name the artifact, never a checkmark.
- **N/A**: legal only by citing the gate's own written trigger.
- **BLOCKED**: the gate could not run; state what is now unverified.

"Skipped because it seemed unnecessary" is not a state, and omitting the row is
the failure the table exists to stop.

## The review record

Gate 18's record is a git note the reviewer writes on the commit it read:

    git notes --ref=reviews add -f -m "<VERDICT> refuter <yyyy-mm-dd> <one line>" <sha>

The verdict word comes first: `SURVIVED` or `REFUTED`. A push whose tip carries
no note, or a refuted one, is refused by the estate's pre-push hook. That hook
is private and is described here, not shipped.

## Known limits

Gate 01's language checks were cut to sentence length after three refutations,
and five known defects in its lint remain open (listed in HISTORY.md). `bash lint/all.sh`
checks install-outward drift only on the maintainer's machine, where the
install script has left its marker; everywhere else it skips the checks that
need the estate, prints how many, and exits non-zero: a reduced run is never a
pass, and a plugin or skills-only install is never called drift. The record of what was refuted, deleted and
corrected, with dates, is in [HISTORY.md](HISTORY.md); the newest entries are
at its top. Read it before
trusting any claim of enforcement.

## Layout and contract

    CONDUCTOR.md     the conductor
    CONTRACT.md      what is canonical here and what is derived
    HISTORY.md       the refutation record, verbatim
    gates/           canonical, hand-reviewed
    skills/          written from private masters by the maintainer's install script; do not hand-edit
    agents/          the reviewer agents (a copy of skills/agents/)
    hooks/           the hooks, registered by hooks/hooks.json
    lint/            the suite's own checks
    scripts/         standalone guards, usable without the rest

`gates/` is the reviewed source of each gate's read. `skills/` and `agents/` are
overwritten by the maintainer's install script. See [CONTRACT.md](CONTRACT.md).

## License

See [LICENSE](LICENSE).
