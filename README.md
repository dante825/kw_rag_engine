# RAG Engine - Local Document Q&A System

**Project**: Local RAG System with Ollama  
**Use Case**: Document Q&A  
**Framework**: LangChain  
**Interface**: Web UI (FastAPI + React)

---

## Current Status: ✅ COMPLETED

The core RAG system is implemented and working. Both backend and frontend are running.

### Running Services
| Service | URL | Status |
|---------|-----|--------|
| Backend API | http://localhost:8000 | Running |
| Frontend UI | http://localhost:5173 | Running |
| Ollama | localhost:11434 | Using qwen3.5:9b |

---

## Quick Start

### Prerequisites
- [x] Ollama installed with models pulled
- [x] Python dependencies installed
- [x] Frontend dependencies installed

### Start Backend
```bash
cd /Users/kangwei/development/repo/kw_rag_engine
python -m backend.main
```

### Start Frontend
```bash
cd /Users/kangwei/development/repo/kw_rag_engine/frontend
npm run dev
```

### Access
- Open http://localhost:5173 in browser
- Upload documents (PDF, TXT, DOC, DOCX)
- Ask questions about your documents

---

## Project Structure

```
kw_rag_engine/
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── api/routes.py        # API endpoints
│   ├── core/config.py       # Configuration
│   ├── models/schemas.py   # Pydantic models
│   └── services/
│       ├── document_service.py   # Document loading/chunking
│       ├── embedding_service.py   # ChromaDB + embeddings
│       └── rag_service.py        # RAG chain
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main UI
│   │   ├── services/api.ts  # API client
│   │   └── index.css       # Tailwind styles
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── data/documents/          # Uploaded files
├── vector_store/            # ChromaDB persistence
├── requirements.txt
└── README.md
```

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| LLM | qwen3.5:9b (via Ollama) |
| Embedding | nomic-embed-text |
| Vector DB | ChromaDB |
| Orchestration | LangChain |
| Backend | FastAPI |
| Frontend | React + Vite + TailwindCSS |
| HTTP Client | Axios |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/documents/upload` | Upload document |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{id}` | Delete document |
| POST | `/api/query` | Ask question |

---

## Configuration

Edit `backend/core/config.py` to customize:

```python
ollama_base_url: str = "http://localhost:11434"
llm_model: str = "qwen3.5:9b"
embedding_model: str = "nomic-embed-text"
chunk_size: int = 512
chunk_overlap: int = 50
top_k: int = 4
```

---

## Next Steps (Optional Enhancements)

### High Priority
- [ ] Add streaming responses for real-time LLM output
- [ ] Add chat history for conversation context
- [ ] Add document parsing progress indicator

### Medium Priority
- [ ] Add authentication
- [ ] Add multiple file upload
- [ ] Add search result highlighting

### Low Priority
- [ ] Add support for more file types
- [ ] Add export chat history
- [ ] Add dark mode
- [ ] Add RAG evaluation metrics

---

## Testing the System

```bash
# Health check
curl http://localhost:8000/api/health

# Upload document
curl -X POST -F "file=@data/documents/test.txt" http://localhost:8000/api/documents/upload

# Query
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}' \
  http://localhost:8000/api/query
```

---

## Troubleshooting

### Backend not starting?
- Check if port 8000 is free
- Verify Ollama is running: `ollama list`
- Check Python dependencies: `pip install -r requirements.txt`

### Frontend not loading?
- Check if port 5173 is free
- Run `npm install` in frontend directory

### Query failing?
- Verify Ollama models are pulled: `ollama list`
- Check backend logs for errors
- Ensure documents are uploaded first
