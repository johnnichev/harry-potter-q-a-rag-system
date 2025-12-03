import time
from pathlib import Path
from typing import Optional

import numpy as np

from .config import CHAPTER_PATH, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K
from .services.loader import load_text
from .services.chunker import chunk_text
from .services.embedding import embed_texts, embed_query
from .services.vectorstore import InMemoryVectorStore
from .services.retriever import retrieve
from .services.generator import generate_answer


class RAGService:
    def __init__(self):
        self.text = load_text(Path(CHAPTER_PATH))
        self.chunks = chunk_text(self.text, CHUNK_SIZE, CHUNK_OVERLAP)
        self.embeddings = embed_texts(self.chunks)
        self.store = InMemoryVectorStore(self.embeddings, self.chunks)
        self._answer_cache: dict[str, str] = {}

    def ask(self, question: str) -> str:
        if not question.strip():
            return ""
        if question in self._answer_cache:
            return self._answer_cache[question]
        qv = embed_query(question)
        hits = retrieve(self.store, qv, TOP_K)
        contexts = [h[0] for h in hits]
        ans = generate_answer(question, contexts)
        self._answer_cache[question] = ans
        return ans

    def ask_meta(self, question: str):
        qv = embed_query(question)
        hits = retrieve(self.store, qv, TOP_K)
        contexts = [h[0] for h in hits]
        ans = generate_answer(question, contexts)
        return {"answer": ans, "sources": [{"chunk": c, "score": float(s), "index": int(i)} for c, s, i in hits]}
