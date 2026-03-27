import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List

from backend.models.schemas import Document, QueryRequest, QueryResponse
from backend.services.document_service import DocumentService
from backend.services.embedding_service import EmbeddingService
from backend.services.rag_service import RAGService

router = APIRouter()

# Singletons — instantiated once at startup, reused across all requests
_doc_service = DocumentService()
_embedding_service = EmbeddingService()
_rag_service = RAGService()


def get_doc_service():
    return _doc_service


def get_embedding_service():
    return _embedding_service


def get_rag_service():
    return _rag_service


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/documents/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_doc_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    allowed_extensions = {".pdf", ".txt", ".doc", ".docx"}
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()

    try:
        doc_id, chunks = await asyncio.to_thread(doc_service.save_upload, content, file.filename)
        await asyncio.to_thread(embedding_service.add_chunks, chunks, doc_id)

        docs = await asyncio.to_thread(doc_service.list_documents)
        upload_date = next((d["upload_date"] for d in docs if d["id"] == doc_id), "")

        return Document(
            id=doc_id,
            filename=file.filename,
            upload_date=upload_date,
            chunk_count=len(chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[Document])
async def list_documents(doc_service: DocumentService = Depends(get_doc_service)):
    docs = await asyncio.to_thread(doc_service.list_documents)
    return [
        Document(
            id=d["id"],
            filename=d["filename"],
            upload_date=d["upload_date"],
            chunk_count=0
        )
        for d in docs
    ]


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    doc_service: DocumentService = Depends(get_doc_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    await asyncio.to_thread(doc_service.delete_document, doc_id)
    await asyncio.to_thread(embedding_service.delete_by_doc_id, doc_id)
    return {"status": "deleted", "doc_id": doc_id}


@router.post("/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    try:
        result = await asyncio.to_thread(rag_service.query, request.question, request.top_k, request.history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_document_stream(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    return StreamingResponse(
        rag_service.query_stream(request.question, request.top_k, request.history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
