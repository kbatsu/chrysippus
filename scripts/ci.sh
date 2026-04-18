#!/usr/bin/env bash
#
# Run the full local CI suite. Mirrors the GitHub Actions `ci.yml` workflow.
#
# Usage:
#   scripts/ci.sh        # run all checks
#   scripts/ci.sh -v     # verbose test output

set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> render drift check"
python3 scripts/render.py --check

echo ""
echo "==> unit tests"
tests/run.sh "$@"

echo ""
echo "==> JSON manifest validation"
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))" && echo "  plugin.json OK"
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))" && echo "  marketplace.json OK"
for meta in rules/*/_meta.json; do
  python3 -c "import json; json.load(open('$meta'))" && echo "  $meta OK"
done

echo ""
echo "==> shell syntax check"
for f in hooks/*.sh scripts/*.sh tests/*.sh; do
  if [[ -f "$f" ]]; then
    bash -n "$f" && echo "  $f OK"
  fi
done

echo ""
echo "==> shellcheck (if installed)"
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck hooks/*.sh scripts/*.sh tests/*.sh 2>&1 | grep -v '^$' || echo "  no issues"
else
  echo "  shellcheck not installed; skipping"
fi

echo ""
echo "CI checks passed."
