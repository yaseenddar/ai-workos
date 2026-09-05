from dataclasses import dataclass

from app.db.models import DocumentChunk


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    score: float