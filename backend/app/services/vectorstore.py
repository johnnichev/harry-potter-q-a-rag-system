import numpy as np


class InMemoryVectorStore:
    def __init__(self, embeddings: np.ndarray, chunks: list[str]):
        self.embeddings = self._normalize(embeddings)
        self.chunks = chunks

    def _normalize(self, m: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return m / norms

    def similar(self, query: np.ndarray, top_k: int) -> list[tuple[int, float]]:
        q = query / (np.linalg.norm(query) or 1.0)
        sims = self.embeddings @ q
        idxs = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[int(i)])) for i in idxs]
