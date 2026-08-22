#!/bin/bash
# The one door. Every gate, then the pairing rule, then the baits themselves.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
run() {
  local name="$1"; shift
  local out rc
  out=$("$@" 2>&1); rc=$?
  if [ $rc -eq 0 ]; then printf "\033[32mPASS\033[0m  %s\n" "$name"
  else printf "\033[31mFAIL\033[0m  %s\n" "$name"; echo "$out" | sed 's/^/      /'; fail=1; fi
}
# THE INVOCATION CONTRACT. An earlier version lint-ed a FIXED path list, so a
# brand-new page committed freely — proven 2026-08-22 by committing a 68-word
# sentence that every gate passed. A gate pointed at the wrong input is not a
# gate. Lint the changeset when there is one, the whole repo when there is not.
#
# --diff-filter=ACM excludes deletions and the pre-rename path. Both were
# reported as "unreadable" and blocked good commits.
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | tr "\n" " ")
if [ -n "${STAGED// /}" ]; then
  run "gate 01 lints the STAGED changeset" python3 gates/01-ste/lint_ste.py $STAGED
else
  run "gate 01 lints this repo's own prose" python3 gates/01-ste/lint_ste.py README.md CONTRACT.md gates
fi
run "gate 01 baits — every check seen to fail" python3 gates/01-ste/baits.py
run "baits pair — no check ships unbaited" python3 lint/baits_pair.py
run "baits pair BAIT — the rule cannot exempt itself" python3 lint/bait_baits_pair.py
run "the surviving test suite" python3 test_gates.py
[ $fail -eq 0 ] && printf "\n\033[32mALL GATES PASS\033[0m\n" || printf "\n\033[31mGATES RED\033[0m\n"
exit $fail
