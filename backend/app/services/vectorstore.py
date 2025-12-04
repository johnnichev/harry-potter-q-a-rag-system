import logging
import numpy as np


class InMemoryVectorStore:
    """Small in-memory vector index with cosine similarity.

    Embeddings are sanitized and L2-normalized at construction time to make
    similarity stable and to avoid NaN/Inf issues propagating through math.
    """

    def __init__(self, embeddings: np.ndarray, chunks: list[str]):
        self.logger = logging.getLogger("rag")
        # Sanitize embeddings to avoid NaN/Inf issues and clamp extremes
        clean = np.nan_to_num(embeddings, nan=0.0, posinf=0.0, neginf=0.0)
        clean = np.clip(clean, -1e6, 1e6)
        self.embeddings = self._normalize(np.ascontiguousarray(clean, dtype=np.float32))
        self.chunks = chunks

    def _normalize(self, m: np.ndarray) -> np.ndarray:
        """Row-wise L2 normalization; protect against zero-norm rows."""
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return m / norms

    def similar(self, query: np.ndarray, top_k: int) -> list[tuple[int, float]]:
        """Return the top-k most similar chunk indices and scores.

        Steps:
        1) Sanitize inputs (replace NaN/Inf, clamp extremes)
        2) Validate query dimensionality against embedding dimension
        3) L2-normalize the query to turn dot product into cosine similarity
        4) Compute similarities and pick top-k with stable ordering
        """

        # 1) Sanitize query values to avoid invalid math downstream
        queryVector = np.nan_to_num(query, nan=0.0, posinf=0.0, neginf=0.0)
        queryVector = np.clip(queryVector, -1e6, 1e6)

        # Compute norm and early-exit on invalid vectors
        queryNorm = np.linalg.norm(queryVector)
        if queryNorm == 0 or not np.isfinite(queryNorm):
            self.logger.warning(
                "VectorStore: query norm invalid (%.4f); returning empty hits",
                queryNorm,
            )
            return []

        # 2) Ensure query dimension matches embedding dimension
        if queryVector.shape[0] != self.embeddings.shape[1]:
            self.logger.warning(
                "VectorStore: query dim %d != embed dim %d; returning empty hits",
                queryVector.shape[0],
                self.embeddings.shape[1],
            )
            return []

        # 3) Normalize to unit length so dot-product yields cosine similarity
        queryVector = queryVector / queryNorm

        # 4) Dot product over unit vectors = cosine similarity
        similarities = self.embeddings @ queryVector
        similarities = np.nan_to_num(similarities, nan=-1.0, posinf=-1.0, neginf=-1.0)

        # Select top-k indices; clamp bounds and ensure deterministic ordering
        topK = max(0, min(int(top_k), similarities.shape[0]))
        topIndices = np.argsort(-similarities, kind="stable")[:topK]

        # Return (index, score) pairs as ints/floats for downstream usage
        return [(int(i), float(similarities[int(i)])) for i in topIndices]
