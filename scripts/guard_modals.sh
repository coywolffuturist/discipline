#!/bin/bash
# guard_modals.sh — PreToolUse[Write|Edit] hook enforcing the no-browser-modals rule
# Deterministic half only: bans the
# native calls alert()/confirm()/prompt(). The HTML/CSS overlay-modal ban is judgment
# and stays in memory — a regex can't reliably tell a modal overlay from any dialog.
#
# False-positive guard: this repo is full of LLM `prompt(` calls, so bare alert/confirm/
# prompt are matched ONLY in browser-markup files; the unambiguous `window.*` form is
# matched in any file.
set -u

input=$(cat)
file=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.file_path // empty')
[ -z "$file" ] && exit 0
# content being written: Write → .content, Edit → .new_string
content=$(printf '%s' "$input" | /usr/bin/jq -r '.tool_input.content // .tool_input.new_string // empty')
[ -z "$content" ] && exit 0

deny() {
  /usr/bin/jq -n --arg r "$1" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
}

GUIDE="Banned: browser modals (alert/confirm/prompt) — they block the page, look like phishing, break flow. Use an inline pattern instead: an inline status banner (e.g. a _setStatus(text,tone) helper), a two-step button (click again to confirm), an inline form row, or a chat-injected message. No popup, no exception."

# Bare call — only in browser-markup files (avoids LLM `prompt(` / node CLI false positives)
case "$file" in
  *.html|*.htm|*.vue|*.svelte|*.jsx|*.tsx)
    printf '%s' "$content" | grep -qE '\b(alert|confirm|prompt)[[:space:]]*\(' && \
      deny "alert()/confirm()/prompt() in frontend markup ($file). $GUIDE"
    ;;
esac

# window.* form — unambiguous browser modal in ANY file type
printf '%s' "$content" | grep -qE '\bwindow\.(alert|confirm|prompt)[[:space:]]*\(' && \
  deny "window.alert/confirm/prompt() in $file. $GUIDE"

exit 0
