# RAG System Project Plan

**Project**: Local RAG System with Ollama  
**Use Case**: Document Q&A  
**Framework**: LangChain  
**Interface**: Web UI (FastAPI + React)

---

## Prerequisites

- **Hardware**: 8GB+ RAM (16GB recommended), ~10GB disk space
- **Software**: Python 3.8+, Ollama installed

## Architecture

1. **Ollama** - Local LLM runtime
2. **Embedding Model** - `nomic-embed-text` (or `bge-m3`)
3. **Vector Database** - ChromaDB
4. **Document Processing** - PyPDFLoader for PDFs
5. **Orchestration** - LangChain
6. **Backend** - FastAPI
7. **Frontend** - React

---

## Phase 1: Setup

### 1.1 Install Ollama and pull models

```bash
ollama pull llama3.2        # LLM
ollama pull nomic-embed-text # Embedding
```

### 1.2 Create project structure

```
/rag_engine
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   └── rag_service.py
│   └── models/
│       └── schemas.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
├── data/
│   └── documents/
├── vector_store/
├── requirements.txt
└── README.md
```

### 1.3 Python dependencies

```
langchain
langchain-community
langchain-ollama
chromadb
pypdf
python-docx
fastapi
uvicorn
python-multipart
```

---

## Phase 2: Backend Implementation

### 2.1 Core Configuration (`core/config.py`)

- Ollama host: `http://localhost:11434`
- Default LLM model: `llama3.2`
- Default embedding model: `nomic-embed-text`
- Chunk size: 512
- Chunk overlap: 50
- Top-k results: 4

### 2.2 Data Models (`models/schemas.py`)

- `Document`: id, filename, upload_date, chunk_count
- `DocumentUpload`: filename, content
- `QueryRequest`: question, top_k
- `QueryResponse`: answer, sources

### 2.3 Document Service (`services/document_service.py`)

- `load_pdf(file_path) -> List[Document]`
- `chunk_documents(documents, chunk_size, overlap) -> List[Chunk]`
- `save_document(file) -> Document`
- `list_documents() -> List[Document]`
- `delete_document(doc_id)`

### 2.4 Embedding Service (`services/embedding_service.py`)

- Initialize Ollama embeddings
- `embed_texts(texts) -> embeddings`
- ChromaDB collection management
- `add_to_vector_store(chunks, embeddings, doc_id)`
- `similarity_search(query, top_k) -> results`

### 2.5 RAG Service (`services/rag_service.py`)

- `create_rag_chain()` - LangChain RetrievalQA with Ollama
- `query(question) -> answer + sources`
- Prompt template: Context-aware Q&A

### 2.6 API Routes (`api/routes.py`)

- `POST /documents/upload` - Upload PDF
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document
- `POST /query` - Ask question
- `GET /health` - Health check

---

## Phase 3: Frontend Implementation

### 3.1 React Setup

- Vite + React + TypeScript
- TailwindCSS for styling

### 3.2 Components

- `DocumentUploader` - Drag & drop PDF upload
- `DocumentList` - Display uploaded files
- `ChatInterface` - Message input, response display
- `SourceViewer` - Show retrieved context

### 3.3 API Integration

- Axios for HTTP requests
- Polling for async operations

---

## Phase 4: Configuration & Tuning

- Adjust chunk size based on document types
- Experiment with top-k (3-5 recommended)
- Swap LLM model for quality/speed tradeoffs
- Add chat history for conversation context

---

## Models to Consider

### LLM Models

| Model | Size | Use Case |
|-------|------|----------|
| llama3.2 | 3-7B | Balanced |
| gemma3:4b | 4B | Fast responses |
| mistral | 7B | Better accuracy |

### Embedding Models

| Model | Dim | Notes |
|-------|-----|-------|
| nomic-embed-text | 768 | Good quality |
| bge-m3 | 1024 | Multilingual |
