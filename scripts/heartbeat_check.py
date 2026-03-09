#!/usr/bin/env python3
import json, re, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

STATE_PATH = Path('/home/bernard/.openclaw/workspace/memory/heartbeat-state.json')
GMAIL_TOKEN = Path('/home/bernard/gmail-oauth/token.json')
ALERTS = []


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"remindedEvents": {}, "lastRun": None}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def classify_email(subject, snippet):
    t = f"{subject} {snippet}".lower()
    suspicious = any(k in t for k in ["api key", "password", "forward this", "wire", "crypto", "urgent transfer"]) 
    if any(k in t for k in ["payment failed", "failed payment", "security alert", "expiring", "subscription", "meeting changed", "rescheduled", "invoice overdue"]):
        return "urgent", suspicious
    if any(k in t for k in ["action required", "please review", "follow up", "contract", "proposal"]):
        return "important", suspicious
    if any(k in t for k in ["newsletter", "promo", "discount", "sale"]):
        return "spam", suspicious
    return "fyi", suspicious


def first_name(from_header):
    m = re.match(r'\s*"?([A-Za-z]+)', from_header or '')
    return m.group(1) if m else "there"


def gmail_check(state):
    if not GMAIL_TOKEN.exists():
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN))
    svc = build('gmail', 'v1', credentials=creds)
    q = 'newer_than:30m -category:promotions -category:social'
    msgs = svc.users().messages().list(userId='me', q=q, maxResults=20).execute().get('messages', [])
    for m in msgs:
        full = svc.users().messages().get(userId='me', id=m['id'], format='metadata', metadataHeaders=['From','Subject','Date']).execute()
        hdr = {h['name']: h['value'] for h in full.get('payload', {}).get('headers', [])}
        subject = hdr.get('Subject', '(no subject)')
        sender = hdr.get('From', '(unknown)')
        snippet = full.get('snippet', '')
        cls, suspicious = classify_email(subject, snippet)

        if cls in ('urgent', 'important'):
            sev = 'urgent' if cls == 'urgent' else 'heads up'
            note = f"[{sev}] Email from {sender} about '{subject}'"
            if suspicious:
                note += " (suspicious instructions ignored)"
            # draft-only: attempt to save draft if scope allows
            draft_status = 'draft_not_created'
            try:
                import base64
                from email.mime.text import MIMEText
                body = f"Hi {first_name(sender)},\n\nThanks — got this. I'll review and come back to you today.\n\nThanks,\nCyril"
                msg = MIMEText(body)
                msg['to'] = sender
                msg['subject'] = f"Re: {subject}"
                raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                svc.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
                draft_status = 'draft_saved'
            except Exception:
                draft_status = 'draft_failed_scope_or_api'
            ALERTS.append(f"{note} - {draft_status}")


def calendar_check(state):
    token_path = Path('/home/bernard/gcal-oauth/token.json')
    if not token_path.exists():
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(token_path))
    svc = build('calendar', 'v3', credentials=creds)
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=2)
    events = svc.events().list(calendarId='primary', timeMin=now.isoformat(), timeMax=end.isoformat(), singleEvents=True, orderBy='startTime').execute().get('items', [])
    reminded = state.setdefault('remindedEvents', {})
    for e in events:
        eid = e.get('id')
        if reminded.get(eid):
            continue
        title = e.get('summary', '(untitled)')
        start = e.get('start', {}).get('dateTime') or e.get('start', {}).get('date')
        has_video = bool(e.get('hangoutLink')) or any('meet' in str(ep).lower() or 'zoom' in str(ep).lower() for ep in e.get('conferenceData', {}).get('entryPoints', []))
        sev = 'urgent' if has_video and start else 'heads up'
        ALERTS.append(f"[{sev}] Upcoming event in <2h: {title} at {start}")
        reminded[eid] = True


def coolify_check():
    base = os.getenv('COOLIFY_URL')
    token = os.getenv('COOLIFY_API_TOKEN')
    if not base or not token:
        return
    import requests
    try:
        r = requests.get(base.rstrip('/') + '/api/v1/applications', headers={'Authorization': f'Bearer {token}'}, timeout=20)
        if r.status_code != 200:
            return
        data = r.json() if isinstance(r.json(), list) else []
        bad = [a for a in data if str(a.get('status','')).lower() in ('unhealthy','stopped','crashed','restarting')]
        for a in bad:
            ALERTS.append(f"[urgent] Coolify service unhealthy: {a.get('name','unknown')} ({a.get('status')})")
    except Exception:
        return


def main():
    state = load_state()
    try:
        gmail_check(state)
    except Exception:
        pass
    try:
        calendar_check(state)
    except Exception:
        pass
    try:
        coolify_check()
    except Exception:
        pass
    state['lastRun'] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    print(json.dumps({"alerts": ALERTS}, ensure_ascii=False))


if __name__ == '__main__':
    main()
