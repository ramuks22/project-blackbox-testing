#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

fail=0
java_status="OK"
python_status="OK"

node_status="OK"

check_tools() {
  local missing=0
  if ! command -v mvn &> /dev/null; then
    echo "ERROR: 'mvn' (Maven) is missing."
    missing=1
  fi
  if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "ERROR: '$PYTHON_BIN' is missing."
    missing=1
  fi
  if ! command -v npm &> /dev/null; then
    echo "ERROR: 'npm' is missing."
    missing=1
  fi
  if [ "$missing" -eq 1 ]; then
    echo "Please ensure java (maven), python, and node are installed."
    exit 1
  fi
}

check_tools

latest_bundle() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    return 1
  fi
  local latest
  latest=$(ls -1dt "$dir"/*/ 2>/dev/null | head -n 1 || true)
  if [ -z "$latest" ]; then
    return 1
  fi
  echo "${latest%/}"
}

validate_bundle() {
  local bundle="$1"
  local manifest="$bundle/manifest.json"
  local context_log="$bundle/context.log"

  if [ ! -f "$manifest" ]; then
    echo "Missing manifest.json in $bundle"
    return 1
  fi
  if [ ! -f "$context_log" ]; then
    echo "Missing context.log in $bundle"
    return 1
  fi
  if ! "$PYTHON_BIN" "$ROOT_DIR/spec/compliance/validate_manifest.py" "$manifest"; then
    return 1
  fi
  return 0
}

run_expected_failure() {
  local name="$1"
  shift
  set +e
  "$@"
  local status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "ERROR: $name test unexpectedly passed"
    return 1
  fi
  return 0
}

run_java() {
  echo "[java] running JUnit 5 failing test"
  local dir="$ROOT_DIR/adapters/java-junit5"
  rm -rf "$dir/blackbox-reports"
  if ! (cd "$dir" && run_expected_failure "java" mvn -q -Dtest=SampleFailingTest test); then
    java_status="FAIL"
    fail=1
    return
  fi
  local bundle
  bundle=$(latest_bundle "$dir/blackbox-reports") || {
    echo "[java] no bundle found"
    java_status="FAIL"
    fail=1
    return
  }
  if ! validate_bundle "$bundle"; then
    java_status="FAIL"
    fail=1
    return
  fi
}

run_python() {
  echo "[python] running pytest failing test"
  local dir="$ROOT_DIR/adapters/python-pytest"
  rm -rf "$dir/blackbox-reports"
  (cd "$dir" && "$PYTHON_BIN" -m pip install -e . >/dev/null)
  if ! (cd "$dir" && run_expected_failure "python" "$PYTHON_BIN" -m pytest -q tests/test_failing.py); then
    python_status="FAIL"
    fail=1
    return
  fi
  local bundle
  bundle=$(latest_bundle "$dir/blackbox-reports") || {
    echo "[python] no bundle found"
    python_status="FAIL"
    fail=1
    return
  }
  if ! validate_bundle "$bundle"; then
    python_status="FAIL"
    fail=1
    return
  fi
}

run_node() {
  echo "[node] running Playwright failing test"
  local dir="$ROOT_DIR/adapters/node-playwright"
  rm -rf "$dir/blackbox-reports"
  (cd "$dir" && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install >/dev/null)
  if ! (cd "$dir" && run_expected_failure "node" npm test); then
    node_status="FAIL"
    fail=1
    return
  fi
  local bundle
  bundle=$(latest_bundle "$dir/blackbox-reports") || {
    echo "[node] no bundle found"
    node_status="FAIL"
    fail=1
    return
  }
  if ! validate_bundle "$bundle"; then
    node_status="FAIL"
    fail=1
    return
  fi
}

run_golden() {
  echo "[compliance] running golden reference check"
  if ! validate_bundle "$ROOT_DIR/spec/compliance/golden/9f2a0c1b3d4e5a6b_20260202T143000Z"; then
    echo "ERROR: Golden bundle failed validation!"
    fail=1
    exit 1
  fi
}

run_golden
run_java
run_python
run_node

echo ""
echo "Compliance summary:"
echo "  java:   $java_status"
echo "  python: $python_status"
echo "  node:   $node_status"

echo ""

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "❌ COMPLIANCE FAILED"
  echo "See individual adapter logs above for details."
  exit 1
fi

echo ""
echo "✅ COMPLIANCE PASSED"

