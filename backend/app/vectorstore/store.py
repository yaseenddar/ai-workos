from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from uuid import UUID
from qdrant_client.models import PointStruct

class VectorStore:

    def __init__(self, client: QdrantClient):
        self.client = client

    def ensure_collection(self) -> None:
        collection_name = "document_chunks"

        existing_collections = self.client.get_collections()

        collection_exists = any(
            collection.name == collection_name
            for collection in existing_collections.collections
        )

        if collection_exists:
            return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )
    
    def upsert(
        self,
        chunk_id: UUID,
        vector: list[float],
        payload: dict,
    ) -> None:

        self.client.upsert(
            collection_name="document_chunks",
            points=[
                PointStruct(
                    id=str(chunk_id),
                    vector=vector,
                    payload=payload,
                )
            ],
        )
    def search(
        self,
        vector: list[float],
        limit: int = 5,
        ):
        
        return self.client.query_points(
            collection_name="document_chunks",
            query=vector,
            limit=limit,
        ).points
    
    def upsert_many(
        self,
        chunk_ids: list[UUID],
        vectors: list[list[float]],
        payloads: list[dict],
    ) -> None:

        if not (
            len(chunk_ids)
            == len(vectors)
            == len(payloads)
        ):
            raise ValueError(
                "chunk_ids, vectors, and payloads "
                "must have the same length"
            )

        points = [
            PointStruct(
                id=str(chunk_id),
                vector=vector,
                payload=payload,
            )
            for chunk_id, vector, payload
            in zip(chunk_ids, vectors, payloads)
        ]

        self.client.upsert(
            collection_name="document_chunks",
            points=points,
        )