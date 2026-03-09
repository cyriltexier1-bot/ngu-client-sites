import requests
from common.config import TODOIST_API_TOKEN, ASANA_ACCESS_TOKEN, LINEAR_API_KEY, NOTION_API_KEY


def create_task(provider, title, body='', project='Inbox'):
    if provider == 'todoist':
        if not TODOIST_API_TOKEN:
            return {'status':'fallback', 'id':None, 'message':'missing TODOIST_API_TOKEN'}
        r = requests.post('https://api.todoist.com/rest/v2/tasks',
                          headers={'Authorization': f'Bearer {TODOIST_API_TOKEN}'},
                          json={'content': title, 'description': body, 'project_id': project if project.isdigit() else None}, timeout=15)
        return {'status': r.status_code, 'id': r.json().get('id') if r.ok else None, 'body': r.text[:300]}
    if provider == 'asana':
        if not ASANA_ACCESS_TOKEN:
            return {'status':'fallback','id':None,'message':'missing ASANA_ACCESS_TOKEN'}
        return {'status':'stub','id':None,'message':'asana adapter v1 placeholder'}
    if provider == 'linear':
        if not LINEAR_API_KEY:
            return {'status':'fallback','id':None,'message':'missing LINEAR_API_KEY'}
        return {'status':'stub','id':None,'message':'linear adapter v1 placeholder'}
    if provider == 'notion':
        if not NOTION_API_KEY:
            return {'status':'fallback','id':None,'message':'missing NOTION_API_KEY'}
        return {'status':'stub','id':None,'message':'notion adapter v1 placeholder'}
    return {'status':'error','message':f'unknown provider {provider}'}
