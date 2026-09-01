#!/bin/bash
# guard_secrets.sh — Claude Code PreToolUse[Bash] hook that prevents leaking
# secrets and accidental public exposure.
# Deny rules: (1) `gh repo create` without --private; (2) any visibility flip to
# public via `gh repo edit` / `gh api`; (3) `git push` when outgoing commits
# contain secret-shaped files or secret-pattern content.
# Why it exists: a public repo leaking committed secrets is a one-way, expensive
# mistake — this makes it structurally hard to do by accident.
set -u

input=$(cat)
cmd=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0

deny() {
  /usr/bin/jq -n --arg r "$1" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
}

# ---- 1. New repos must be explicitly private ----
if printf '%s' "$cmd" | grep -qE '\bgh +repo +create\b'; then
  printf '%s' "$cmd" | grep -q -- '--private' || \
    deny "BLOCKED: gh repo create without --private. New repos should default private — add --private explicitly. Making a repo public is the maintainer's call, in their own terminal."
fi

# ---- 2. No visibility flips to public ----
if printf '%s' "$cmd" | grep -qE '\bgh +repo +edit\b' && \
   printf '%s' "$cmd" | grep -qE -- '--visibility[ =]+"?public'; then
  deny "BLOCKED: gh repo edit --visibility public. Visibility flips are the maintainer's call, in their own terminal."
fi
if printf '%s' "$cmd" | grep -qE '\bgh +api\b' && \
   printf '%s' "$cmd" | grep -qE 'visibility["'"'"'= :]+"?public|"private" *: *false|\bprivate=false'; then
  deny "BLOCKED: gh api call flipping a repo public. Visibility flips are the maintainer's call, in their own terminal."
fi

# ---- 3. Secret scan on outgoing commits before any git push ----
# Trigger on git+push robustly. Don't try to parse the invocation — `git -c k=v push`,
# `git -C dir push`, and `VAR=val git push` all defeat a structured regex. Over-
# triggering is safe: the scan only DENIES when real secrets are found, so a spurious
# scan (e.g. "push" in a commit message) just costs one cheap check. A missed push
# ships a secret — the asymmetry favors matching loosely.
if printf '%s' "$cmd" | grep -qE '\bgit\b' && printf '%s' "$cmd" | grep -qE '\bpush\b'; then
  cwd=$(printf '%s' "$input" | /usr/bin/jq -r '.cwd // empty')
  [ -n "$cwd" ] && cd "$cwd" 2>/dev/null
  if git rev-parse --git-dir >/dev/null 2>&1; then
    outgoing=$(git rev-list HEAD --not --remotes 2>/dev/null | head -200)
    if [ -n "$outgoing" ]; then
      # 3a. Secret-shaped FILES in outgoing commits (a committed .env is wrong even if "clean")
      bad_files=$(git show --name-only --pretty=format: $outgoing 2>/dev/null | sort -u | \
        grep -E '(^|/)\.env($|\.[^/]*$)|\.pem$|\.p12$|(^|/)id_(rsa|ed25519|ecdsa)($|\.)|(^|/)credentials(\.json)?$|(^|/)oauth-token$|(^|/)service[-_]account.*\.json$' || true)
      [ -n "$bad_files" ] && \
        deny "BLOCKED: outgoing commits contain secret-shaped files: $(printf '%s' "$bad_files" | tr '\n' ' '). Remove from history before pushing (.gitignore alone does not unstage history)."
      # 3b. Secret-pattern CONTENT in outgoing diffs
      if command -v gitleaks >/dev/null 2>&1; then
        gitleaks detect --no-banner --exit-code 9 --log-opts="HEAD --not --remotes" >/dev/null 2>&1
        [ $? -eq 9 ] && \
          deny "BLOCKED: gitleaks found secrets in outgoing commits. Inspect: gitleaks detect -v --log-opts=\"HEAD --not --remotes\""
      else
        # Pattern file (same one the companion pre-commit hook uses, if installed)
        patterns_file="$HOME/.git-hooks/secret-patterns.txt"
        [ -r "$patterns_file" ] || \
          deny "BLOCKED: secret-patterns.txt not found at $patterns_file — refusing to push unscanned. Install it from this kit's scripts/ folder, or install gitleaks."
        regex=$(grep -vE '^[[:space:]]*(#|$)' "$patterns_file" | paste -sd '|' -)
        # --pretty=format: scans diffs only (hashes in commit messages are public,
        # not secrets); lockfiles excluded (SHA-256 checksums false-positive on the
        # bare-64-hex crypto-key pattern).
        hits=$(git show --pretty=format: $outgoing -- \
          ':(exclude)*.lock' ':(exclude)package-lock.json' ':(exclude)yarn.lock' \
          ':(exclude)pnpm-lock.yaml' 2>/dev/null | grep -cE "$regex" || true)
        [ "${hits:-0}" -gt 0 ] && \
          deny "BLOCKED: $hits secret-pattern match(es) in outgoing commits (API keys / private keys / tokens). Inspect: git show \$(git rev-list HEAD --not --remotes) | grep -nE -f <(grep -v '^#' $patterns_file)"
      fi
    fi
  fi
fi

exit 0
