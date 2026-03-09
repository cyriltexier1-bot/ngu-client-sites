import argparse
from datetime import datetime, timedelta
from common.db import get_conn, init_db, now_iso
from common.utils import jdump, jload
from tasking.adapters import create_task


def enqueue(provider, payload, error):
    conn = get_conn()
    conn.execute('''INSERT INTO task_retry_queue(provider,payload_json,error,attempts,next_attempt_ts,status,created_ts)
                    VALUES(?,?,?,?,?,?,?)''',
                 (provider, jdump(payload), error, 0, now_iso(), 'pending', now_iso()))
    conn.commit()


def process(limit=25):
    init_db()
    conn = get_conn()
    rows = conn.execute("SELECT * FROM task_retry_queue WHERE status='pending' ORDER BY id LIMIT ?", (limit,)).fetchall()
    for r in rows:
        payload = jload(r['payload_json'])
        res = create_task(r['provider'], payload.get('title','Untitled'), payload.get('body',''), payload.get('project','Inbox'))
        if str(res.get('status')).startswith(('2','stub')):
            conn.execute("UPDATE task_retry_queue SET status='done' WHERE id=?", (r['id'],))
        else:
            attempts = r['attempts'] + 1
            next_ts = (datetime.utcnow() + timedelta(minutes=min(60, attempts*10))).isoformat()+'Z'
            conn.execute("UPDATE task_retry_queue SET attempts=?, next_attempt_ts=?, error=? WHERE id=?",
                         (attempts, next_ts, str(res), r['id']))
    conn.commit()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=25)
    a = ap.parse_args()
    process(a.limit)
    print('retry queue processed')
