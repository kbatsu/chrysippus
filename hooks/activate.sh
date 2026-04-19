#!/usr/bin/env bash
#
# chrysippus activate — set (or clear) the auto-activate persona for a
# Claude Code project.
#
# Writes the persona name to .claude/personas/active in the project dir.
# The SessionStart hook (hooks/session-start.sh) reads this file on every
# new session and injects activation instructions into Claude's context.
#
# Usage:
#   activate.sh <persona>   Enable auto-activation of <persona>
#   activate.sh off         Disable auto-activation (delete state file)
#   activate.sh status      Show current auto-activation state
#
# Available personas: shakespeare, pirate, gen-alpha, toronto-mans
#
# Security notes:
#   - Idempotent: running twice with the same persona has no side effect.
#   - No network calls.
#   - Only writes inside $CLAUDE_PROJECT_DIR/.claude/personas/.
#   - No eval, no exec of user-provided strings.

set -euo pipefail

PROGNAME="$(basename "$0")"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
STATE_DIR="${PROJECT_DIR}/.claude/personas"
STATE_FILE="${STATE_DIR}/active"

usage() {
  cat <<USAGE
${PROGNAME} — set the auto-activate persona for this Claude Code project.

Usage:
  ${PROGNAME} <persona>   Enable auto-activation of <persona>
  ${PROGNAME} off         Disable auto-activation (delete state file)
  ${PROGNAME} status      Show current auto-activation state

Available personas:
  shakespeare   Early Modern English (courtly / tavern / sonnet)
  pirate        Treasure Island / buccaneer (scurvy-dog / captain / drunk / shanty)
  gen-alpha     Internet-native ironic slang (unhinged / corporate / tutorial)
  toronto-mans          Toronto / MTE caricature (mans)
  ontario-bud           Rural-Ontario / Letterkenny-inspired caricature (bud)

State file: ${STATE_FILE}
USAGE
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

case "$1" in
# chrysippus:allow-list BEGIN
  gen-alpha|ontario-bud|pirate|shakespeare|toronto-mans)
# chrysippus:allow-list END
    mkdir -p "${STATE_DIR}"
    printf '%s\n' "$1" > "${STATE_FILE}"
    echo "${PROGNAME}: auto-activation enabled for persona '$1'"
    echo "  state file: ${STATE_FILE}"
    echo "  disable with: ${PROGNAME} off"
    ;;
  off|disable|none)
    if [[ -f "${STATE_FILE}" ]]; then
      rm -f "${STATE_FILE}"
      echo "${PROGNAME}: auto-activation disabled"
    else
      echo "${PROGNAME}: auto-activation was already disabled"
    fi
    ;;
  status|show)
    if [[ -f "${STATE_FILE}" ]]; then
      active="$(tr -d '[:space:]' < "${STATE_FILE}")"
      echo "${PROGNAME}: auto-activating persona '${active}' on session start"
      echo "  state file: ${STATE_FILE}"
    else
      echo "${PROGNAME}: no auto-activation configured"
      echo "  (no state file at ${STATE_FILE})"
    fi
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "${PROGNAME}: unknown argument '$1'" >&2
    echo "run '${PROGNAME} --help' for usage" >&2
    exit 1
    ;;
esac
