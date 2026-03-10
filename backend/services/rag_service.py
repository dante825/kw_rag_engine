from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough

from backend.core.config import settings
from backend.services.embedding_service import EmbeddingService
from backend.models.schemas import QueryResponse, Source

class RAGService:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.7,
        )
        self.embedding_service = EmbeddingService()
        
        self.prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def query(self, question: str, top_k: int = None) -> QueryResponse:
        top_k = top_k or settings.top_k
        
        results = self.embedding_service.similarity_search(question, top_k)
        
        if not results:
            return QueryResponse(
                answer="No documents found. Please upload some documents first.",
                sources=[]
            )
        
        context = "\n\n".join([doc.page_content for doc, _ in results])
        
        chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
        )
        
        response = chain.invoke(question)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        sources = [
            Source(
                chunk_id=doc.metadata.get("chunk_id", "unknown"),
                content=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                score=score
            )
            for doc, score in results
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources
        )
