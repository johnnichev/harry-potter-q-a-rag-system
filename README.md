# Harry Potter Chapter 1 RAG Q&A

## Overview

- Full-stack app: `FastAPI` backend + `React` frontend.
- Answers questions strictly from `harry-potter-the-philosophers-stone-chapter-1.txt`.
- Uses local `Ollama` for embeddings and generation.

## Architecture

- Backend: RAG pipeline with modules for loading, chunking, embedding, vector search, retrieval, and generation.
- Frontend: Single page with question input, submit button, answer area, optional sources toggle.
- Endpoints: `GET /health`, `POST /ask` (returns plain text), `POST /ask_meta`, `POST /ask_stream` (optional).

## Prerequisites

- macOS (Apple Silicon recommended for speed) or Linux/WSL2
- Python 3.9+ (virtualenv recommended)
- Node.js 18+ (for Vite + React dev server)
- Ollama installed and running locally
  - Install: `curl -fsSL https://ollama.com/install.sh | sh` (or use the macOS app)
  - Start daemon: `ollama serve`
  - Pull models:
    - `ollama pull nomic-embed-text`
    - `ollama pull llama3.1:8b` (or `llama2:7b`)
  - Verify: `curl http://localhost:11434` returns a JSON banner

## Backend Setup (FastAPI)

1. Create and activate a Python virtualenv
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies
   - `pip install -r backend/requirements.txt`
3. Ensure Ollama is running and models are pulled (see prerequisites)
4. Start the server from the repository root
   - `uvicorn backend.app.main:app --reload --port 8000`
5. Configuration via environment variables (optional)
   - `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`)
   - `EMBED_MODEL` (default `nomic-embed-text`)
   - `LLM_MODEL` (default `llama3.1:8b`)
   - `CHUNK_SIZE` (default `500`), `CHUNK_OVERLAP` (default `50`), `TOP_K` (default `4`)
6. Health check
   - `curl http://localhost:8000/health`
   - Returns `{"status":"ok"}` when ready; `503 Service not ready` if Ollama/models are unavailable

## Frontend Setup (React + Vite + Material UI)

1. `cd frontend && npm install`
2. Start dev server: `npm run dev`
3. Open http://localhost:5173/
4. Configure API base URL via `VITE_API_BASE_URL` in your env (optional; defaults to `http://localhost:8000`)
5. UI/UX
   - Polished Material UI design with accessible labels and responsive layout
   - Toggle "Show sources" to view retrieved chunks and similarity scores

## Usage

- Open the frontend at `http://localhost:5173/`
- Enter a question based on Chapter 1 and click `Ask Chapter`
- Optional: toggle `Show sources` to inspect the retrieved context
- The backend answers strictly from `harry-potter-the-philosophers-stone-chapter-1.txt`

## Testing

- Backend unit tests: `pytest -q` from repository root
- Manual API checks:
  - Health: `curl http://localhost:8000/health`
  - Ask: `curl -s -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{"question": "Where do the Dursleys live?"}'`
- Benchmark: `python backend/scripts/benchmark.py`

## Implementation Notes

- Text is chunked with overlap to balance recall and latency.
- Embeddings and vector index are precomputed at startup and kept in memory.
- `/ask` returns the final answer as a plain string per requirement.

## Optional Enhancements

- Citations endpoint `POST /ask_meta` exposing source chunks and scores
- Streamed responses `POST /ask_stream` for improved perceived latency
- Frontend `Show sources` toggle to inspect retrieved context
- In-memory query cache to accelerate repeated questions
- Preflight model checks with graceful readiness reporting
- Benchmark script `backend/scripts/benchmark.py` for local latency measurement

### Justification

- Citations increase trust and explain model answers without altering the core flow.
- Streaming reduces time-to-first-token and improves UX while keeping `/ask` unchanged.
- Query cache avoids repeated embedding/generation work for identical questions.
- Preflight offers clear operational signals when Ollama or models are unavailable.
- Benchmarking aids performance tuning and reporting.

## Troubleshooting

- Ollama not running: start it and ensure `OLLAMA_BASE_URL` is reachable
- Missing models: run the `ollama pull` commands above
- Health is 503: ensure preflight can embed & generate; pull models and restart
- CORS errors: default frontend origin `http://localhost:5173` is allowed
- Port conflicts: change frontend dev port or backend `--port`
- Node version issues: use Node 18+ for Vite 5
- Python dependency issues: upgrade pip (`python -m pip install --upgrade pip`)

## Submission

- This repository contains both backend and frontend
- Follow setup above; confirm unit tests pass and manual queries work

## Project Structure

```
backend/
  app/
    main.py            # FastAPI app and endpoints
    config.py          # Environment-backed configuration
    rag.py             # Orchestration service
    schemas.py         # Pydantic models
    services/          # Loader, chunker, embedding, vectorstore, retriever, generator, preflight
  requirements.txt
  tests/               # Unit tests (pytest)
  scripts/benchmark.py # Latency benchmark
frontend/
  src/
    App.tsx           # Main page
    components/       # AskForm, Answer (Material UI)
    api/client.ts     # API calls to backend
  package.json, tsconfig.json, vite.config.ts, index.html
README.md
harry-potter-the-philosophers-stone-chapter-1.txt
```
