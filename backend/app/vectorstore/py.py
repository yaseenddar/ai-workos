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

db = SessionLocal()

embedding_service = SentenceTransformerProvider()

vector_store = VectorStore(
    get_qdrant_client()
)

retrieval_service = RetrievalService(
    db=db,
    embedding_service=embedding_service,
    vector_store=vector_store,
)

context_builder = ContextBuilder()

llm = GeminiProvider()

rag = RAGService(
    retrieval_service=retrieval_service,
    context_builder=context_builder,
    llm=llm,
)

questions = [
    "What frontend technologies does the developer use?",
    "What company does the developer currently work for?",
    "What is SecurePay?",
    "What is JSX?",
    "Explain React hooks.",
    "Who is the developer?",
    "What database technologies are mentioned?",
    "Who was the first president of the United States?",
]

for question in questions:
    print("=" * 80)
    print(f"QUESTION: {question}")

    answer = rag.answer(
        question=question,
        organization_id="23aee910-ddf8-41ac-a25d-cfed61658639",
    )

    print("\nANSWER:")
    print(answer.answer)

    print("\nSOURCES:")
    for source in answer.sources:
        print(
            f"- {source.document_name} | "
            f"Page {source.page_number} | "
            f"Score {source.score}"
        )

    print()
db.close()