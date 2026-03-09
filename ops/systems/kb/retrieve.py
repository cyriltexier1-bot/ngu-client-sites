import argparse
import json
from common.db import init_db, get_conn
from common.embeddings import get_embedding_provider, cosine


def retrieve(query, topk=5):
    init_db()
    qv = get_embedding_provider().embed([query])[0]
    conn = get_conn()
    rows = conn.execute('SELECT kb_docs.title, kb_chunks.chunk_text, kb_chunks.embedding_json FROM kb_chunks JOIN kb_docs ON kb_docs.id=kb_chunks.doc_id').fetchall()
    scored = []
    for r in rows:
        ev = json.loads(r['embedding_json']) if r['embedding_json'] else []
        scored.append((cosine(qv, ev), r['title'], r['chunk_text']))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:topk]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--topk', type=int, default=5)
    a = ap.parse_args()
    for s, t, c in retrieve(a.query, a.topk):
        print(f'[{s:.3f}] {t}\n{c[:240]}\n---')
