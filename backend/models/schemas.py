from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Document(BaseModel):
    id: str
    filename: str
    upload_date: datetime
    chunk_count: int

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None

class Source(BaseModel):
    chunk_id: str
    content: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
