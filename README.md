# RAG Engine - Local Document Q&A System

**Use Case**: Multi-turn conversational Q&A over uploaded documents
**Framework**: LangChain
**Interface**: Web UI (FastAPI + React)

---

## Quick Start

```bash
./start.sh    # start backend + frontend
./stop.sh     # stop both services
./status.sh   # check running status
```

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Ollama | http://localhost:11434 |

---

## Features

- **Upload documents** — PDF, TXT, DOC, DOCX
- **Streaming answers** — LLM response streams token-by-token in real time
- **Multi-turn conversation** — previous Q&A is retained in the session and passed as context so follow-up questions work naturally
- **Document filter** — restrict search to a specific uploaded document using the dropdown in the chat panel
- **Warm sepia UI** — easy-on-the-eyes color scheme with chat bubble layout and collapsible sources

---

## Project Structure

```
kw_rag_engine/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/routes.py              # API endpoints
│   ├── core/config.py             # Configuration (models, top_k, chunk size…)
│   ├── models/schemas.py          # Pydantic request/response models
│   └── services/
│       ├── document_service.py    # File upload, loading, chunking
│       ├── embedding_service.py   # ChromaDB vector store + embeddings
│       └── rag_service.py         # Prompt building + LLM streaming
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main UI (chat, upload, document list)
│   │   ├── services/api.ts        # API client (streaming + history)
│   │   └── index.css              # Tailwind base styles
│   ├── tailwind.config.js         # Custom sepia color palette
│   └── vite.config.ts
├── data/documents/                # Uploaded files (persisted)
├── vector_store/                  # ChromaDB vector store (persisted)
├── start.sh / stop.sh / status.sh
└── requirements.txt
```

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| LLM | qwen3.5:9b (via Ollama) |
| Embeddings | nomic-embed-text (via Ollama) |
| Vector DB | ChromaDB (persistent, cosine similarity) |
| Orchestration | LangChain |
| Backend | FastAPI + Server-Sent Events (streaming) |
| Frontend | React + Vite + TailwindCSS |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/documents/upload` | Upload a document |
| GET | `/api/documents` | List uploaded documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| POST | `/api/query` | Ask a question (non-streaming) |
| POST | `/api/query/stream` | Ask a question (SSE streaming) |

### Query request body

```json
{
  "question": "What is the main topic?",
  "top_k": 8,
  "history": [
    { "question": "previous question", "answer": "previous answer" }
  ],
  "doc_id_filter": "uuid-of-specific-doc-or-null"
}
```

---

## Configuration

Edit `backend/core/config.py`:

```python
llm_model: str = "qwen3.5:9b"
embedding_model: str = "nomic-embed-text"
ollama_base_url: str = "http://localhost:11434"

chunk_size: int = 512        # tokens per chunk
chunk_overlap: int = 50      # overlap between chunks
top_k: int = 8               # chunks retrieved per query
llm_num_ctx: int = 8192      # LLM context window
llm_num_predict: int = 2048  # max tokens to generate
```

---

## Troubleshooting

**Backend not starting?**
- Verify Ollama is running: `ollama list`
- Check Python dependencies: `pip install -r requirements.txt`
- Check port 8000 is free

**Frontend not loading?**
- Run `npm install` in the `frontend/` directory
- Check port 5173 is free

**Document filter returns no results?**
- Documents uploaded before the filename-injection fix may not have the `[Source: filename]` prefix in their chunks. Re-upload them to fix this.

**Query failing or slow?**
- Check backend logs: `tail -f backend.log`
- Ensure the Ollama models are pulled: `ollama pull qwen3.5:9b && ollama pull nomic-embed-text`
