import logging
import ollama
import numpy as np
from ..config import EMBED_MODEL, OLLAMA_BASE_URL


def _client() -> ollama.Client:
    """Create a pre-configured Ollama client bound to the local host."""
    return ollama.Client(host=OLLAMA_BASE_URL)


def _embed_single(client: ollama.Client, text: str) -> np.ndarray:
    """Embed a single piece of text and return a float32 vector.

    Raises RuntimeError if the embedding call fails.
    """
    try:
        result = client.embeddings(model=EMBED_MODEL, prompt=text)
        return np.array(result["embedding"], dtype=np.float32)
    except Exception as exc:
        logger = logging.getLogger("rag")
        logger.error("Embedding failed: %s", exc)
        raise RuntimeError(f"embedding failed: {exc}")


def embed_texts(texts: list[str]) -> np.ndarray:
    """Compute embeddings for a batch of chunk strings.

    Logs progress every 100 items to give feedback during startup.
    Returns a float32 array of shape (N, D).
    """
    client = _client()
    logger = logging.getLogger("rag")
    vectors: list[np.ndarray] = []
    for index, textItem in enumerate(texts):
        vectors.append(_embed_single(client, textItem))
        if (index + 1) % 100 == 0:
            logger.info("Embeddings: %d/%d", index + 1, len(texts))
    return np.stack(vectors, axis=0)


def embed_query(text: str) -> np.ndarray:
    """Compute a single query embedding as float32 vector."""
    client = _client()
    return _embed_single(client, text)
"""Embedding helpers for Ollama.

Provides thin wrappers to compute embeddings for chunks and queries using the
configured embedding model. All calls go through a local Ollama client.
"""
