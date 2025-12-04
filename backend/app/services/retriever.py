"""Retrieval helpers.

Maps nearest vector indices back to chunk strings with their scores.
"""

from .vectorstore import InMemoryVectorStore


def retrieve(store: InMemoryVectorStore, query_vec, top_k: int):
    """Return (chunk, score, index) tuples for the top-k similarities."""
    hits = store.similar(query_vec, top_k)
    return [(store.chunks[i], s, i) for i, s in hits]
