from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.db.models import Document, DocumentChunk
from app.retrieval.models.retrieved_chunk import RetrievedChunk
from app.embeddings.providers.sentence_transformer import (
    SentenceTransformerProvider,
)
from app.vectorstore.store import VectorStore
from app.reranking.service import Reranker


class RetrievalService:

    def __init__(
        self,
        db: Session,
        embedding_service: SentenceTransformerProvider,
        vector_store: VectorStore,
        reranker: Reranker,
    ):
        self.db = db
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.reranker = reranker

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

        # 2. Retrieve more candidates than we ultimately need
        candidate_limit = max(limit * 2, 10)

        results = self.vector_store.search(
            vector=query_vector,
            organization_id=organization_id,
            limit=candidate_limit,
        )

        if not results:
            return []

        # 3. Extract chunk IDs returned by Qdrant
        chunk_ids = [
            UUID(result.payload["chunk_id"])
            for result in results
        ]

        # 4. Fetch authoritative chunks + their documents
        chunks = (
            self.db.query(DocumentChunk)
            .options(
                selectinload(DocumentChunk.document)
            )
            .filter(
                DocumentChunk.id.in_(chunk_ids),
                DocumentChunk.document.has(
                    Document.organization_id == organization_id
                ),
            )
            .all()
        )

        # 5. Create lookup for efficient access
        chunks_by_id = {
            chunk.id: chunk
            for chunk in chunks
        }

        # 6. Align PostgreSQL chunks with Qdrant's order
        candidate_chunks = []

        candidate_results = []

        for result in results:
            chunk_id = UUID(
                result.payload["chunk_id"]
            )

            chunk = chunks_by_id.get(chunk_id)

            if chunk is None:
                continue

            candidate_chunks.append(chunk)
            candidate_results.append(result)

        if not candidate_chunks:
            return []

        # 7. Extract text for reranking
        documents = [
            chunk.content
            for chunk in candidate_chunks
        ]

        # 8. Rerank candidates
        ranked_indexes = self.reranker.rerank(
            query=query,
            documents=documents,
        )

        # 9. Take the best final candidates
        ranked_indexes = ranked_indexes[:limit]

        # 10. Convert back into RetrievedChunk objects
        retrieved_chunks: list[RetrievedChunk] = []

        for index in ranked_indexes:
            chunk = candidate_chunks[index]
            result = candidate_results[index]

            retrieved_chunks.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=result.score,
                )
            )

        return retrieved_chunks