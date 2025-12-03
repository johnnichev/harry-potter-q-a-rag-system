from .vectorstore import InMemoryVectorStore


def retrieve(store: InMemoryVectorStore, query_vec, top_k: int):
    hits = store.similar(query_vec, top_k)
    return [(store.chunks[i], s, i) for i, s in hits]
