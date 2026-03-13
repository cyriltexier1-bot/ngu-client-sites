import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env', override=False)

DB_PATH = Path(os.getenv('SYSTEMS_DB_PATH', ROOT / 'data' / 'systems.db'))
ASSETS_DIR = Path(os.getenv('IMAGE_ASSETS_DIR', ROOT / 'data' / 'assets'))
CACHE_DIR = Path(os.getenv('RESEARCH_CACHE_DIR', ROOT / 'data' / 'cache'))
RETRY_DIR = Path(os.getenv('TASK_RETRY_DIR', ROOT / 'data' / 'retry'))
LEARNING_PATH = Path(os.getenv('CRM_LEARNING_PATH', ROOT / 'crm' / 'learning.json'))
DEFAULT_TASK_PROJECT = os.getenv('DEFAULT_TASK_PROJECT', 'Inbox')

TELEGRAM_BOT_TOKEN = [REDACTED_SECRET]
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

OPENAI_API_KEY = [REDACTED_SECRET]
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = [REDACTED_SECRET]
GOOGLE_REFRESH_TOKEN = [REDACTED_SECRET]
GOOGLE_USER_EMAIL = os.getenv('GOOGLE_USER_EMAIL', '')

HUBSPOT_API_KEY = [REDACTED_SECRET]
HUBSPOT_ACCESS_TOKEN = [REDACTED_SECRET]
SALESFORCE_INSTANCE_URL = os.getenv('SALESFORCE_INSTANCE_URL', '')
SALESFORCE_ACCESS_TOKEN = [REDACTED_SECRET]

TODOIST_API_TOKEN = [REDACTED_SECRET]
ASANA_ACCESS_TOKEN = [REDACTED_SECRET]
LINEAR_API_KEY = [REDACTED_SECRET]
NOTION_API_KEY = [REDACTED_SECRET]
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', '')

YOUTUBE_API_KEY = [REDACTED_SECRET]
X_BEARER_TOKEN = [REDACTED_SECRET]
BROWSERLESS_API_KEY = [REDACTED_SECRET]

IMAGE_PROVIDER = os.getenv('IMAGE_PROVIDER', 'stub')
IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'stub-v1')

for p in [DB_PATH.parent, ASSETS_DIR, CACHE_DIR, RETRY_DIR, LEARNING_PATH.parent]:
    p.mkdir(parents=True, exist_ok=True)
