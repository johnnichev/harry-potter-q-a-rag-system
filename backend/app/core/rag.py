"""Core orchestration for the RAG pipeline.

Loads the chapter text, builds chunks and embeddings, and wires a simple
in-memory vector store for retrieval. Streaming generation is handled in the
services layer.
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
from ..services.generator import stream_answer  # used by API


class RAGService:
    """Bootstrap chapter data and provide retrieval over an in-memory index."""

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

    def retrieve_hits(self, question: str):
        """Return raw retrieval hits for a question as (chunk, score, index)."""
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
