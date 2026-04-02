import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from typing import List, Tuple

from backend.core.config import settings

class EmbeddingService:
    def __init__(self):
        settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        self.embeddings = OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url,
        )
        
        self.client = chromadb.PersistentClient(
            path=str(settings.vector_store_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Document], doc_id: str):
        if not chunks:
            return
        
        ids = [chunk.metadata.get("chunk_id", f"{doc_id}_{i}") for i, chunk in enumerate(chunks)]
        texts = [chunk.page_content for i, chunk in enumerate(chunks)]
        embeddings = self.embeddings.embed_documents(texts)
        metadatas = [chunk.metadata for chunk in chunks]
        
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def similarity_search(self, query: str, top_k: int = None, doc_id_filter: str = None) -> List[Tuple[Document, float]]:
        top_k = top_k or settings.top_k

        query_embedding = self.embeddings.embed_query(query)
        where = {"doc_id": doc_id_filter} if doc_id_filter else None
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )
        
        docs_with_scores = []
        if results["documents"] and results["documents"][0]:
            for i, (doc_text, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                doc = Document(
                    page_content=doc_text,
                    metadata=metadata
                )
                score = 1 - distance
                if score >= settings.min_relevance_score:
                    docs_with_scores.append((doc, score))
        
        return docs_with_scores

    def delete_by_doc_id(self, doc_id: str):
        all_ids = self.collection.get()["ids"]
        ids_to_delete = [id for id in all_ids if id.startswith(doc_id)]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

    def get_chunk_count(self) -> int:
        return self.collection.count()
