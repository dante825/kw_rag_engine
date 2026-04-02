import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from backend.core.config import settings

class DocumentService:
    def __init__(self):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,    # measured in characters by len()
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

    def _get_loader(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        elif ext == ".txt":
            return TextLoader(file_path, encoding="utf-8")
        elif ext in [".doc", ".docx"]:
            return Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def load_document(self, file_path: str) -> List[Document]:
        loader = self._get_loader(file_path)
        return loader.load()

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        return self.text_splitter.split_documents(documents)

    def save_upload(self, file_content: bytes, filename: str) -> tuple[str, List[Document]]:
        doc_id = str(uuid.uuid4())
        file_path = settings.data_dir / f"{doc_id}_{filename}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        docs = self.load_document(str(file_path))
        chunks = self.chunk_documents(docs)
        
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"{doc_id}_{i}"
            chunk.metadata["doc_id"] = doc_id
            chunk.metadata["filename"] = filename
        
        return doc_id, chunks

    def list_documents(self) -> List[dict]:
        files = {}
        for f in settings.data_dir.iterdir():
            if f.is_file():
                parts = f.stem.split("_", 1)
                if len(parts) == 2:
                    doc_id, filename = parts
                    if doc_id not in files:
                        files[doc_id] = {"id": doc_id, "filename": filename, "upload_date": datetime.fromtimestamp(f.stat().st_mtime)}
        
        return list(files.values())

    def delete_document(self, doc_id: str) -> bool:
        deleted = False
        for f in settings.data_dir.iterdir():
            if f.stem.startswith(doc_id):
                f.unlink()
                deleted = True
        return deleted
