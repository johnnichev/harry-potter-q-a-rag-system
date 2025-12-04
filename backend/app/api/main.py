"""
Adheres to project-instructions.md: minimal API, clear module boundaries.
This entrypoint is organized under app/api with core and services separated.
"""
import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from ..config.config import CORS_ORIGINS
from ..core.schemas import AskRequest
from ..core.rag import RAGService
from ..services.generator import stream_answer
from ..services.preflight import check_models
from ..utils.logger import setup_logging

logger = setup_logging()

from typing import Optional
rag_service: Optional[RAGService] = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag_service
    try:
        logger.info("Startup: beginning service initialization")
        if not check_models():
            logger.error("Startup: preflight failed; RAG service will not start")
            rag_service = None
        else:
            logger.info("Startup: building RAGService (loading text, chunking, embedding)")
            rag_service = RAGService()
            logger.info("Startup: RAGService ready")
        yield
    except Exception as e:
        logger.exception("Startup: exception during initialization: %s", e)
        raise e


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    if rag_service is None:
        return {
            "status": "not_ready",
            "message": "Service not ready",
        }
    return {
        "status": "ok",
        "embed_model": os.getenv("EMBED_MODEL", "nomic-embed-text"),
        "llm_model": os.getenv("LLM_MODEL", "llama3.1:8b"),
        "chunks": len(rag_service.chunks),
    }


@app.post("/ask")
def ask(req: AskRequest):
    logger = logging.getLogger("rag")
    logger.info("HTTP /ask received: %s", (req.question or "").strip())
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    if not req.question:
        raise HTTPException(status_code=400, detail="Question required")
    try:
        hits = rag_service.retrieve_hits(req.question)
        sources = [
            {"index": int(i), "score": float(s), "chunk": c}
            for c, s, i in hits
        ]
        def sse():
            start_payload = {"sources": sources}
            yield f"event: start\ndata: {json.dumps(start_payload)}\n\n"
            contexts = [c for c, _, _ in hits]
            final = []
            for token in stream_answer(req.question, contexts):
                final.append(token)
                yield f"event: token\ndata: {json.dumps(token)}\n\n"
            answer = ("".join(final)).strip()
            rag_service._answer_cache[req.question] = {"answer": answer, "hits": hits}
            end_payload = {"answer": answer}
            yield f"event: end\ndata: {json.dumps(end_payload)}\n\n"
        return StreamingResponse(sse(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


 
