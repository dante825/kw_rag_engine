from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List

from backend.models.schemas import Document, QueryRequest, QueryResponse
from backend.services.document_service import DocumentService
from backend.services.embedding_service import EmbeddingService
from backend.services.rag_service import RAGService

router = APIRouter()

def get_doc_service():
    return DocumentService()

def get_embedding_service():
    return EmbeddingService()

def get_rag_service():
    return RAGService()

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
        doc_id, chunks = doc_service.save_upload(content, file.filename)
        embedding_service.add_chunks(chunks, doc_id)
        
        return Document(
            id=doc_id,
            filename=file.filename,
            upload_date=doc_service.list_documents()[0]["upload_date"],
            chunk_count=len(chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[Document])
async def list_documents(doc_service: DocumentService = Depends(get_doc_service)):
    docs = doc_service.list_documents()
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
    doc_service.delete_document(doc_id)
    embedding_service.delete_by_doc_id(doc_id)
    return {"status": "deleted", "doc_id": doc_id}

@router.post("/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    try:
        result = rag_service.query(request.question, request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
