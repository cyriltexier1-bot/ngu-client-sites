#!/usr/bin/env bash
set -u

BASE_URL="${1:-${BASE_URL:-http://127.0.0.1:8080}}"

PAGES=(
  "/"
  "/assistant-dashboard/"
  "/pauleauz-landing/"
)

DASHBOARD_JS="assistant-dashboard/app.js"
PASS_COUNT=0
FAIL_COUNT=0

echo "QA check started"
echo "Base URL: ${BASE_URL}"
echo

check_page() {
  local path="$1"
  local url="${BASE_URL%/}${path}"
  local result
  local code

  result=$(curl -sS -L -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null)
  code="$result"

  if [[ "$code" =~ ^[0-9]{3}$ ]] && [[ "$code" -lt 400 ]]; then
    echo "[PASS] ${path} -> HTTP ${code}"
    ((PASS_COUNT++))
  else
    echo "[FAIL] ${path} -> HTTP ${code:-N/A}"
    ((FAIL_COUNT++))
  fi
}

for page in "${PAGES[@]}"; do
  check_page "$page"
done

echo
if node --check "$DASHBOARD_JS" >/dev/null 2>&1; then
  echo "[PASS] node --check ${DASHBOARD_JS}"
  ((PASS_COUNT++))
else
  echo "[FAIL] node --check ${DASHBOARD_JS}"
  ((FAIL_COUNT++))
fi

echo
echo "Summary: ${PASS_COUNT} passed, ${FAIL_COUNT} failed"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  exit 1
fi

exit 0
