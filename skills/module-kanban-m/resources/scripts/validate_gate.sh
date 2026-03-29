#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:-}"
if [[ -z "$SKILL_DIR" ]]; then
  echo "Usage: $0 <module-skill-dir>"
  exit 1
fi

fail() {
  echo "[FAIL] $1"
  exit 1
}

pass() {
  echo "[PASS] $1"
}

required_file() {
  local path="$1"
  [[ -f "$path" ]] || fail "missing required file: $path"
  [[ -s "$path" ]] || fail "file is empty: $path"
}

contains_text() {
  local path="$1"
  local pattern="$2"
  grep -qi "$pattern" "$path" || fail "missing required content '$pattern' in: $path"
}

SKILL_MD="$SKILL_DIR/SKILL.md"
USAGE_MD="$SKILL_DIR/resources/spec/USAGE.md"
TEST_REPORT="$SKILL_DIR/resources/spec/TEST_REPORT.md"
E2E_MD="$SKILL_DIR/resources/spec/E2E.md"

required_file "$SKILL_MD"
required_file "$USAGE_MD"
contains_text "$SKILL_MD" "## When to use"
contains_text "$USAGE_MD" "## Quick Start"
pass "doc gate passed"

required_file "$TEST_REPORT"
contains_text "$TEST_REPORT" "status: passed"
contains_text "$TEST_REPORT" "test command"
pass "test-report gate passed"

required_file "$E2E_MD"
contains_text "$E2E_MD" "core flow"
contains_text "$E2E_MD" "status: passed"
pass "e2e gate passed"

echo "Gate check passed for: $SKILL_DIR"
