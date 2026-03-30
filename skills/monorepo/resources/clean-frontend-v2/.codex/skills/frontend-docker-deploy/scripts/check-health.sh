#!/usr/bin/env sh
set -eu

PORT="${APP_PORT:-8080}"
URL="http://127.0.0.1:${PORT}/health"

echo "Checking ${URL}"
response="$(curl -fsS "${URL}")"
echo "${response}" | grep -q '"status":"ok"'
echo "Health check passed"
