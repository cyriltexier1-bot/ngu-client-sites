import argparse
import json
from common.db import init_db, get_conn, now_iso
from common.embeddings import get_embedding_provider, cosine
from common.utils import jdump
from tasking.adapters import create_task


def dedup_score(title, conn):
    provider = get_embedding_provider()
    tv = provider.embed([title])[0]
    rows = conn.execute('SELECT title FROM content_ideas ORDER BY id DESC LIMIT 200').fetchall()
    if not rows:
        return 0.0
    sims = [cosine(tv, provider.embed([r['title']])[0]) for r in rows]
    kw_overlap = max((len(set(title.lower().split()) & set(r['title'].lower().split())) / max(1,len(set(title.lower().split()))) for r in rows), default=0)
    return min(100.0, (max(sims)*70 + kw_overlap*100*0.3))


def make_brief(title, notes):
    return {
        'hook': f'Why {title} matters now',
        'angle': notes[:220],
        'outline': ['Context', 'Key insight', 'Actionable takeaway'],
        'cta': 'Invite discussion or next step.'
    }


def submit(title, notes, keywords, provider='todoist', create_task_flag=False):
    init_db()
    conn = get_conn()
    dscore = dedup_score(title, conn)
    if dscore > 40:
        conn.execute('''INSERT INTO content_ideas(title,source_notes,keywords,score,status,dedup_score,brief_json,created_ts)
                        VALUES(?,?,?,?,?,?,?,?)''', (title, notes, ','.join(keywords), 0, 'rejected_dedup', dscore, '{}', now_iso()))
        conn.commit()
        return {'status':'rejected','dedup_score':dscore}

    brief = make_brief(title, notes)
    task_res = None
    task_id = None
    status = 'accepted'
    if create_task_flag:
        task_res = create_task(provider, f'Content brief: {title}', json.dumps(brief, ensure_ascii=False), 'Inbox')
        task_id = task_res.get('id')
    conn.execute('''INSERT INTO content_ideas(title,source_notes,keywords,score,status,dedup_score,brief_json,task_provider,task_external_id,created_ts)
                    VALUES(?,?,?,?,?,?,?,?,?,?)''',
                 (title, notes, ','.join(keywords), 75, status, dscore, jdump(brief), provider if create_task_flag else None, str(task_id) if task_id else None, now_iso()))
    conn.commit()
    return {'status':status, 'dedup_score':dscore, 'brief':brief, 'task':task_res}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('title')
    ap.add_argument('--notes', default='')
    ap.add_argument('--keywords', default='')
    ap.add_argument('--provider', default='todoist', choices=['todoist','asana','linear','notion'])
    ap.add_argument('--create-task', action='store_true')
    a = ap.parse_args()
    print(submit(a.title, a.notes, [k.strip() for k in a.keywords.split(',') if k.strip()], a.provider, a.create_task))
