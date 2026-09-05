import uuid

from app.db.session import SessionLocal
from app.embeddings.providers.sentence_transformer import SentenceTransformerProvider
from app.retrieval.service import RetrievalService
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.store import VectorStore


db = SessionLocal()

try:
    embedding_service = SentenceTransformerProvider()
    vector_store = VectorStore(get_qdrant_client())

    retrieval_service = RetrievalService(
        db=db,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # organization_id = uuid.UUID(
    #     "23aee910-ddf8-41ac-a25d-cfed61658639"
    # )

    results = retrieval_service.retrieve(
        query="What is the purpose of the forwardRef function in React?",
        organization_id="23aee910-ddf8-41ac-a25d-cfed61658639",
        limit=5,
    )

    print(f"Results: {len(results)}")

    for result in results:
        chunk = result.chunk

        print("\n---")
        print("Score:", result.score)
        print("Chunk ID:", chunk.id)
        print("Document ID:", chunk.document_id)
        print("Chunk index:", chunk.chunk_index)
        print("Page:", chunk.page_number)
        print("Tokens:", chunk.token_count)
        print("Content:", chunk.content[:300])

finally:
    db.close()