#!/usr/bin/env bash
set -euo pipefail
. ~/gmail-oauth/.venv/bin/activate
OUT="$(python3 /home/bernard/.openclaw/workspace/scripts/email_watch_elisa.py)"
COUNT="$(python3 - "$OUT" <<'PY'
import json,sys
obj=json.loads(sys.argv[1])
print(len(obj.get('alerts',[])))
PY
)"
if [ "$COUNT" -eq 0 ]; then
  exit 0
fi
MSG="$(python3 - "$OUT" <<'PY'
import json,sys
obj=json.loads(sys.argv[1])
print("\n".join(obj.get('alerts',[])))
PY
)"
openclaw message send --channel telegram --target 2134875160 --message "$MSG" >/dev/null
