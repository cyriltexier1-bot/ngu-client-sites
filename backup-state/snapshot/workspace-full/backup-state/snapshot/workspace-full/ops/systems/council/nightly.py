import argparse
from datetime import date
from common.db import init_db, get_conn, now_iso
from common.notify import notify

PERSONAS = [
    ('CFO', 0.30),
    ('Head of Sales', 0.25),
    ('Operations Lead', 0.20),
    ('Brand Strategist', 0.15),
    ('Customer Advocate', 0.10),
]


def analyze(persona, context):
    base = len(context) % 30 + 60
    findings = f'{persona} review: focus on risks/opportunities from latest CRM + content + research signals.'
    return findings, min(100, base)


def run(context=''):
    init_db()
    conn = get_conn()
    rows = []
    for persona, w in PERSONAS:
        findings, raw = analyze(persona, context)
        final_score = raw * w + 40 * (1-w)
        rows.append((persona, findings, final_score, w))
    rows.sort(key=lambda x: x[2], reverse=True)
    report_date = str(date.today())
    for i, (persona, findings, score, w) in enumerate(rows, start=1):
        conn.execute('''INSERT INTO council_reports(report_date,persona,findings,score,rank,metadata_json)
                        VALUES(?,?,?,?,?,?)''', (report_date, persona, findings, score, i, f'{{"weight":{w}}}'))
    conn.commit()
    top = rows[0]
    notify(f'Nightly council done. Top perspective: {top[0]} score={top[2]:.1f}')
    return rows


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--context', default='')
    a = ap.parse_args()
    print(run(a.context))
