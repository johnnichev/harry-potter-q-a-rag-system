import ollama
import numpy as np
from ..config import EMBED_MODEL, OLLAMA_BASE_URL


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def embed_texts(texts: list[str]) -> np.ndarray:
    client = _client()
    vectors = []
    for t in texts:
        res = client.embeddings(model=EMBED_MODEL, input=t)
        vectors.append(np.array(res["embedding"], dtype=np.float32))
    return np.stack(vectors, axis=0)


def embed_query(text: str) -> np.ndarray:
    client = _client()
    res = client.embeddings(model=EMBED_MODEL, input=text)
    return np.array(res["embedding"], dtype=np.float32)
