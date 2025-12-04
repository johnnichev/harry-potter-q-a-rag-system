import logging
import ollama
import numpy as np
from ..config import EMBED_MODEL, OLLAMA_BASE_URL


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def embed_texts(texts: list[str]) -> np.ndarray:
    client = _client()
    logger = logging.getLogger("rag")
    vectors = []
    for i, t in enumerate(texts):
        res = client.embeddings(model=EMBED_MODEL, prompt=t)
        vectors.append(np.array(res["embedding"], dtype=np.float32))
        if (i + 1) % 100 == 0:
            logger.info("Embeddings: %d/%d", i + 1, len(texts))
    return np.stack(vectors, axis=0)


def embed_query(text: str) -> np.ndarray:
    client = _client()
    res = client.embeddings(model=EMBED_MODEL, prompt=text)
    return np.array(res["embedding"], dtype=np.float32)
