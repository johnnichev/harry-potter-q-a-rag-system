import numpy as np
from backend.app.services.vectorstore import InMemoryVectorStore


def test_vectorstore_similarity():
    chunks = ["a", "b", "c"]
    vecs = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    store = InMemoryVectorStore(vecs, chunks)
    q = np.array([1.0, 0.0], dtype=np.float32)
    hits = store.similar(q, 2)
    assert len(hits) == 2
    assert hits[0][0] == 0

