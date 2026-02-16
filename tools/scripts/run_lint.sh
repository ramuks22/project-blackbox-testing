#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

check_tools() {
  local missing=0
  if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "ERROR: '$PYTHON_BIN' is missing."
    missing=1
  fi
  if ! command -v npm &> /dev/null; then
    echo "ERROR: 'npm' is missing."
    missing=1
  fi
  if ! command -v shellcheck &> /dev/null; then
    echo "ERROR: 'shellcheck' is missing."
    missing=1
  fi
  if [ "$missing" -eq 1 ]; then
    echo "Please install required lint tools before running this script."
    exit 1
  fi
}

check_tools

echo "[lint] Python (ruff)"
"$PYTHON_BIN" -m ruff check \
  "$ROOT_DIR/spec/compliance" \
  "$ROOT_DIR/adapters/python-pytest/src" \
  "$ROOT_DIR/adapters/python-pytest/tests"

echo "[lint] Python (black --check)"
"$PYTHON_BIN" -m black --check \
  "$ROOT_DIR/spec/compliance" \
  "$ROOT_DIR/adapters/python-pytest/src" \
  "$ROOT_DIR/adapters/python-pytest/tests"

echo "[lint] Node (eslint)"
(cd "$ROOT_DIR/adapters/node-playwright" && npm run lint)

echo "[lint] Shell scripts (shellcheck)"
shellcheck \
  "$ROOT_DIR/tools/scripts/run_compliance.sh" \
  "$ROOT_DIR/tools/scripts/run_lint.sh"

echo "[lint] all lint gates passed"
