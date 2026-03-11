import sqlite3
import json
from datetime import datetime
from .config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA foreign_keys=ON;')
    return conn


def now_iso():
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS crm_items (
      id INTEGER PRIMARY KEY,
      source TEXT NOT NULL,
      external_id TEXT,
      ts TEXT,
      sender TEXT,
      subject TEXT,
      body TEXT,
      stage1_pass INTEGER DEFAULT 0,
      stage2_score REAL DEFAULT 0,
      metadata_json TEXT,
      UNIQUE(source, external_id)
    );
    CREATE TABLE IF NOT EXISTS crm_contacts (
      id INTEGER PRIMARY KEY,
      email TEXT UNIQUE,
      name TEXT,
      company TEXT,
      notes TEXT,
      last_seen_ts TEXT
    );
    CREATE TABLE IF NOT EXISTS crm_runs (
      id INTEGER PRIMARY KEY,
      run_type TEXT,
      started_ts TEXT,
      finished_ts TEXT,
      status TEXT,
      details_json TEXT
    );

    CREATE TABLE IF NOT EXISTS kb_docs (
      id INTEGER PRIMARY KEY,
      source_type TEXT,
      source_id TEXT,
      normalized_url TEXT,
      content_hash TEXT,
      title TEXT,
      raw_text TEXT,
      metadata_json TEXT,
      created_ts TEXT,
      UNIQUE(normalized_url, content_hash)
    );
    CREATE TABLE IF NOT EXISTS kb_chunks (
      id INTEGER PRIMARY KEY,
      doc_id INTEGER,
      chunk_index INTEGER,
      chunk_text TEXT,
      embedding_json TEXT,
      FOREIGN KEY(doc_id) REFERENCES kb_docs(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS content_ideas (
      id INTEGER PRIMARY KEY,
      title TEXT,
      source_notes TEXT,
      keywords TEXT,
      score REAL,
      status TEXT,
      dedup_score REAL,
      brief_json TEXT,
      task_provider TEXT,
      task_external_id TEXT,
      created_ts TEXT
    );

    CREATE TABLE IF NOT EXISTS research_cache (
      id INTEGER PRIMARY KEY,
      query TEXT UNIQUE,
      response_json TEXT,
      tier_used TEXT,
      cost_estimate REAL,
      created_ts TEXT
    );
    CREATE TABLE IF NOT EXISTS research_logs (
      id INTEGER PRIMARY KEY,
      query TEXT,
      tier TEXT,
      provider TEXT,
      tokens INTEGER,
      cost REAL,
      created_ts TEXT
    );

    CREATE TABLE IF NOT EXISTS council_reports (
      id INTEGER PRIMARY KEY,
      report_date TEXT,
      persona TEXT,
      findings TEXT,
      score REAL,
      rank INTEGER,
      metadata_json TEXT
    );

    CREATE TABLE IF NOT EXISTS action_items (
      id INTEGER PRIMARY KEY,
      source TEXT,
      description TEXT,
      assignee TEXT,
      is_owner INTEGER,
      todoist_title TEXT,
      crm_enrichment_json TEXT,
      status TEXT,
      created_ts TEXT
    );

    CREATE TABLE IF NOT EXISTS task_retry_queue (
      id INTEGER PRIMARY KEY,
      provider TEXT,
      payload_json TEXT,
      error TEXT,
      attempts INTEGER DEFAULT 0,
      next_attempt_ts TEXT,
      status TEXT DEFAULT 'pending',
      created_ts TEXT
    );

    CREATE TABLE IF NOT EXISTS image_sessions (
      id INTEGER PRIMARY KEY,
      session_key TEXT,
      prompt TEXT,
      context_json TEXT,
      selected_asset TEXT,
      updated_ts TEXT,
      UNIQUE(session_key)
    );
    ''')
    conn.commit()
    conn.close()


def insert_json(conn, table, data):
    keys = ','.join(data.keys())
    vals = ','.join('?' for _ in data)
    conn.execute(f"INSERT INTO {table} ({keys}) VALUES ({vals})", tuple(data.values()))


def row_to_dict(row):
    return dict(row) if row else None


def safe_json(s, default=None):
    if s is None:
        return default if default is not None else {}
    try:
        return json.loads(s)
    except Exception:
        return default if default is not None else {}
