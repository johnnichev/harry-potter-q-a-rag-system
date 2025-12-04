"""
Adheres to project-instructions.md: core orchestration separated under app/core.
Provides RAGService for retrieval and generation.
"""
import time
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from ..config.config import CHAPTER_PATH, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, EMBED_MODEL
from ..services.loader import load_text
from ..services.chunker import chunk_text
from ..services.embedding import embed_texts, embed_query
from ..services.vectorstore import InMemoryVectorStore
from ..services.retriever import retrieve
from ..services.generator import generate_answer


class RAGService:
    def __init__(self):
        logger = logging.getLogger("rag")
        t0 = time.time()
        logger.info("RAG: loading chapter text from %s", CHAPTER_PATH)
        self.text = load_text(Path(CHAPTER_PATH))
        logger.info("RAG: text loaded (%d chars)", len(self.text))
        logger.info("RAG: chunking text (size=%d overlap=%d)", CHUNK_SIZE, CHUNK_OVERLAP)
        self.chunks = chunk_text(self.text, CHUNK_SIZE, CHUNK_OVERLAP)
        logger.info("RAG: produced %d chunks", len(self.chunks))
        logger.info("RAG: embedding %d chunks with '%s'", len(self.chunks), EMBED_MODEL)
        t1 = time.time()
        self.embeddings = embed_texts(self.chunks)
        t2 = time.time()
        logger.info("RAG: embeddings ready (%.2fs)", t2 - t1)
        self.store = InMemoryVectorStore(self.embeddings, self.chunks)
        logger.info("RAG: vector store initialized")
        logger.info("RAG: startup completed (%.2fs total)", t2 - t0)
        self._answer_cache: dict[str, dict] = {}

    def ask(self, question: str) -> str:
        logger = logging.getLogger("rag")
        if not question.strip():
            return ""
        if question in self._answer_cache:
            return self._answer_cache[question]["answer"]
        t0 = time.time()
        logger.info("RAG: /ask start: '%s'", question)
        qv = embed_query(question)
        hits = retrieve(self.store, qv, TOP_K)
        contexts = [h[0] for h in hits]
        logger.info(
            "RAG: retrieved %d hits: %s",
            len(hits),
            ", ".join([f"{i}:{s:.3f}" for _, s, i in hits]) if hits else "none",
        )
        t1 = time.time()
        ans = generate_answer(question, contexts)
        t2 = time.time()
        logger.info("RAG: generation done (retrieve=%.2fs, generate=%.2fs)", t1 - t0, t2 - t1)
        self._answer_cache[question] = {"answer": ans, "hits": hits}
        return ans

    def ask_meta(self, question: str):
        logger = logging.getLogger("rag")
        logger.info("RAG: /ask_meta start: '%s'", question)
        record = self._answer_cache.get(question)
        if record is None:
            qv = embed_query(question)
            hits = retrieve(self.store, qv, TOP_K)
            contexts = [h[0] for h in hits]
            ans = generate_answer(question, contexts)
            record = {"answer": ans, "hits": hits}
            self._answer_cache[question] = record
        ans = record["answer"]
        hits = record["hits"]
        logger.info(
            "RAG: /ask_meta retrieved %d hits: %s",
            len(hits),
            ", ".join([f"{i}:{s:.3f}" for _, s, i in hits]) if hits else "none",
        )
        return {"answer": ans, "sources": [{"chunk": c, "score": float(s), "index": int(i)} for c, s, i in hits]}

    def retrieve_hits(self, question: str):
        logger = logging.getLogger("rag")
        logger.info("RAG: retrieve_hits for '%s'", question)
        qv = embed_query(question)
        hits = retrieve(self.store, qv, TOP_K)
        logger.info(
            "RAG: retrieved %d hits: %s",
            len(hits),
            ", ".join([f"{i}:{s:.3f}" for _, s, i in hits]) if hits else "none",
        )
        return hits
