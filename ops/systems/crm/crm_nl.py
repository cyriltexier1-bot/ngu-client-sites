import argparse
import re
import requests
from common.config import HUBSPOT_ACCESS_TOKEN, HUBSPOT_API_KEY, SALESFORCE_ACCESS_TOKEN, SALESFORCE_INSTANCE_URL

REQUIRED = {
    'contacts:create': ['email', 'firstname', 'lastname'],
    'companies:create': ['name'],
    'deals:create': ['dealname'],
}


def classify_intent(text):
    t = text.lower()
    action = 'lookup'
    if any(w in t for w in ['create', 'add', 'new']): action='create'
    elif any(w in t for w in ['update', 'change', 'set']): action='update'
    elif any(w in t for w in ['list', 'show all']): action='list'
    elif any(w in t for w in ['associate', 'link']): action='associate'
    obj = 'contacts'
    for cand in ['contacts','companies','deals','owners','associations']:
        if cand[:-1] in t or cand in t:
            obj = cand
    return action, obj


def extract_fields(text):
    fields = {}
    m = re.search(r'email\s*[:=]\s*([^,\s]+)', text, re.I)
    if m: fields['email'] = m.group(1)
    for k in ['firstname','lastname','name','dealname']:
        m = re.search(rf'{k}\s*[:=]\s*([^,]+)', text, re.I)
        if m: fields[k]=m.group(1).strip()
    return fields


def validate_required(action, obj, fields):
    key = f'{obj}:{action}'
    missing = [f for f in REQUIRED.get(key,[]) if f not in fields]
    return missing


def hubspot_request(action, obj, fields):
    if not (HUBSPOT_ACCESS_TOKEN or HUBSPOT_API_KEY):
        return {'mode':'fallback', 'message':'HubSpot credentials missing; dry-run only', 'payload':fields}
    headers = {'Authorization': f'Bearer {HUBSPOT_ACCESS_TOKEN}', 'Content-Type':'application/json'} if HUBSPOT_ACCESS_TOKEN else {'Content-Type':'application/json'}
    params = {'hapikey': HUBSPOT_API_KEY} if HUBSPOT_API_KEY and not HUBSPOT_ACCESS_TOKEN else None
    base = 'https://api.hubapi.com/crm/v3/objects'
    if action == 'create':
        r = requests.post(f'{base}/{obj}', json={'properties': fields}, headers=headers, params=params, timeout=15)
        return {'status': r.status_code, 'body': r.text[:500]}
    if action in ('lookup','list'):
        r = requests.get(f'{base}/{obj}', headers=headers, params=params, timeout=15)
        return {'status': r.status_code, 'body': r.text[:500]}
    return {'mode':'not-implemented','action':action,'obj':obj}


def salesforce_request(action, obj, fields):
    if not (SALESFORCE_INSTANCE_URL and SALESFORCE_ACCESS_TOKEN):
        return {'mode':'fallback', 'message':'Salesforce credentials missing; dry-run only', 'payload':fields}
    return {'mode':'stub','message':'Salesforce adapter v1 placeholder', 'action':action, 'obj':obj, 'fields':fields}


def format_response(intent, obj, result):
    return f"Intent={intent} Object={obj}\nResult={result}"


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--provider', choices=['hubspot','salesforce'], default='hubspot')
    a = ap.parse_args()

    intent, obj = classify_intent(a.query)
    fields = extract_fields(a.query)
    miss = validate_required(intent, obj, fields)
    if miss:
        print(f"Missing required fields for {obj}:{intent}: {', '.join(miss)}")
        raise SystemExit(2)

    result = hubspot_request(intent, obj, fields) if a.provider == 'hubspot' else salesforce_request(intent, obj, fields)
    print(format_response(intent, obj, result))
