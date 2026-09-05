from uuid import UUID

from sqlalchemy.orm import Session
from app.db.models import RetrievedChunk
from app.db.models import DocumentChunk
from app.embeddings.providers.sentence_transformer import (
    SentenceTransformerProvider,
)
from app.vectorstore.store import VectorStore


class RetrievalService:

    def __init__(
        self,
        db: Session,
        embedding_service: SentenceTransformerProvider,
        vector_store: VectorStore,
    ):
        self.db = db
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        organization_id: UUID,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        # 1. Convert the user's query into an embedding
        query_vector = self.embedding_service.embed_text(
            query
        )

        # 2. Search Qdrant within the organization
        results = self.vector_store.search(
            vector=query_vector,
            organization_id=organization_id,
            limit=limit,
        )

        if not results:
            return []

        # 3. Extract the chunk IDs returned by Qdrant
        chunk_ids = [
            UUID(result.payload["chunk_id"])
            for result in results
        ]

        # 4. Fetch the authoritative chunk records
        chunks = (
            self.db.query(DocumentChunk)
            .filter(
                DocumentChunk.id.in_(chunk_ids)
            )
            .all()
        )

        # 5. Create a lookup for efficient ordering
        chunks_by_id = {
            chunk.id: chunk
            for chunk in chunks
        }

        # 6. Preserve Qdrant's relevance order
        retrieved_chunks = list[RetrievedChunk]()

        for result in results:
            chunk_id = UUID(
                result.payload["chunk_id"]
            )

            chunk = chunks_by_id.get(chunk_id)

            if chunk is None:
                continue

            retrieved_chunks.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=result.score,
                )
            )

        return retrieved_chunks