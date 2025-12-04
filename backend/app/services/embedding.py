import logging
import ollama
import numpy as np
from ..config import EMBED_MODEL, OLLAMA_BASE_URL


def _client() -> ollama.Client:
    """Create a pre-configured Ollama client bound to the local host."""
    return ollama.Client(host=OLLAMA_BASE_URL)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Compute embeddings for a batch of chunk strings.

    Logs progress every 100 items to give feedback during startup.
    Returns a float32 array of shape (N, D).
    """
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
    """Compute a single query embedding as float32 vector."""
    client = _client()
    res = client.embeddings(model=EMBED_MODEL, prompt=text)
    return np.array(res["embedding"], dtype=np.float32)
"""Embedding helpers for Ollama.

Provides thin wrappers to compute embeddings for chunks and queries using the
configured embedding model. All calls go through a local Ollama client.
"""
