from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


class RAGQueryRequest(BaseModel):
    question: str


@dataclass
class Source:
    document_id: UUID
    document_name: str
    page_number: int
    score: float


@dataclass
class RAGResponse:
    answer: str
    sources: list[Source]