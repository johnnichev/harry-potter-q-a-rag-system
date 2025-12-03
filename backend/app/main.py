import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from .config import CORS_ORIGINS
from .schemas import AskRequest
from .rag import RAGService
from .services.generator import stream_answer
from .services.preflight import check_models

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
        if not check_models():
            rag_service = None
            return
        rag_service = RAGService()
    except Exception as e:
        raise e


@app.get("/health")
def health():
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ok"}


@app.post("/ask", response_class=PlainTextResponse)
def ask(req: AskRequest):
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    if not req.question:
        raise HTTPException(status_code=400, detail="Question required")
    try:
        return rag_service.ask(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask_meta")
def ask_meta(req: AskRequest):
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    if not req.question:
        raise HTTPException(status_code=400, detail="Question required")
    try:
        return rag_service.ask_meta(req.question)
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
