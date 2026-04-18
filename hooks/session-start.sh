#!/usr/bin/env bash
#
# chrysippus — SessionStart hook.
#
# Reads .claude/personas/active in the current project (if present). If the
# file names a valid persona, emits an instruction on stdout telling Claude
# to load and apply that persona's skill for the session. If the file is
# absent or empty, the hook exits silently — no change to session behavior.
#
# Run this hook with: bash session-start.sh
# Fails noisily on shell errors; fails silently (exit 0) on "no persona set".
#
# Security notes:
#   - No network calls.
#   - No eval, no exec of user-provided strings.
#   - State file contents validated against an allow-list.

set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
state_file="${project_dir}/.claude/personas/active"

if [[ ! -f "${state_file}" ]]; then
  # No auto-activation configured for this project.
  exit 0
fi

# Trim whitespace; take first non-empty line.
active="$(tr -d '[:space:]' < "${state_file}" | head -c 64)"

if [[ -z "${active}" ]]; then
  exit 0
fi

# Validate against allow-list. Reject anything else silently — the state
# file is not a place for arbitrary input.
case "${active}" in
  shakespeare|pirate|gen-alpha|toronto-mans)
    ;;
  *)
    # Unknown persona name — log once to stderr and exit cleanly.
    printf 'chrysippus/session-start: unknown persona %q in %s; ignoring.\n' \
      "${active}" "${state_file}" >&2
    exit 0
    ;;
esac

# Emit instructions for Claude. Output on stdout is injected into the
# session context per Claude Code's hook contract.
cat <<INSTRUCTION
## chrysippus: auto-activate persona

A \`chrysippus\` persona is configured for auto-activation in this project:

  **active persona**: \`${active}\`
  **state file**: \`.claude/personas/active\`

Load the skill at \`.claude/skills/${active}/SKILL.md\` now and apply its
register to all assistant prose for the rest of this session. Read the
sibling \`${active}.config\` for the active flavor and preservation toggles.

To disable auto-activation: run \`hooks/activate.sh off\` or delete the
state file.
INSTRUCTION
