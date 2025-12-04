# Harry Potter Chapter 1 RAG Q&A

## Overview

- Full-stack app: `FastAPI` backend + `React` frontend.
- Answers questions strictly from `harry-potter-the-philosophers-stone-chapter-1.txt`.
- Uses local `Ollama` for embeddings and generation.

## Architecture

- Backend: RAG pipeline with modules for loading, chunking, embedding, vector search, retrieval, and generation.
- Frontend: Single page with question input, submit button, answer area, optional sources toggle.
- Endpoints: `GET /health`, `POST /ask` (unified; streaming + sources supported), `POST /ask_meta` (alias).

## Prerequisites

- macOS (Apple Silicon recommended for speed) or Linux/WSL2
- Python 3.9+ (virtualenv recommended)
- Node.js 18+ (for Vite + React dev server)
- Ollama installed and running locally
  - Install: `curl -fsSL https://ollama.com/install.sh | sh` or simply `brew install ollama`
  - Start daemon: `ollama serve`
  - Pull models (chosen defaults):
    - Embedding: `ollama pull all-minilm` (Ollama name for all-MiniLM-L6-v2)
    - Generation: `ollama pull llama3.1:8b`
  - Verify: `curl http://localhost:11434` returns a JSON banner

## Backend Setup (FastAPI)

1. Create and activate a Python virtualenv
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies
   - `pip install -r backend/requirements.txt`
3. Ensure Ollama is running and models are pulled (see prerequisites)
4. Start the server from the repository root (new entrypoint)
   - `uvicorn backend.app.api.main:app --reload --port 8000`
5. Configuration via environment variables (optional)
   - `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`)
   - `EMBED_MODEL` (default `nomic-embed-text`)
   - `LLM_MODEL` (default `llama3.1:8b`)
   - `CHUNK_SIZE` (default `500`), `CHUNK_OVERLAP` (default `50`), `TOP_K` (default `4`)
6. Health check
   - `curl http://localhost:8000/health`
   - Returns diagnostics JSON (status, models, chunk count). If not ready, ensure Ollama is running and models are pulled.

## Frontend Setup (React + Vite)

1. `cd frontend && npm install`
2. Start dev server: `npm run dev`
3. Open http://localhost:5173/
4. Configure API base URL via `VITE_API_BASE_URL` in your env (optional; defaults to `http://localhost:8000`)
5. UI/UX
   - Polished design with accessible labels and responsive layout
   - Use the "Show sources" toggle to view retrieved chunks and similarity scores

## Usage

- Open `http://localhost:5173/`
- Single-chat interface streams answers into a chat thread
- Toggle `Show sources` to reveal citations under assistant messages
- The backend answers strictly from `harry-potter-the-philosophers-stone-chapter-1.txt`

## Testing

- Backend unit tests: `pytest -q` from repository root
- Manual API checks:
  - Health: `curl http://localhost:8000/health`
  - /ask non-stream plain: `curl -s -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{"question":"Where do the Dursleys live?","stream":false,"include_sources":false,"format":"text"}'`
  - /ask non-stream JSON: `curl -s -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{"question":"Where do the Dursleys live?","stream":false,"include_sources":true,"format":"json"}'`
  - /ask stream SSE: `curl -N -H 'Accept: text/event-stream' -H 'Content-Type: application/json' -d '{"question":"Where do the Dursleys live?","stream":true,"include_sources":true,"format":"json"}' http://localhost:8000/ask`
  - Embeddings test (Ollama): `curl -s http://localhost:11434/api/embeddings -d '{"model":"all-minilm","prompt":"test"}'`
  - Generation test (Ollama): `curl -s http://localhost:11434/api/generate -d '{"model":"llama3.1:8b","prompt":"hello"}'`
- Benchmark: `python backend/scripts/benchmark.py`

## Implementation Notes

- Frontend now uses a single conversation thread stored in localStorage (`hp_chat_messages`).
- Single consistent design with accessible contrast; no theme toggles.
- Input clears and refocuses on send for fast follow-ups.
- A loading indicator appears before first tokens with subtle animation.

- Text is chunked with overlap to balance recall and latency.
- Embeddings and vector index are precomputed at startup and kept in memory.
- `/ask` returns the final answer as a plain string per requirement.

### Model Choice (Why these defaults)

- Embeddings: `all-minilm` balances retrieval quality and speed on local CPUs, and is widely used for sentence embeddings.
- Generation: `llama3.1:8b` improves response quality and reasoning over 7B family models while remaining feasible locally. Expect slightly higher memory and latency than 7B, with better answer fidelity for nuanced questions.
- You can override via env: `EMBED_MODEL` and `LLM_MODEL`.

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

## Project Structure (updated)

```
backend/
  app/
    api/
      main.py          # FastAPI app and endpoints (only entrypoint)
    core/
      rag.py           # Orchestration service
      schemas.py       # Pydantic models
    config/
      config.py        # Environment-backed configuration
    services/          # Loader, chunker, embedding, vectorstore, retriever, generator, preflight
    utils/
      logger.py        # Logging setup
  requirements.txt
  tests/               # Unit tests (pytest)
  scripts/benchmark.py # Latency benchmark
frontend/
  src/
    app/App.tsx        # Root app component
    features/chat/
      components/      # AskForm, Answer
      __tests__/       # feature tests
    lib/
      api/client.ts    # API client
      types.ts         # Shared types
    styles/styles.css  # App styles
    vite-env.d.ts      # Vite type references
  package.json, tsconfig.json, vite.config.ts, index.html
README.md
harry-potter-the-philosophers-stone-chapter-1.txt
```
