import asyncio
import json
import logging
import time
from typing import AsyncGenerator

import ollama

from backend.core.config import settings
from backend.services.embedding_service import EmbeddingService
from backend.models.schemas import QueryResponse, Source

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.async_client = ollama.AsyncClient(host=settings.ollama_base_url)
        self.sync_client = ollama.Client(host=settings.ollama_base_url)
        self.embedding_service = EmbeddingService()

    def _build_prompt(self, question: str, context: str, history: list = None) -> str:
        history_block = ""
        if history:
            lines = []
            for turn in history:
                lines.append(f"Human: {turn.question}")
                lines.append(f"Assistant: {turn.answer}")
            history_block = "\nConversation history:\n" + "\n".join(lines) + "\n"

        return f"""/no_think
Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, say so clearly.

Context:
{context}
{history_block}
Question: {question}

Answer:"""

    def _ollama_options(self) -> dict:
        return {
            "num_predict": settings.llm_num_predict,
            "num_ctx": settings.llm_num_ctx,
            "temperature": settings.llm_temperature,
        }

    def query(self, question: str, top_k: int = None, history: list = None, doc_id_filter: str = None) -> QueryResponse:
        top_k = top_k or settings.top_k

        results = self.embedding_service.similarity_search(question, top_k, doc_id_filter)

        if not results:
            return QueryResponse(
                answer="No documents found. Please upload some documents first.",
                sources=[]
            )

        context = "\n\n".join(
            f"[Source: {doc.metadata.get('filename', 'unknown')}]\n{doc.page_content}"
            for doc, _ in results
        )
        prompt = self._build_prompt(question, context, history)

        response = self.sync_client.chat(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            think=False,
            options=self._ollama_options(),
        )
        answer = response["message"]["content"]

        sources = [
            Source(
                chunk_id=doc.metadata.get("chunk_id", "unknown"),
                content=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                score=score,
            )
            for doc, score in results
        ]

        return QueryResponse(answer=answer, sources=sources)

    async def query_stream(self, question: str, top_k: int = None, history: list = None, doc_id_filter: str = None) -> AsyncGenerator[str, None]:
        top_k = top_k or settings.top_k
        t0 = time.monotonic()

        logger.info("Query received: %r", question)
        logger.info("Step 1/2: Running similarity search (top_k=%d)...", top_k)

        results = await asyncio.to_thread(
            self.embedding_service.similarity_search, question, top_k, doc_id_filter
        )

        logger.info("Step 1/2 done: found %d chunks (%.2fs)", len(results), time.monotonic() - t0)

        if not results:
            yield f"data: {json.dumps({'type': 'token', 'content': 'No documents found. Please upload some documents first.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        context = "\n\n".join(
            f"[Source: {doc.metadata.get('filename', 'unknown')}]\n{doc.page_content}"
            for doc, _ in results
        )
        prompt = self._build_prompt(question, context, history)

        sources = [
            {
                "chunk_id": doc.metadata.get("chunk_id", "unknown"),
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "score": score,
            }
            for doc, score in results
        ]

        logger.info("Step 2/2: Sending prompt to LLM (%s), streaming response...", settings.llm_model)
        t1 = time.monotonic()
        token_count = 0
        in_think_block = False
        pending = ""

        response = await self.async_client.chat(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            think=False,
            options=self._ollama_options(),
        )

        async for part in response:
            content = part["message"]["content"]
            if not content:
                continue

            pending += content

            # Strip any <think>...</think> blocks as a safety net
            while pending:
                if in_think_block:
                    end = pending.find("</think>")
                    if end == -1:
                        pending = ""
                        break
                    pending = pending[end + len("</think>"):]
                    in_think_block = False
                else:
                    start = pending.find("<think>")
                    if start == -1:
                        token_count += 1
                        if token_count == 1:
                            logger.info("First token received (%.2fs after LLM call)", time.monotonic() - t1)
                        yield f"data: {json.dumps({'type': 'token', 'content': pending})}\n\n"
                        pending = ""
                        break
                    before = pending[:start]
                    if before:
                        token_count += 1
                        if token_count == 1:
                            logger.info("First token received (%.2fs after LLM call)", time.monotonic() - t1)
                        yield f"data: {json.dumps({'type': 'token', 'content': before})}\n\n"
                    pending = pending[start + len("<think>"):]
                    in_think_block = True

        if pending and not in_think_block:
            yield f"data: {json.dumps({'type': 'token', 'content': pending})}\n\n"

        logger.info("Step 2/2 done: %d tokens in %.2fs (total %.2fs)",
                    token_count, time.monotonic() - t1, time.monotonic() - t0)

        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
