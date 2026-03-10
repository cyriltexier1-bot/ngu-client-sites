import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def notify(msg: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f'[notify:stdout] {msg}')
        return False
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg}, timeout=10)
        return True
    except Exception:
        print(f'[notify:fallback] {msg}')
        return False
