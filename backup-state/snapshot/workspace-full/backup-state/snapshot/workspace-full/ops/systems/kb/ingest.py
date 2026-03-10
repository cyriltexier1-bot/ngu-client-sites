import argparse
import requests
from common.db import init_db, get_conn, now_iso
from common.utils import normalize_url, content_hash, chunks, jdump
from common.embeddings import get_embedding_provider


def fetch_content(source):
    if source.startswith('http'):
        try:
            r = requests.get(source, timeout=20)
            return r.text
        except Exception:
            return ''
    try:
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def validate_source(source, source_type):
    if source_type in ('web','youtube','x') and not source.startswith('http'):
        return False, 'URL required for web/youtube/x'
    return True, ''


def fallback_fetch(source, source_type):
    chain = [source_type, 'web', 'text'] if source_type != 'text' else ['text']
    for t in chain:
        txt = fetch_content(source)
        if txt and txt.strip():
            return txt, t
    return '', None


def ingest_one(source, source_type='web'):
    init_db()
    ok, reason = validate_source(source, source_type)
    if not ok:
        return {'status':'invalid', 'reason': reason}
    text, used_type = fallback_fetch(source, source_type)
    if not text.strip():
        return {'status':'empty'}
    nurl = normalize_url(source) if source.startswith('http') else f'file://{source}'
    h = content_hash(text)

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''INSERT INTO kb_docs(source_type,source_id,normalized_url,content_hash,title,raw_text,metadata_json,created_ts)
                       VALUES(?,?,?,?,?,?,?,?)''',
                    (used_type or source_type, source, nurl, h, source[:120], text[:200000], '{}', now_iso()))
    except Exception:
        row = cur.execute('SELECT id FROM kb_docs WHERE normalized_url=? AND content_hash=?', (nurl,h)).fetchone()
        return {'status':'duplicate','doc_id': row['id'] if row else None}

    doc_id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
    ch = chunks(text)
    emb = get_embedding_provider().embed(ch)
    for i, c in enumerate(ch):
        cur.execute('INSERT INTO kb_chunks(doc_id,chunk_index,chunk_text,embedding_json) VALUES(?,?,?,?)',
                    (doc_id, i, c, jdump(emb[i])))
    conn.commit()
    return {'status':'ok','doc_id':doc_id,'chunks':len(ch)}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--type', default='web', choices=['web','youtube','x','pdf','text'])
    a = ap.parse_args()
    print(ingest_one(a.source, a.type))
