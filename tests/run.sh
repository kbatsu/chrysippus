#!/usr/bin/env bash
#
# Run the full test suite locally. Mirrors the CI workflow.
#
# Usage: tests/run.sh [unittest args...]
#   tests/run.sh                        # run all tests
#   tests/run.sh tests.test_render      # run one test module
#   tests/run.sh -v                     # verbose

set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m unittest discover -s tests -p "test_*.py" "$@"
