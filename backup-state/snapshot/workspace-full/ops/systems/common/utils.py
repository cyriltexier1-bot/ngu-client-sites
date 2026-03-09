import hashlib
import json
import re
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    p = urlparse(url.strip())
    netloc = p.netloc.lower().replace('www.', '')
    clean = p._replace(fragment='', query='')
    return urlunparse((clean.scheme or 'https', netloc, clean.path.rstrip('/'), '', '', ''))


def content_hash(text: str) -> str:
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def chunks(text: str, size=800, overlap=120):
    text = re.sub(r'\s+', ' ', text or '').strip()
    if not text:
        return []
    out = []
    i = 0
    while i < len(text):
        out.append(text[i:i+size])
        i += max(1, size-overlap)
    return out


def jdump(obj):
    return json.dumps(obj, ensure_ascii=False)


def jload(s, default=None):
    try:
        return json.loads(s)
    except Exception:
        return default if default is not None else {}
