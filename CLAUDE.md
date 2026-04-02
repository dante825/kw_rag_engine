# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A full-stack document Q&A system (RAG engine) with:
- **Backend**: Python FastAPI + LangChain + ChromaDB + Ollama (local LLM inference)
- **Frontend**: React + TypeScript + Vite + TailwindCSS (sepia theme)
- **LLMs**: `qwen3.5:9b` for generation, `nomic-embed-text` for embeddings (both via local Ollama)

## Commands

### Start / Stop Services
```bash
./start.sh    # starts backend (port 8000) and frontend (port 5173)
./stop.sh     # stops both services
./status.sh   # check running status
```

### Backend (FastAPI)
```bash
# Run directly (from repo root)
PYTHONPATH=. /Users/kangwei/opt/anaconda3/envs/data_protector/bin/python -m backend.main

# Install dependencies
pip install -r requirements.txt
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev      # dev server on port 5173
npm run build    # TypeScript + Vite production build
npm run lint     # ESLint
npm run preview  # preview production build
```

## Architecture

### Request Flow (Query)
1. React UI → `POST /api/query/stream` (with question, conversation history, optional `doc_id_filter`)
2. `RAGService` embeds the question → ChromaDB similarity search → top-k chunks
3. Context + history injected into system prompt → Ollama LLM (`qwen3.5:9b`)
4. Response streamed back via SSE; `<think>` tokens stripped before forwarding
5. Source document list sent as final SSE event

### Service Layer (`backend/services/`)
- **`document_service.py`**: File I/O (PDF, TXT, DOC, DOCX), text chunking (512 tokens, 50 overlap), persists to `data/documents/`
- **`embedding_service.py`**: ChromaDB wrapper + Ollama embeddings (`nomic-embed-text`), cosine similarity search
- **`rag_service.py`**: Orchestrates retrieval → prompt building → LLM streaming; injects `[Source: filename]` into chunks

All three services are singletons instantiated at startup and injected via FastAPI's dependency system.

### API Routes (`backend/api/routes.py`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/documents/upload` | Upload file (multipart) |
| GET | `/documents` | List indexed documents |
| DELETE | `/documents/{id}` | Delete document + its vectors |
| POST | `/query` | Non-streaming query |
| POST | `/query/stream` | SSE streaming query |

### Frontend (`frontend/src/`)
- `App.tsx` — main chat UI with message history, document upload panel, document filter dropdown
- `services/api.ts` — Axios + `EventSource` client; `/api` prefix proxied to `http://localhost:8000` by Vite

### Configuration (`backend/core/config.py`)
Key defaults (overridable via `.env`):
```
llm_model = "qwen3.5:9b"
embedding_model = "nomic-embed-text"
llm_num_ctx = 8192
top_k = 8                  # chunks retrieved per query
chunk_size = 512
chunk_overlap = 50
ollama_base_url = "http://localhost:11434"
```

### Persistence
- `backend/data/documents/` — raw uploaded files (symlinked from repo root `data/documents/`)
- `backend/vector_store/` — ChromaDB on-disk store (symlinked from repo root `vector_store/`)

## Key Implementation Details

- Blocking I/O in services is wrapped with `asyncio.to_thread()` to avoid blocking the event loop
- Streaming uses FastAPI `StreamingResponse` with `text/event-stream` content type
- The frontend uses `EventSource` (not `fetch`) for SSE; sources arrive as the last SSE event
- The sepia color palette is defined in `frontend/tailwind.config.js` as custom Tailwind colors (`sepia-50` through `sepia-900`)
- `start.sh` uses a hardcoded Anaconda env path — update if the Python environment changes
