import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from common.db import init_db, get_conn, now_iso
from common.config import LEARNING_PATH
from common.notify import notify


def load_learning():
    if LEARNING_PATH.exists():
        return json.loads(LEARNING_PATH.read_text())
    data = {
        'positive_keywords': ['proposal', 'follow up', 'meeting', 'invoice', 'urgent'],
        'negative_keywords': ['newsletter', 'unsubscribe', 'promo'],
        'sender_weights': {},
        'threshold': 45
    }
    LEARNING_PATH.write_text(json.dumps(data, indent=2))
    return data


def stage1_filter(item, learning):
    body = (item.get('subject','') + ' ' + item.get('body','')).lower()
    if any(k in body for k in learning['negative_keywords']):
        return False
    return True


def stage2_score(item, learning):
    txt = (item.get('subject','') + ' ' + item.get('body','')).lower()
    score = 20
    score += sum(15 for k in learning['positive_keywords'] if k in txt)
    score += learning['sender_weights'].get(item.get('sender','').lower(), 0)
    if 'calendar' in item.get('source',''):
        score += 8
    return min(score, 100)


def fetch_gmail_stub(days):
    now = datetime.utcnow()
    return [{
        'source': 'gmail', 'external_id': f'g-{i}', 'ts': (now - timedelta(days=i%days)).isoformat()+'Z',
        'sender': 'client@example.com', 'subject': f'Follow up #{i}', 'body': 'Can we schedule a meeting next week?'
    } for i in range(1, 12)]


def fetch_calendar_stub(days):
    now = datetime.utcnow()
    return [{
        'source': 'gcal', 'external_id': f'c-{i}', 'ts': (now - timedelta(days=i%days)).isoformat()+'Z',
        'sender': 'calendar', 'subject': f'Meeting {i}', 'body': 'Event with prospect.'
    } for i in range(1, 8)]


def ingest(backfill_days=60, run_type='backfill'):
    init_db()
    learning = load_learning()
    conn = get_conn()
    started = now_iso()
    conn.execute('INSERT INTO crm_runs(run_type,started_ts,status,details_json) VALUES(?,?,?,?)',
                 (run_type, started, 'running', '{}'))
    run_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    items = fetch_gmail_stub(backfill_days) + fetch_calendar_stub(backfill_days)
    inserted = 0
    for it in items:
        p1 = 1 if stage1_filter(it, learning) else 0
        s2 = stage2_score(it, learning) if p1 else 0
        if p1 and s2 >= learning.get('threshold',45):
            contact_email = it.get('sender') if '@' in it.get('sender','') else None
            if contact_email:
                conn.execute('''INSERT INTO crm_contacts(email,name,company,notes,last_seen_ts)
                                VALUES(?,?,?,?,?)
                                ON CONFLICT(email) DO UPDATE SET last_seen_ts=excluded.last_seen_ts''',
                             (contact_email, None, None, 'autocaptured', it['ts']))
        try:
            conn.execute('''INSERT INTO crm_items(source,external_id,ts,sender,subject,body,stage1_pass,stage2_score,metadata_json)
                            VALUES(?,?,?,?,?,?,?,?,?)''',
                         (it['source'], it['external_id'], it['ts'], it['sender'], it['subject'], it['body'], p1, s2, '{}'))
            inserted += 1
        except Exception:
            pass

    conn.execute('UPDATE crm_runs SET finished_ts=?, status=?, details_json=? WHERE id=?',
                 (now_iso(), 'ok', json.dumps({'inserted': inserted}), run_id))
    conn.commit()
    conn.close()
    notify(f'CRM ingest {run_type} completed. inserted={inserted}')
    return inserted


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--backfill-days', type=int, default=60)
    ap.add_argument('--run-type', default='manual')
    args = ap.parse_args()
    print({'inserted': ingest(args.backfill_days, args.run_type)})
