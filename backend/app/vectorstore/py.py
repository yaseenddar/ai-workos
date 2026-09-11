from app.context.builder import ContextBuilder
from app.db.session import SessionLocal
from app.embeddings.providers.sentence_transformer import (
    SentenceTransformerProvider,
)
from app.llm.gimini import GeminiProvider
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.store import VectorStore
from app.reranking.provider.cross_encoder import CrossEncoderReranker
db = SessionLocal()
from uuid import UUID
embedding_service = SentenceTransformerProvider()

vector_store = VectorStore(
    get_qdrant_client()
)

retrieval_service = RetrievalService(
    db=db,
    embedding_service=embedding_service,
    vector_store=vector_store,
    reranker=CrossEncoderReranker(),
)

context_builder = ContextBuilder()

llm = GeminiProvider()

rag = RAGService(
    retrieval_service=retrieval_service,
    context_builder=context_builder,
    llm=llm,
)
results = retrieval_service.retrieve(
    query="What is JSX",
    organization_id=UUID("23aee910-ddf8-41ac-a25d-cfed61658639"),
    limit=5,
)

for result in results:
    print(
        result.chunk.document.filename,
        "| Page:", result.chunk.page_number,
        "| Qdrant score:", result.score,
    )
db.close()