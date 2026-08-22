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
run "gate 01 lints this repo's own prose" python3 gates/01-ste/lint_ste.py README.md CONTRACT.md gates
run "gate 01 baits — every check seen to fail" python3 gates/01-ste/baits.py
run "baits pair — no check ships unbaited" python3 lint/baits_pair.py
run "baits pair BAIT — the rule cannot exempt itself" python3 lint/bait_baits_pair.py
run "the surviving test suite" python3 test_gates.py
[ $fail -eq 0 ] && printf "\n\033[32mALL GATES PASS\033[0m\n" || printf "\n\033[31mGATES RED\033[0m\n"
exit $fail
