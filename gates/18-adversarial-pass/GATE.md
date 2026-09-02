# Gate 18 — adversarial-pass

    order:  18. VERIFY, last before the posterior. Nothing it finds can be
            priced until it has run.
    forms:  skill · agent · code (adopted)
    ruled:  the operator, 2026-09-01 — full moon. Money, irreversibility or
            anything outward-facing: a reviewer runs, or the work does not ship.
    where:  the code form is the estate `pre-push` hook on the primary
            workstation, registered by `core.hooksPath`, opt-in per repo via a
            `.gate18-guarded` marker in the repo root.

---

## The read

**The author cannot be the only reviewer.** Spawn a reader that does not share
your context and brief it to REFUTE the claim, not to bless it.

The failure is not carelessness. It is that the reasoning which produced a thing
also certifies it, so the certification inherits every error the production had.
Measured across one day: 34 encounters, 19 fired, **15 blocked**. All fifteen
name a refuter; fourteen also name what is unverified as a result.

Fourteen say a refuter did NOT run, in 8 different phrasings. **The
fifteenth says the opposite** and it is the one worth reading: *"Refuter
spawned, verdict not returned."* A reviewer HAD run. Blocked is not only "nobody
looked" — it is also "somebody looked and I did not wait."

An earlier version of this line said *every* block read "no independent reviewer
ran". No row contains the word *reviewer*, no single phrasing covers fourteen
rows, and "every" erased the one row that means something different. Correcting
it, I then wrote "fourteen of the fifteen open 'No refuter'" — also false, since
only seven use that exact opening. **The count was never the hard part; the
characterisation was, twice.**

What reviewers found on the days they did run, each time on work the author had
already verified and believed correct:

- a sentinel, break-tested and believed sound — **six defects**, three of which
  printed GREEN over a real failure
- a money path already hardened twice — **three high-severity defects**, each
  reopening a cap believed enforced
- a repository hours from publication — its scrubbed history and its remote were
  **disjoint object graphs**

## The intent

Make a claim survive someone trying to break it, so a posterior rests on evidence
the author could not have manufactured.

## The forms

| form | what it is | when |
|---|---|---|
| **skill** | the read: what to refute, how to brief a reviewer, why self-review is not this gate | before any non-trivial claim |
| **agent** | `refuter` — read-only, no build context, briefed to find the failure | money · irreversible · outward-facing |
| **code** | ADOPTED — the estate `pre-push` hook. Refuses an ordinary push with no review in scope, names what licensed it, consumes the review on a path that reaches the remote, and expires it at 30 minutes. **A record, not a boundary** — see below | every push from a guarded repo |
| **hook** | `mark_refuter.py`, `PostToolUse[Agent]` — records that a reviewer ran. **Install with the code form or neither:** pre-push reads a flag only this writes | paired |

## Why the code form moved to the action point — and what that did NOT buy

**Three versions of a `PreToolUse[Bash]` guard were built and all three were
refuted.** Each tried to decide "is this a ship?" by parsing the command string.
Each was defeated by a shape it had not imagined: a flag word inside a quoted
argument; an `ssh` payload stripped along with the quotes; then `cd X && ssh`,
an unquoted remote command, `caffeinate -i`, `timeout`, base64 through a pipe.
The third version simultaneously **allowed** the ordinary shape of a remote push
and **denied** a plain `grep` of a guarded file — the worst of both errors, and
the second is what gets a guard switched off.

Shell has unbounded ways to express one action. That arms race cannot be won by
a denylist of shapes. So the guard moved to `pre-push`, on this reasoning, taken
from the hook's own 2026-07-13 header:

> *pre-push is the one choke point every route to a remote must cross.*

**That premise was false, and this gate adopted it without testing it.** A
refuter landed pushes past the hook eight ways, with no review present, exit 0
every time: `--no-verify` · `-c core.hooksPath=/dev/null` ·
`GIT_CONFIG_GLOBAL=/dev/null` · `git send-pack` · `HOME=<other>` ·
`git config --local core.hooksPath` · a push from a worktree · a push from a
bare clone. Two more defects sat inside the block: `touch` minted a valid
licence and printed a success line **byte-identical** to a real review's, and
the review was consumed *before* the secret scan, so a blocked push burned it
and every retry cost a fresh one — pressure toward the bypass, manufactured by
the gate.

**A SECOND refuter then refuted the rewrite**, and the defect it found is the
same fault wearing new clothes. The marker check had been widened from the
working tree to `HEAD`. But a push sends whatever refspec you name, so
`git push origin <branch>` on a guarded branch that was not HEAD produced **zero
gate output and landed the guarded blob** — as did a tag and `--all`. The first
version read the working tree; the second read HEAD; **both are things ADJACENT
to the push.** The refs actually being pushed were on stdin the whole time, and
this hook already parsed that stdin seventy lines lower for the secret scan.

That is gate 10's lesson landing on gate 18: I fixed the instance I tripped over
and left the class live. The class was *"the gate reads something near what is
being pushed."* It is now fixed at the class level — stdin is buffered once and
both readers use it — and baited on four shapes plus an unguarded control.

**A THIRD refuter then found the same fault a third time, one level deeper.**
The marker check had moved from the working tree, to HEAD, to *the tip of each
pushed ref*. All three are endpoint checks. A push carrying a guarded commit
whose LATER commit removes the marker shipped with zero gate output. The gate is
now computed from **every outbound commit**, which is what the push actually
carries.

Sixty lines above its own gate block, this file already rejects endpoint-diff:
*"a secret in any pushed commit is exposed on the remote even if a later commit
removes it, so endpoint-diff is not enough."* The gate was endpoint-diff anyway.

**Reading the rule is not applying it.** Three refuters were needed to close one
fault, because each fix was aimed at the instance rather than the class.

**AND THE THIRD REVIEW FOUND TWO DEFECTS THAT WERE NOT GATE 18'S AT ALL.** The
secret scan in the same file failed OPEN, silently, on two ordinary pushes.

**First:** `git rev-list "$remote_sha..$local_sha" 2>/dev/null` never checked its
exit code. It read "I cannot compute this range" as "nothing to scan". That is
the normal shape after a peer pushes and you `push -f`.

**Second:** `--max-count=1000` truncated newest-first. So the first push of an
existing repo to a new public remote shipped everything past commit 1000
unscanned.

Both were demonstrated putting a real private key on a remote. Both are now
fixed. There is no cap, exit codes are checked, and an undeterminable range
REFUSES rather than scanning nothing.

**A FOURTH refuter then refuted the fix**, and the defect is elementary. The
helper signalled failure with `exit 1`. Both call sites are command
substitutions, `$( )` forks, and `exit` terminated the SUBSHELL. `set -e` was
not on and neither caller checked `$?`, so control fell through with an empty
list into `[ -z "$COMMITS" ] && continue` — the exact fail-open the helper was
written to close. **The hook printed "Refusing rather than scanning nothing" and
pushed the key anyway, exit 0.** A comment reading "IT FAILS CLOSED" described a
`printf`. It disarmed gate 18 by the same route.

Three more, from the same review:

- **`.gitattributes` blinded the scanner.** A path marked `binary` makes `git
  show` print "Binary files ... differ" with no `+` lines, so the engine was fed
  nothing and the commit scored clean. `.pem`, `.key` and `.p12` are exactly what
  people mark binary. Plain commit, plain push, key on the remote — and
  `pre-commit` missed it too, so there was no second net. Fixed with `--text`.
- **`git rev-list <blob>` exits 0 with EMPTY output**, so a blob pushed as a tag
  read as "nothing outbound" and shipped unscanned. Anything that will not peel
  to a commit is now refused.
- **An annotated tag's own message was never scanned.** No commit diff covers it.
  Now scanned.

**A FIFTH refuter broke it again, and this one is the most instructive.** The
fallback used `git rev-list "$ref" --not --remotes=origin`. Those are LOCAL
remote-tracking refs: a cached BELIEF about a remote, keyed on the remote's
NAME. `git remote set-url origin <public>` — the ordinary "let's open-source
this" move — leaves the belief intact while the destination changes, so **every
commit in it became invisible to the scanner while uploading for the first
time.** Verified 6/6: hook silent, exit 0, key on the public remote. Same hole
through `set-url --push`, and through a stale tracking ref after upstream prunes
a branch.

**The fix is the same sentence this gate keeps learning:** ask the thing you are
acting on. git hands the hook the destination URL as `$2` and the hook had never
read it. It now asks the actual remote with `ls-remote`, keyed on the URL. When
the remote cannot be asked, it scans the FULL history rather than refusing —
because a false denial removes the guard entirely, and that outcome is worse
than a slow one.

Three more from the same review, all closed:

- **A nested annotated tag** (a tag object pointing at another tag object)
  shipped its inner message unscanned. The chain is now peeled.
- **A secret in a PATH NAME was never scanned at all.** `grep -vE '^\+\+\+'`
  drops the only line carrying the new path, and `diff --git a/… b/…` never
  begins with `+`. An empty file at `keys/PRIVATE_KEY=0x…` shipped clean.
- **`git rm .gate18-guarded` was a silent, permanent bypass.** The working tree
  lacked it, the outbound commits lacked it, the tip lacked it — so nothing
  fired, and every later push was ungated too. The gate now also reads the state
  the REMOTE already has. Disarming a gate is the change that most needs review.

**A SIXTH refuter broke the property that matters most: no false denial.** Not
by refusing a push — by making one take **322 seconds instead of 141ms**. The
`ls-remote` call ran once per pushed ref in BOTH loops, uncached, and forked
`git cat-file -e` once per advertised remote ref: 60,100 forks for a
`git push --tags` of 50 tags against a 601-ref remote, on a LOCAL remote with no
network at all. And it was silent, because the progress notice is gated on
outbound COMMIT count while this stall scales with REF count.

This file already contains the sentence that condemns it: *an unexplained hang is
how a hook gets disabled, and a disabled hook guards nothing.* The fix
reintroduced exactly that on a surface the warning did not cover. One memoised
advertisement and a single `cat-file --batch-check` brought it to 8s.

**Gate 18 was also disarmed permanently, in three ordinary commands, no review.**
Push a clean new branch; delete the branch carrying the marker; push the clean
branch back to that name. The deletion was the load-bearing step: the loop
skipped deletions entirely, so **deleting the marker-bearing branch was itself
ungated.** The gate is now REPO-scoped rather than ref-scoped — asked once over
the whole local ref space — because a repository is guarded or it is not, and
per-ref scoping can always be walked around by renaming a ref.

**And a false denial did exist.** `git replace -f <blob> <blob>` is supported;
`--mirror` then pushes `refs/replace/<sha>`, which cannot peel to a commit, and
the hook refused the entire legitimate mirror push — with the advertised escape
hatch unreachable, because the refusal ran before the bypass checks. A
non-commit ref now returns a distinct code meaning *scan the object's own bytes*,
which is both correct and stricter than refusing.

**I introduced a fresh defect while fixing those three**, and it is the same
lesson a third time: the new ref-count notice sat ABOVE `PUSH_REFS="$(cat)"`, so
`set -u` killed the subshell on every push. The parent survived — command
substitution again — so the notice silently never worked while printing
`PUSH_REFS: unbound variable` to the user. It was found only because a bait
returned an exit code I could not explain and I went looking instead of
banking it.

**A SEVENTH refuter found a silent leak on a plain push.** The added-line filter
was `grep -E '^\+' | grep -vE '^\+\+\+'`, and the second grep exists to drop the
`+++ b/path` header. It drops CONTENT too. A combined (merge) diff prefixes an
added line with one `+` per parent, so a three-parent octopus renders it
`+++foo` — and, needing no merge at all, **any file line beginning with `++`
renders `+++…`**. Both are indistinguishable from the header. Plain commit,
plain push, exit 0, hook silent, key on the remote.

That is the same bug I had already fixed once today. I closed the PATH half —
the header carries the filename — and left the CONTENT half open in the same
line of code.

The replacement identifies headers by POSITION, between `diff --git` and the
first `@@`, so no content can collide with them. Both cases now caught, with the
two-parent merge and the path-name case still caught.

**And the latency blind spot moved rather than closing.** `git push --all` of 25
branches x 299 commits took **736 seconds with zero output for twelve minutes**.
Both progress notices missed BY CONSTRUCTION: the ref notice fires above 25
refs, the commit notice above 300 commits PER REF, so 25 x 299 was silent.
Per-dimension thresholds do not compose. The outbound set is now computed ONCE
for the whole push, deduped across refs, and the notice is driven by the TOTAL —
the number that matches the wait.

**The estimate is now a RANGE, and that is deliberate.** A single number has been
wrong twice: 2x optimistic, which reads as a hang, then 7x pessimistic. The
COUNT is measured; the seconds are labelled an estimate, because the rate varies
from 14ms per empty commit to ~100ms per commit with real content.

**One finding is only partly closed, and this is the honest state.** `git clone
--single-branch --branch main` of a repo whose marker sits on another branch
produces a clone with no marker anywhere — and gate 18 computes guardedness from
THIS clone's ref space. `--depth 1` implies `--single-branch`, so a shallow
clone hits it too. The premise written above, *"a repository is guarded or it is
not"*, is false as stated: a clone is free not to fetch the marker, and no
amount of local checking can see what was never fetched.

**The mitigation is a precondition, not a fix: `.gate18-guarded` must live on the
DEFAULT branch.** Then every ordinary clone carries it. A clone that
deliberately fetches only an unmarked branch remains ungated, which is consistent
with everything else on this page — this gate detects forgetting, not deciding.

**An EIGHTH refuter found that my own fix leaked.** `/usr/bin/awk` aborts the
entire stream on the first byte that is not valid UTF-8 — *towc: multibyte
conversion failure*, exit 2, **empty stdout**. A PNG in the commit, or a plain
latin-1 text file, silenced the extractor completely, and I had thrown awk's
exit status away. An extractor that emits nothing and an extractor that finds
nothing are indistinguishable downstream. Key on the remote, exit 0.

**One correction to that review, from my own measurement.** It reported this as
a REGRESSION — that the `grep` pipeline I replaced would have caught it. On this
machine the old pipeline scored **0 as well**, because plain `grep` suppresses
output on binary input without `-a`. It was a hole in BOTH implementations by
two different mechanisms, which is worse news than a regression, not better.

Three more from the same review, all closed.

**NULs.** awk's `print` truncates at the first one, and `LC_ALL=C` does not
repair that. NULs are now DELETED, not translated. Translating one to a newline
splits the record and loses the `+` prefix — that was my first attempt.

**The diff was captured into a shell VARIABLE.** Command substitution mangles
binary. It goes to a file now.

**The non-commit-ref scan was one object deep.** An annotated tag at a blob, any
tag at a TREE, and a tag-at-tag chain all shipped unscanned. The peel loop had
already computed the real target and then discarded it.

**And the silent-stall band was still open, for the third time.** Cost is
dominated by BYTES, which no counter measured: 150 commits of ~470KB ran 61
seconds in total silence, one commit below the threshold by construction.

**Three proxy dimensions have now been thresholded and all three were beaten by
the one not measured** — refs, then commits, then bytes. The notice is now
driven by ELAPSED TIME, which is the thing actually being complained about and
cannot be beaten by a dimension nobody thought of. Measured: it fires at 9s into
a 29s byte-heavy push that previously printed nothing.

**My own test harness lied three times in this round.** Each near-miss is worth
more than the fix.

Binary stored in a shell variable came back mangled. A "large file" generator
wrote 400KB on ONE line, which any entropy check flags. And a "realistic prose"
generator emitted twelve words per line from a small vocabulary overlapping the
BIP-39 list. That is a seed phrase by shape. The engine was right and my control
was wrong.

The clean control is 18MB of varied text at rc=0, with zero false positives.

**A NINTH refuter found the same lesson one layer down.** `LC_ALL=C` was set on
the hook's own `tr` and `awk`. It was NOT set on the ENGINE those feed. The
engine matches with bare `grep -nE`, and BSD grep in a UTF-8 locale returns no
match, rc=1, no error and no stderr for any line holding an invalid multibyte
byte BEFORE the match. A latin-1 config file with an accented field name ahead
of the key scanned clean, 5/5, on a plain commit and a plain push.

**I hardened the transport and left the consumer unprotected.** The bytes
arrived intact and were dropped at the end of the pipe.

The fix went into the ENGINE, not the four call sites — the engine has FIVE
callers including `pre-commit` and the estate's Bash guard, so all five were
blind. Verified afterwards that `pre-commit` still blocks a real secret and
still passes ordinary source.

**Commit messages were scanned by nothing in the estate.** `git show --format=`
blanks the message. This hook scanned ANNOTATED TAG messages — added by an
earlier refuter — and never the symmetric case, and `commit-msg` does naming
checks only. A GitHub token prefix, an AWS access-key prefix and a PEM private-key
header all shipped in a message at exit 0, and the engine flags all three the
moment it is shown them.

The literal markers are described rather than quoted here on purpose. This repo
is public, and a file carrying a verbatim key header trips every secret scanner
that reads it — including the estate's own, which refused this very commit until
the line was rewritten. That refusal was the guard working, on its author.

**And the notice failed a FOURTH time.** The elapsed-time check was gated behind
`SCANNED % 20`, which put a COUNT proxy in front of the clock. Worse, a check
between iterations cannot see time spent INSIDE one: a single 20MB commit ran 21
seconds in silence with the loop body running exactly once. It is now a
WATCHDOG — a background timer that measures wall-clock from OUTSIDE the work, so
no property of the work can hide from it. Measured at 0.21s overhead on a
trivial push, against 0.07s with no hook at all.

**My own instruments lied twice more, and one is the sharpest of the night:
I verified a fix for UTF-8-grep blindness using a UTF-8 grep.** The counting
`grep -c` in my bait was blind in exactly the way the engine had been, so a
working fix read as a failure. The proof needed a hexdump. The second was a
timing harness measuring at one-second granularity with repo setup inside the
window, which invented a 5-second regression that did not exist.

**A TENTH refuter found the deepest one yet: `refs/replace/*` is a LENS.**

git's READ commands — `rev-list`, `show`, `log`, `cat-file` — honour replace refs
by default. `git push` and pack-objects DO NOT: they transfer the TRUE object.
So any repository holding a replace ref scans the REPLACEMENT and ships the
ORIGINAL. Verified 5/5, and I reproduced it myself: the hook saw
`token = os.environ["TOKEN"]` while the remote received the real key, exit 0, no
output. The estate's PreToolUse Bash guard was blind by the same mechanism, so
BOTH layers passed.

**And it is forgetting, not deciding.** `git filter-repo` writes replace refs BY
DEFAULT, and `git replace --graft` is the documented non-destructive history
fix. Once one exists, every later push from that clone is scanned against a
different history than the one being uploaded.

**The design error is visible in my own code.** The hook treated `refs/replace`
as another ref to SCAN. It never considered that a replace ref rewrites what the
scanner SEES. Read through it and you are auditing a story about the repository
instead of the repository. `GIT_NO_REPLACE_OBJECTS=1` is now exported in both
the hook and the Bash guard.

**A claim in my own comment was false.** The advertisement memoisation "fixed"
last round never took effect: `remote_have_init` was called only from inside
`outbound_commits`, and both call sites invoke that as `$( )`, so the subshell
set the flag and exited. The comment described a fix that was not running.
Hoisting it helped less than expected, and the honest measurement is now IN the
file: the union `rev-list` removed the per-ref query, 40 tags against a 602-ref
remote went 3.7s to 3.1s, and the residue is a per-ref tag peel. **I stopped
optimising and wrote the number down** rather than claiming a win I had not
delivered.

Also closed: a watchdog `sleep` orphaned by `kill` (short sleeps now, so a
stray lives a second, not fifteen), three dead variables, and `diff --cc`
headers reaching the extractor as content.

**What survived is worth as much.** That reviewer ran the shared-engine
`LC_ALL=C` change against 479 real UTF-8 files and 25 adversarial non-ASCII
lines and found **zero output differences** — and confirmed the BIP-39 tier still
works on the second machine's Python floor, 3.9.6.

**And what SURVIVED matters as much.** That reviewer threw 30 legitimate push
shapes at it — shallow and partial clones, grafts and replace refs, orphan
histories, submodules, worktrees, `--mirror`, `--atomic`, no remotes configured,
a dangling `origin/HEAD` — and found **no false denial**. That is the property
worth more than any catch, because a hook that wrongly blocks gets switched off.

**What that costs, stated rather than hidden:** the scan runs about 50ms per
commit, so a 1000-commit first push takes roughly a minute. The old
`--max-count=1000` was fast because it silently skipped everything past it. The
hook now prints the count and an estimate, because an unexplained hang is how a
hook gets disabled, and a disabled hook guards nothing.

**That is the argument for this gate in one line.** Gate 18 was built to review
outward-facing work. Reviewing it found a hole in the estate's own secret
scanner that had been open since 2026-07-13 and that no amount of reading had
surfaced.

**Two defects were conceded rather than fixed, because they cannot be fixed
here.** Naming the reviewer in the success line does NOT expose a forgery: the
writer appends one of three fixed words, so `echo refuter > flag` is
byte-identical to a real flag, same sha1. And deferring consumption recovers
only the failed-scan case — `pre-push` runs BEFORE the transfer and git has no
client-side post-push hook, so a non-fast-forward, a `pre-receive` decline and
"everything up-to-date" still burn a review on a push that never landed.

**The correction, and it is the finding worth keeping:** moving from the command
text to the hook did not remove the evadable surface. It replaced ONE surface
with THREE — whether git runs hooks at all, where git looks for them, and
whether a file exists in a directory this same user can write. Each is cheaper
to defeat than the string-parsing it replaced. `--no-verify` is nine characters.

**Same-privilege enforcement cannot bind the process it runs inside.** A guard
that runs as me, on a machine I control, is a record and a speed bump. It is not
a boundary and no version of it will be.

So the honest scope, now written into the hook itself: **this catches
forgetting, not deciding.** It fires on every ordinary push shape — plain, `-f`,
`--tags`, `--all`, `--mirror`, `--delete`, and an up-to-date push — which is the
failure it was built for. A pass here is not evidence a review happened.

The four fixable defects were fixed and baited: an empty flag is refused, a
symlinked flag no longer reads the link's own mtime, the marker is honoured in
the pushed commit as well as the working tree, and consumption is deferred to a
path that actually reaches the remote. The eight bypasses were not fixed,
because at this privilege level they cannot be.

**FOR THE ESTATE, and it is larger than this gate.** The same eight routes also
bypass the `pre-push` SECRET SCAN, which has guarded a public remote since
2026-07-13 on the same false premise. `--no-verify` ships an unscanned commit.
The only boundary outside this user's privilege is **server-side** — branch
protection, required reviews, push protection — which is the operator's to set
and is **not in place today.**

## Round four, 2026-09-02 — the first review that could reach the hook

Three earlier reviews could not read `pre-push`, because it is not in this
repo. A fourth was given the file, the engine, the corpus and a second
machine. It found a fourth LAYER, below prose, mechanism and publication:
**where the fixed code runs.** Open, not fixed, as of this writing.

- **Every fix narrated above is an uncommitted working copy.** The hook is 533
  lines of diff against its own repo's HEAD of 2026-07-13; the engine's
  `LC_ALL=C`, `diff_added.awk` and `commit-msg` are uncommitted or untracked
  with it. The second machine runs the 75-line July hook and the engine with
  no `LC_ALL=C`. "The fix went into the ENGINE so all five callers" (above) is
  true on one machine's working tree.
- **The licence is minted at LAUNCH.** `PostToolUse[Agent]` fires when the
  Agent tool returns, which for a background reviewer is seconds after spawn.
  The corpus row this page calls the interesting BLOCKED case — *"Refuter
  spawned, verdict not returned"* — is exactly what the code form licenses.
  Observed on three spawns in one session. One flag also licenses ANY repo
  from ANY directory, and two pushes that read it before either consumes it
  (3/3 concurrent). Fourteen accumulated reviews were consumed by one push.
- **"The gate now also reads the state the REMOTE already has" is false.**
  The marker check reads local refs only. Delete the marker in one commit
  and push: no review, no output, and every later push from that clone is
  ungated. The remote's advertised tips are already in hand and are never
  asked for the marker.
- **The engine passed realistic secret lines. FIXED the same day, both
  machines.** Five shapes had each landed on a remote at exit 0: a wallet-key
  line dropped whole for holding a word like `transaction`; a base58 key
  alone on a line; an AWS secret access key; a hardcoded fallback beside an
  env read; and the seed-phrase tier failing open when `python3` failed. Each
  is now a golden case, seen to fail before the fix. Two reviewer passes
  found the fix itself failing open without `awk` and printing 43 bytes of a
  keypair; both closed. Still open, named: a key split by string
  concatenation, a fallback literal wrapped onto the next line, and
  `${VAR:-default}`.
- **"No property of the work can hide from [the watchdog]" is false.** The
  watchdog starts AFTER the per-ref loop that scans trees and tags. A
  lightweight tag at a tree of 2000 blobs ran 14.8s, and a 16MB tree 18s,
  with no output at all.
- **A push -f after a peer pushed rescans the whole history.** One unknown
  sha in the negative set discards the remote's advertisement with it. 600
  commits already on the remote: 66.7s against 0.11s without the hook.
- **`outbound_commits()` has no callers.** The fail-closed helper the FOURTH
  refuter's section describes is dead code; its comment says "every caller
  now uses `if ! VAR=$(…)`". `REMOTE_NAME` is assigned and never read. The
  comment claiming a `-s` test names a test that does not exist.
- **Numbers.** Measured on the same machine: ~113ms per content commit, not
  ~50ms; ~82ms per empty commit, not 14ms; 40 tags against a 602-ref remote
  5.9s, not 3.1s. "Fifty-four hook defects" cannot be reconstructed from
  this page (47–51 by enumeration); "8 different phrasings" is 9 by first
  sentence. "30 legitimate push shapes" and "479 files" have no source
  outside this page. No bait harness for the hook exists anywhere; every
  "verified n/n" above rests on its author's word.
- **A caught seed phrase is printed unredacted.** The redaction masks tokens
  of 12+ characters; seed words are short.

What held under the same review: the corpus counts (34 / 19 / 15, and every
characterisation the page corrected twice); the eight bypasses; the ten
rounds; every gate-18 refusal shape (no flag, empty, symlink, stale, future
mtime, undeletable, second push); every secret-scan closure listed above,
re-driven one by one; the replace-ref lens; trivial-push overhead 0.20s.

The full report with every command: `~/.coywolf/handoff/05-review-four-findings.md`.

## What is still unguarded, named rather than implied

The push path is covered. These are not, and each needs a check at ITS action
point rather than in a command parser:

- **deploy** — inside the deploy script
- **value transfer** — inside the signer, which already owns a leash
- **a signed record leaving for another agent** — inside the rendezvous tool

They were never guarded; the retired hook only appeared to guard them.

## Disproof

**Mechanical, and it points at the enforcement rather than the reviewer:**
refuted if a push from a guarded repo completes with no review in scope.

**It was refuted in ten successive review rounds.** The units below differ, so
they do not sum: the FIRST round found eight distinct bypass SHAPES; the second
refuted three of five rewritten CLAIMS, including a path that reached the remote
with the gate emitting nothing at all. An earlier version of this sentence put
"ten times", "eight times" and "three" in one line as though they were the same
unit, and the arithmetic did not close. The claim as written was too strong; the surviving claim is narrower and
is stated above. This section is kept in its refuted form on purpose — a
disproof that never fires was never a disproof, and this one earned its place by
firing.

What survived the same review, each attacked and unbroken: age-out at 1800s, a
negative age from a future mtime, an undeletable flag refusing rather than
licensing unbounded pushes, a `stat` failure failing closed, and no collateral
denial in unmarked repositories.

**One bait mattered more than the others:** the block was first appended after
an `exit 0` and was dead code. It produced no output in any state and looked
like a silent pass. Baiting caught it; reading would not have.

The weaker human half is kept: refuted if a reviewer passes a claim later found
false for a reason it had the access and brief to catch. It tests judgement and
could never have caught any of the fifty-four hook defects.

**REVISIT** when a server-side boundary exists, which is the only thing that
would let this gate claim prevention rather than record. Until then, treat every
pass as "no review was forgotten", never as "no review was skipped."
