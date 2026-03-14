import argparse
from pathlib import Path
from common.config import ASSETS_DIR, IMAGE_PROVIDER
from common.db import init_db, get_conn, now_iso


def load_session(conn, key):
    r = conn.execute('SELECT * FROM image_sessions WHERE session_key=?', (key,)).fetchone()
    return dict(r) if r else None


def save_session(conn, key, prompt, ctx, selected=None):
    conn.execute('''INSERT INTO image_sessions(session_key,prompt,context_json,selected_asset,updated_ts)
                    VALUES(?,?,?,?,?)
                    ON CONFLICT(session_key) DO UPDATE SET prompt=excluded.prompt, context_json=excluded.context_json,
                    selected_asset=COALESCE(excluded.selected_asset,image_sessions.selected_asset), updated_ts=excluded.updated_ts''',
                 (key, prompt, ctx, selected, now_iso()))
    conn.commit()


def generate_variant(prompt, idx, session_key):
    # provider abstraction; v1 writes placeholder artifact
    fname = f'{session_key}_v{idx}.txt'
    p = ASSETS_DIR / fname
    p.write_text(f'provider={IMAGE_PROVIDER}\nprompt={prompt}\nvariant={idx}\n')
    return str(p)


def run(session_key, prompt, variants=3, accept=None, revise=None):
    init_db()
    conn = get_conn()
    current = load_session(conn, session_key)
    if revise and current:
        prompt = current.get('prompt','') + ' | revision: ' + revise
    assets = [generate_variant(prompt, i+1, session_key) for i in range(variants)]
    selected = assets[int(accept)-1] if accept and 0 < int(accept) <= len(assets) else None
    save_session(conn, session_key, prompt, '{"mode":"v1"}', selected)
    return {'session': session_key, 'prompt': prompt, 'variants': assets, 'selected': selected}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('session_key')
    ap.add_argument('prompt')
    ap.add_argument('--variants', type=int, default=3)
    ap.add_argument('--accept')
    ap.add_argument('--revise')
    args = ap.parse_args()
    print(run(args.session_key, args.prompt, args.variants, args.accept, args.revise))
