#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "[preflight] ERROR: 'gh' is not installed."
  echo "[preflight] Install GitHub CLI first: https://cli.github.com/"
  exit 1
fi

if gh auth status >/dev/null 2>&1; then
  echo "[preflight] OK: gh auth status passed."
  exit 0
fi

echo "[preflight] ERROR: gh auth status failed."
echo "[preflight] Run: gh auth login"
exit 1
