import logging
import numpy as np


class InMemoryVectorStore:
    def __init__(self, embeddings: np.ndarray, chunks: list[str]):
        self.logger = logging.getLogger("rag")
        # Sanitize embeddings to avoid NaN/Inf issues and clamp extremes
        clean = np.nan_to_num(embeddings, nan=0.0, posinf=0.0, neginf=0.0)
        clean = np.clip(clean, -1e6, 1e6)
        self.embeddings = self._normalize(np.ascontiguousarray(clean, dtype=np.float32))
        self.chunks = chunks

    def _normalize(self, m: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return m / norms

    def similar(self, query: np.ndarray, top_k: int) -> list[tuple[int, float]]:
        # Sanitize and normalize query
        q = np.nan_to_num(query, nan=0.0, posinf=0.0, neginf=0.0)
        q = np.clip(q, -1e6, 1e6)
        qn = np.linalg.norm(q)
        if qn == 0 or not np.isfinite(qn):
            self.logger.warning("VectorStore: query norm invalid (%.4f); returning empty hits", qn)
            return []
        # Shape validation
        if q.shape[0] != self.embeddings.shape[1]:
            self.logger.warning(
                "VectorStore: query dim %d != embed dim %d; returning empty hits",
                q.shape[0], self.embeddings.shape[1]
            )
            return []
        q = q / qn
        # Cosine similarity via dot product
        sims = self.embeddings @ q
        sims = np.nan_to_num(sims, nan=-1.0, posinf=-1.0, neginf=-1.0)
        # Clamp top_k and use stable argsort for deterministic ordering
        k = max(0, min(int(top_k), sims.shape[0]))
        idxs = np.argsort(-sims, kind='stable')[:k]
        return [(int(i), float(sims[int(i)])) for i in idxs]
