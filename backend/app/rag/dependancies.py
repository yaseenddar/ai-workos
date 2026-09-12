from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.context.builder import ContextBuilder
from app.db.session import get_db
from app.embeddings.providers.sentence_transformer import (
    SentenceTransformerProvider,
)
from app.llm.gimini import GeminiProvider
from app.rag.service import RAGService
from app.reranking.provider.cross_encoder import CrossEncoderReranker
from app.retrieval.service import RetrievalService
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.store import VectorStore


@lru_cache
def get_embedding_service() -> SentenceTransformerProvider:
    return SentenceTransformerProvider()


@lru_cache
def get_reranker() -> CrossEncoderReranker:
    return CrossEncoderReranker()


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore(
        get_qdrant_client()
    )


@lru_cache
def get_llm() -> GeminiProvider:
    return GeminiProvider()


def get_rag_service(
    db: Session = Depends(get_db),
    embedding_service: SentenceTransformerProvider = Depends(
        get_embedding_service
    ),
    vector_store: VectorStore = Depends(
        get_vector_store
    ),
    reranker: CrossEncoderReranker = Depends(
        get_reranker
    ),
    llm: GeminiProvider = Depends(
        get_llm
    ),
) -> RAGService:

    retrieval_service = RetrievalService(
        db=db,
        embedding_service=embedding_service,
        vector_store=vector_store,
        reranker=reranker,
    )

    context_builder = ContextBuilder()

    return RAGService(
        retrieval_service=retrieval_service,
        context_builder=context_builder,
        llm=llm,
    )