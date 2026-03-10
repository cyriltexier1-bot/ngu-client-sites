import argparse
from common.db import get_conn, init_db


def cmd_recent(limit=20):
    conn = get_conn()
    rows = conn.execute('SELECT source,ts,sender,subject,stage2_score FROM crm_items ORDER BY ts DESC LIMIT ?', (limit,)).fetchall()
    for r in rows:
        print(f"[{r['source']}] {r['ts']} | {r['sender']} | {r['subject']} | score={r['stage2_score']}")


def cmd_search(term):
    conn = get_conn()
    q = f"%{term}%"
    rows = conn.execute('''SELECT source,ts,sender,subject,stage2_score FROM crm_items
                           WHERE subject LIKE ? OR body LIKE ? OR sender LIKE ? ORDER BY ts DESC LIMIT 50''', (q,q,q)).fetchall()
    for r in rows:
        print(f"[{r['source']}] {r['ts']} | {r['sender']} | {r['subject']} | score={r['stage2_score']}")


if __name__ == '__main__':
    init_db()
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    s1 = sp.add_parser('recent'); s1.add_argument('--limit', type=int, default=20)
    s2 = sp.add_parser('search'); s2.add_argument('term')
    a = ap.parse_args()
    if a.cmd == 'recent': cmd_recent(a.limit)
    elif a.cmd == 'search': cmd_search(a.term)
