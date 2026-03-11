#!/usr/bin/env bash
set -euo pipefail

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE="$(date -u +%F)"
WORKSPACE="/home/bernard/.openclaw/workspace"
BACKUP_ROOT="$WORKSPACE/backup-state"
SNAPSHOT="$BACKUP_ROOT/snapshot"
REPORT_JSON="$BACKUP_ROOT/last_report.json"
MISSING_FILE="$BACKUP_ROOT/missing.txt"

mkdir -p "$SNAPSHOT"
: > "$MISSING_FILE"

mark_missing() { echo "$1" >> "$MISSING_FILE"; }
copy_if_exists() {
  local src="$1" dst="$2"
  if [ -e "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
  else
    mark_missing "$src"
  fi
}

# Core files
copy_if_exists "$WORKSPACE/SOUL.md" "$SNAPSHOT/workspace/SOUL.md"
copy_if_exists "$WORKSPACE/MEMORY.md" "$SNAPSHOT/workspace/MEMORY.md"
copy_if_exists "$WORKSPACE/USER.md" "$SNAPSHOT/workspace/USER.md"
copy_if_exists "$WORKSPACE/AGENTS.md" "$SNAPSHOT/workspace/AGENTS.md"
copy_if_exists "$WORKSPACE/TOOLS.md" "$SNAPSHOT/workspace/TOOLS.md"
copy_if_exists "$WORKSPACE/ops/STATE.md" "$SNAPSHOT/workspace/ops/STATE.md"

# Full workspace snapshot
mkdir -p "$SNAPSHOT/workspace-full"
rsync -a --delete \
  --exclude '.git/' \
  --exclude 'node_modules/' \
  --exclude '.wrangler/' \
  --exclude '.openclaw/' \
  "$WORKSPACE/" "$SNAPSHOT/workspace-full/"

# OpenClaw operational definitions
mkdir -p "$SNAPSHOT/openclaw"
openclaw cron list > "$SNAPSHOT/openclaw/cron-list.txt" 2>&1 || mark_missing "openclaw cron list failed"
openclaw skills list > "$SNAPSHOT/openclaw/skills-list.txt" 2>&1 || mark_missing "openclaw skills list failed"
openclaw status --all > "$SNAPSHOT/openclaw/status-all.txt" 2>&1 || mark_missing "openclaw status --all failed"

copy_if_exists "$HOME/.openclaw/config.json" "$SNAPSHOT/openclaw/config.json"
copy_if_exists "$HOME/.openclaw/gateway.json" "$SNAPSHOT/openclaw/gateway.json"
copy_if_exists "$HOME/.openclaw/agents/main/bootstrap.md" "$SNAPSHOT/openclaw/bootstrap.md"

# Environment variable NAMES only
mkdir -p "$SNAPSHOT/env"
env | cut -d= -f1 | sort > "$SNAPSHOT/env/env-var-names.txt"

# Secret redaction
python3 - <<'PY'
from pathlib import Path
import re
root = Path('/home/bernard/.openclaw/workspace/backup-state/snapshot')
patterns = [
    (re.compile(r'ghp_[A-Za-z0-9]{20,}'), '[GITHUB_TOKEN]'),
    (re.compile(r'github_pat_[A-Za-z0-9_]{20,}'), '[GITHUB_FINE_GRAINED_TOKEN]'),
    (re.compile(r'x-access-token:[GITHUB_TOKEN]@\s]+@'), 'x-access-token:[REDACTED_SECRET]
    (re.compile(r'(?i)Bearer\s+[A-Za-z0-9\-\._~\+\/=]+'), 'Bearer [ACCESS_TOKEN]'),
    (re.compile(r'ya29\.[A-Za-z0-9\-_]+'), '[GOOGLE_ACCESS_TOKEN]'),
    (re.compile(r'1//[A-Za-z0-9\-_]+'), '[GOOGLE_REFRESH_TOKEN]'),
    (re.compile(r'(?im)^(.*(?:api[_-]?key|token|secret|password|passwd|client_secret)\s*[:=]\s*).+$'), r'\1[REDACTED_SECRET]'),
]
for p in root.rglob('*'):
    if not p.is_file():
        continue
    try:
        data = p.read_bytes()
    except Exception:
        continue
    if b'\x00' in data:
        continue
    text = data.decode('utf-8', errors='ignore')
    orig = text
    for pat, rep in patterns:
        text = pat.sub(rep, text)
    if text != orig:
        p.write_text(text)
PY

cd "$WORKSPACE"
mkdir -p backup-state
git add backup-state

CHANGED="$(git diff --cached --name-only | wc -l | tr -d ' ')"
if [ "$CHANGED" -gt 0 ]; then
  git commit -m "backup: $DATE daily setup snapshot (changed $CHANGED files)" >/dev/null
  git push origin main >/dev/null
  PUSH_STATUS="ok"
else
  PUSH_STATUS="no_changes"
fi

python3 - <<PY
import json
from pathlib import Path
missing_path = Path('/home/bernard/.openclaw/workspace/backup-state/missing.txt')
missing = [line.strip() for line in missing_path.read_text().splitlines() if line.strip()]
report = {
  'timestamp': '$TS',
  'push_status': '$PUSH_STATUS',
  'missing': missing
}
Path('/home/bernard/.openclaw/workspace/backup-state/last_report.json').write_text(json.dumps(report, indent=2))
PY

echo "BACKUP_OK:$PUSH_STATUS"
