import hashlib
import random
from .config import OPENAI_API_KEY


class EmbeddingProvider:
    def embed(self, texts):
        raise NotImplementedError


class StubEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts):
        out = []
        for t in texts:
            seed = int(hashlib.sha256(t.encode('utf-8')).hexdigest()[:8], 16)
            rng = random.Random(seed)
            out.append([rng.uniform(-1, 1) for _ in range(32)])
        return out


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=[REDACTED_SECRET]
            resp = client.embeddings.create(model='text-embedding-3-small', input=texts)
            return [d.embedding for d in resp.data]
        except Exception:
            return StubEmbeddingProvider().embed(texts)


def get_embedding_provider():
    if OPENAI_API_KEY:
        [REDACTED_SECRET]
    return StubEmbeddingProvider()


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na = (sum(x*x for x in a) or 1) ** 0.5
    nb = (sum(y*y for y in b) or 1) ** 0.5
    return dot/(na*nb)
