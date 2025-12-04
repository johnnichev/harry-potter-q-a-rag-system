import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from .config import CORS_ORIGINS
from .schemas import AskRequest
from .rag import RAGService
from .services.generator import stream_answer
from .services.preflight import check_models
from .utils.logger import setup_logging

logger = setup_logging()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional
rag_service: Optional[RAGService] = None


@app.on_event("startup")
def startup_event():
    global rag_service
    try:
        logger.info("Startup: beginning service initialization")
        if not check_models():
            logger.error("Startup: preflight failed; RAG service will not start")
            rag_service = None
            return
        logger.info("Startup: building RAGService (loading text, chunking, embedding)")
        rag_service = RAGService()
        logger.info("Startup: RAGService ready")
    except Exception as e:
        logger.exception("Startup: exception during initialization: %s", e)
        raise e


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
        stream = True if req.stream is None else bool(req.stream)
        include_sources = True if req.include_sources is None else bool(req.include_sources)
        fmt = req.format or ("json" if stream else "text")

        if stream:
            # Fast path: retrieve hits only; do NOT pre-generate full answer
            hits = rag_service.retrieve_hits(req.question)
            sources = [
                {"index": int(i), "score": float(s), "chunk": c if include_sources else None}
                for c, s, i in hits
            ]
            def sse():
                # Start event with sources
                start_payload = {"sources": sources}
                yield f"event: start\ndata: {json.dumps(start_payload)}\n\n"
                # Now stream tokens
                contexts = [c for c, _, _ in hits]
                final = []
                for token in stream_answer(req.question, contexts):
                    final.append(token)
                    yield f"event: token\ndata: {json.dumps(token)}\n\n"
                # Cache final answer with hits
                answer = ("".join(final)).strip()
                rag_service._answer_cache[req.question] = {"answer": answer, "hits": hits}
                end_payload = {"answer": answer}
                yield f"event: end\ndata: {json.dumps(end_payload)}\n\n"
            return StreamingResponse(sse(), media_type="text/event-stream")
        else:
            # Non-stream: reuse cache when available, else compute
            record = rag_service._answer_cache.get(req.question)
            if record is None:
                meta = rag_service.ask_meta(req.question)
                record = {"answer": meta["answer"], "hits": [(s["chunk"], s["score"], s["index"]) for s in meta["sources"]]}
                rag_service._answer_cache[req.question] = record
            sources = [
                {"index": int(i), "score": float(s), "chunk": c if include_sources else None}
                for c, s, i in record["hits"]
            ]
            if fmt == "json":
                return {"answer": record["answer"], "sources": sources}
            return PlainTextResponse(record["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask_meta")
def ask_meta(req: AskRequest):
    logger = logging.getLogger("rag")
    logger.info("HTTP /ask_meta received: %s", (req.question or "").strip())
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    if not req.question:
        raise HTTPException(status_code=400, detail="Question required")
    try:
        # Alias to unified logic: return non-stream JSON with sources
        meta = rag_service.ask_meta(req.question)
        logger.info("HTTP /ask_meta completed: sources=%d", len(meta.get("sources", [])))
        return meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask_stream")
def ask_stream(req: AskRequest):
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    if not req.question:
        raise HTTPException(status_code=400, detail="Question required")
    q = req.question
    def gen():
        ans_meta = rag_service.ask_meta(q)
        contexts = [s["chunk"] for s in ans_meta["sources"]]
        for token in stream_answer(q, contexts):
            yield token
    return StreamingResponse(gen(), media_type="text/plain")
