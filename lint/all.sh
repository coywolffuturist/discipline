#!/bin/bash
# The one door. Every gate, then the pairing rule, then the baits themselves.
#
# PORTABILITY IS A CORRECTNESS ISSUE HERE. An earlier version used `mapfile`,
# which does not exist in the bash 3.2 that ships with macOS. The staged-file
# gate silently never ran and the chain still printed ALL GATES PASS. A step
# that does not execute must never read as a step that passed, so every run is
# counted and the total is checked at the end.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
ran=0
EXPECTED=10

run() {
  local name="$1"; shift
  local out rc
  out=$("$@" 2>&1); rc=$?
  ran=$((ran + 1))
  if [ $rc -eq 0 ]; then printf "\033[32mPASS\033[0m  %s\n" "$name"
  else printf "\033[31mFAIL\033[0m  %s\n" "$name"; echo "$out" | sed 's/^/      /'; fail=1; fi
}

# Which tree is being committed? This script lives in the discipline repo, but
# it may be installed as a hook in another one. Reading its OWN index there
# would lint the wrong tree and pass.
CALLER="$PWD"
if [ -n "${GIT_WORK_TREE:-}" ]; then CALLER="$GIT_WORK_TREE"
elif [ -n "${OLDPWD:-}" ] && [ -d "$OLDPWD/.git" ]; then CALLER="$OLDPWD"; fi

# bash 3.2 safe: NUL-delimited read, no mapfile, no word splitting on spaces.
STAGED=()
while IFS= read -r -d '' f; do
  STAGED+=("$CALLER/$f")
done < <(cd "$CALLER" 2>/dev/null && git diff --cached --name-only --diff-filter=ACM -z 2>/dev/null)

if [ "${#STAGED[@]}" -gt 0 ]; then
  run "gate 01 lints the STAGED changeset of $CALLER" python3 gates/01-ste/lint_ste.py "${STAGED[@]}"
else
  run "gate 01 lints this repo's own prose" python3 gates/01-ste/lint_ste.py README.md CONTRACT.md gates
fi
run "gate 01 baits — every check seen to fail" python3 gates/01-ste/baits.py
run "baits pair — no check ships unbaited" python3 lint/baits_pair.py
run "baits pair BAIT — the rule cannot exempt itself" python3 lint/bait_baits_pair.py
run "the surviving test suite" python3 test_gates.py
run "crumbs — the breadcrumb stream is readable" python3 lint/crumbs.py
run "quotes — every quoted artifact traces to the record" python3 lint/quotes.py
run "quotes BAIT — every quote check seen to fail" python3 lint/bait_quotes.py
# Added 2026-09-01. Two readers in one hour caught claims in this repo that had
# gone false — a banner saying the hooks were registered nowhere, and three gate
# rows citing a skill this repo does not ship. Both were true when written. A repo
# whose subject is "an eval must not report health it does not have" cannot leave
# its own claims to the author's memory.
run "consistency — this repo does not contradict itself" python3 lint/consistency.py
# Added 2026-09-01. Gate 13 went N/A zero times in 37 encounters, which is the
# signature of a standard too easy to meet. Only the REPO half runs here: the
# remote half needs the network, and a build must not depend on another host
# being reachable. Run `gates/13-nomess/nomess.py --remote` before claiming done.
run "nomess — no debris, no drift, no stale deployed copy" python3 gates/13-nomess/nomess.py --repo

if [ "$ran" -ne "$EXPECTED" ]; then
  printf "\033[31mFAIL\033[0m  only %d of %d steps ran. A step that did not execute is not a pass.\n" "$ran" "$EXPECTED"
  fail=1
fi
[ $fail -eq 0 ] && printf "\n\033[32mALL GATES PASS\033[0m\n" || printf "\n\033[31mGATES RED\033[0m\n"
exit $fail
