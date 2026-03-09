import argparse
import re
from common.db import init_db, get_conn, now_iso
from common.utils import jdump
from common.config import DEFAULT_TASK_PROJECT
from tasking.adapters import create_task
from tasking.queue import enqueue


def parse_input(text):
    lines = [l.strip('-* \t') for l in text.splitlines() if l.strip()]
    items = []
    for l in lines:
        if len(l) > 150:
            l = l[:150]
        if not re.search(r'\b(send|call|draft|prepare|review|update|book|create|follow|share|confirm|remind)\b', l, re.I):
            continue
        assignee = 'owner' if 'i will' in l.lower() or 'me ' in l.lower() else 'unknown'
        is_owner = assignee == 'owner'
        todoist_title = l[:120] if is_owner else ''
        items.append({'description': l, 'assignee': assignee, 'is_owner': is_owner, 'todoist_title': todoist_title})
    return items


def crm_enrich(conn, item):
    words = item['description'].split()
    for w in words:
        if '@' in w:
            row = conn.execute('SELECT * FROM crm_contacts WHERE email=?', (w.strip('.,'),)).fetchone()
            if row:
                return {'matched_contact': dict(row)}
    return {}


def persist_items(source, items):
    conn = get_conn()
    saved = []
    for it in items:
        enrich = crm_enrich(conn, it)
        conn.execute('''INSERT INTO action_items(source,description,assignee,is_owner,todoist_title,crm_enrichment_json,status,created_ts)
                        VALUES(?,?,?,?,?,?,?,?)''',
                     (source, it['description'], it['assignee'], 1 if it['is_owner'] else 0, it['todoist_title'], jdump(enrich), 'pending_approval', now_iso()))
        it2 = dict(it); it2['enrichment'] = enrich
        saved.append(it2)
    conn.commit()
    return saved


def direct_remind(text):
    m = re.search(r'remind me to (.+?) by (.+)', text, re.I)
    if not m:
        return None
    return {'description': m.group(1)[:150], 'assignee':'owner', 'is_owner':True, 'todoist_title': m.group(1)[:120], 'due': m.group(2)}


def create_approved(provider='todoist', ids=None, project=DEFAULT_TASK_PROJECT):
    conn = get_conn()
    q = 'SELECT * FROM action_items WHERE status="approved"'
    rows = conn.execute(q).fetchall() if not ids else conn.execute(f"SELECT * FROM action_items WHERE id IN ({','.join('?'*len(ids))})", ids).fetchall()
    out = []
    for r in rows:
        if not r['is_owner']:
            continue
        res = create_task(provider, r['todoist_title'] or r['description'][:120], r['description'], project)
        if str(res.get('status')).startswith('2') or res.get('status') == 'stub':
            conn.execute('UPDATE action_items SET status=? WHERE id=?', ('task_created', r['id']))
        else:
            enqueue(provider, {'title': r['todoist_title'] or r['description'][:120], 'body': r['description'], 'project': project}, str(res))
            conn.execute('UPDATE action_items SET status=? WHERE id=?', ('queued_retry', r['id']))
        out.append({'id': r['id'], 'result': res})
    conn.commit()
    return out


def mark_approval(mode, ids=None, edits=None):
    conn = get_conn()
    if mode == 'all':
        conn.execute('UPDATE action_items SET status="approved" WHERE status="pending_approval"')
    elif mode == 'none':
        conn.execute('UPDATE action_items SET status="rejected" WHERE status="pending_approval"')
    elif mode == 'some' and ids:
        conn.execute('UPDATE action_items SET status="rejected" WHERE status="pending_approval"')
        conn.execute(f"UPDATE action_items SET status='approved' WHERE id IN ({','.join('?'*len(ids))})", ids)
    if edits:
        for i, text in edits.items():
            conn.execute('UPDATE action_items SET description=?, todoist_title=? WHERE id=?', (text[:150], text[:120], i))
    conn.commit()


if __name__ == '__main__':
    init_db()
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    p1 = sp.add_parser('extract'); p1.add_argument('--source', default='notes'); p1.add_argument('--text', required=True)
    p2 = sp.add_parser('approve'); p2.add_argument('--mode', choices=['all','none','some'], required=True); p2.add_argument('--ids', default=''); p2.add_argument('--edits', default='')
    p3 = sp.add_parser('create'); p3.add_argument('--provider', default='todoist'); p3.add_argument('--ids', default='')
    p4 = sp.add_parser('direct'); p4.add_argument('--text', required=True)
    a = ap.parse_args()

    if a.cmd == 'extract':
        items = parse_input(a.text)
        saved = persist_items(a.source, items)
        for i, it in enumerate(saved, start=1):
            print(f"{i}. {it['description']} | assignee={it['assignee']} | owner={it['is_owner']} | enrich={it['enrichment']}")
    elif a.cmd == 'approve':
        ids = [int(x) for x in a.ids.split(',') if x.strip()] if a.ids else None
        edits = {}
        if a.edits:
            for pair in a.edits.split(';'):
                if ':' in pair:
                    k, v = pair.split(':', 1)
                    edits[int(k.strip())] = v.strip()
        mark_approval(a.mode, ids, edits if edits else None)
        print('approval updated')
    elif a.cmd == 'create':
        ids = [int(x) for x in a.ids.split(',') if x.strip()] if a.ids else None
        print(create_approved(a.provider, ids))
    elif a.cmd == 'direct':
        item = direct_remind(a.text)
        print(item if item else {'error':'No direct remind pattern matched'})
