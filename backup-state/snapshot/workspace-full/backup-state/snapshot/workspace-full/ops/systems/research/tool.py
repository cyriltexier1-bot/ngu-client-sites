import argparse
import requests
from common.db import init_db, get_conn, now_iso
from common.utils import jdump


def cached(conn, query):
    row = conn.execute('SELECT response_json FROM research_cache WHERE query=?', (query,)).fetchone()
    return row['response_json'] if row else None


def tier1(query):
    # lightweight free web scrape tier
    return {'tier':'t1', 'results':[{'title':'Stub result','url':'https://example.com','snippet':query}]}, 0.0


def tier2(query):
    # mid-cost API tier placeholder
    return {'tier':'t2', 'results':[{'title':'Deeper result','url':'https://example.org','snippet':query}]}, 0.002


def tier3(query):
    # premium tier placeholder
    return {'tier':'t3', 'results':[{'title':'Premium insight','url':'https://example.net','snippet':query}]}, 0.01


def research(query, force_tier=None):
    init_db()
    conn = get_conn()
    c = cached(conn, query)
    if c and not force_tier:
        return {'from_cache': True, 'data': c}

    if force_tier == 't3': data, cost = tier3(query)
    elif force_tier == 't2': data, cost = tier2(query)
    else:
        data, cost = tier1(query)
        if len(query) > 120:
            data, cost = tier2(query)

    conn.execute('INSERT OR REPLACE INTO research_cache(query,response_json,tier_used,cost_estimate,created_ts) VALUES(?,?,?,?,?)',
                 (query, jdump(data), data['tier'], cost, now_iso()))
    conn.execute('INSERT INTO research_logs(query,tier,provider,tokens,cost,created_ts) VALUES(?,?,?,?,?,?)',
                 (query, data['tier'], 'internal', 0, cost, now_iso()))
    conn.commit()
    return {'from_cache': False, 'data': data, 'cost': cost}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--tier', choices=['t1','t2','t3'])
    a = ap.parse_args()
    print(research(a.query, a.tier))
