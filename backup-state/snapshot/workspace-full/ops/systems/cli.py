import argparse
from crm.ingest import ingest
from council.nightly import run as council_run
from research.tool import research
from content.pipeline import submit as submit_content
from kb.ingest import ingest_one
from kb.retrieve import retrieve


def main():
    ap = argparse.ArgumentParser(prog='systems')
    sp = ap.add_subparsers(dest='cmd', required=True)

    c = sp.add_parser('crm-ingest'); c.add_argument('--backfill-days', type=int, default=60); c.add_argument('--run-type', default='manual')
    k1 = sp.add_parser('kb-ingest'); k1.add_argument('source'); k1.add_argument('--type', default='web')
    k2 = sp.add_parser('kb-query'); k2.add_argument('query'); k2.add_argument('--topk', type=int, default=5)
    ci = sp.add_parser('content-idea'); ci.add_argument('title'); ci.add_argument('--notes', default=''); ci.add_argument('--keywords', default=''); ci.add_argument('--create-task', action='store_true')
    r = sp.add_parser('research'); r.add_argument('query'); r.add_argument('--tier', choices=['t1','t2','t3'])
    n = sp.add_parser('council'); n.add_argument('--context', default='')

    a = ap.parse_args()
    if a.cmd == 'crm-ingest':
        print(ingest(a.backfill_days, a.run_type))
    elif a.cmd == 'kb-ingest':
        print(ingest_one(a.source, a.type))
    elif a.cmd == 'kb-query':
        print(retrieve(a.query, a.topk))
    elif a.cmd == 'content-idea':
        print(submit_content(a.title, a.notes, [k.strip() for k in a.keywords.split(',') if k.strip()], create_task_flag=a.create_task))
    elif a.cmd == 'research':
        print(research(a.query, a.tier))
    elif a.cmd == 'council':
        print(council_run(a.context))


if __name__ == '__main__':
    main()
