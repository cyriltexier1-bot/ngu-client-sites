#!/usr/bin/env python3
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

STATE_PATH = Path('/home/bernard/.openclaw/workspace/memory/elisa-email-watch.json')
TOKEN_PATH = Path('/home/bernard/gmail-oauth/token.json')


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"seen_ids": []}


def save_state(s):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(s, indent=2))


def main():
    state = load_state()
    seen = set(state.get("seen_ids", []))

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    svc = build('gmail', 'v1', credentials=creds)

    q = 'from:teamcyril@ngurealestate.com.au newer_than:2d'
    msgs = svc.users().messages().list(userId='me', q=q, maxResults=10).execute().get('messages', [])

    new_alerts = []
    for m in msgs:
        mid = m.get('id')
        if mid in seen:
            continue
        full = svc.users().messages().get(
            userId='me',
            id=mid,
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        headers = {h['name']: h['value'] for h in full.get('payload', {}).get('headers', [])}
        new_alerts.append(
            f"[heads up] New Elisa email: {headers.get('Subject','(no subject)')} | {headers.get('Date','')}"
        )
        seen.add(mid)

    state['seen_ids'] = list(seen)[-200:]
    save_state(state)

    print(json.dumps({"alerts": new_alerts}))


if __name__ == '__main__':
    main()
