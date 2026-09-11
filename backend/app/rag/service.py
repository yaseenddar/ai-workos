from uuid import UUID

from app.context.builder import ContextBuilder
from app.llm.service import LLMService
from app.rag.model import RAGResponse, Source
from app.rag.prompt import RAG_PROMPT
from app.retrieval.service import RetrievalService


class RAGService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_builder: ContextBuilder,
        llm: LLMService,
    ):
        self.retrieval_service = retrieval_service
        self.context_builder = context_builder
        self.llm = llm

    def answer(
        self,
        question: str,
        organization_id: UUID,
        limit: int = 5,
    ) -> RAGResponse:

        # 1. Retrieve relevant document chunks
        retrieved_chunks = self.retrieval_service.retrieve(
            query=question,
            organization_id=organization_id,
            limit=limit,
        )
        if not retrieved_chunks:
            return RAGResponse(
                answer="I couldn't find the answer in the provided documents.",
                sources=[],
            )
        # 2. Build context for the LLM
        context = self.context_builder.build(
            retrieved_chunks
        )

        # 3. Build the RAG prompt
        messages = RAG_PROMPT.format_messages(
            context=context,
            question=question,
        )

        # 4. Convert LangChain messages into a prompt
        prompt = "\n\n".join(
            message.content
            for message in messages
        )

        # 5. Generate the answer
        answer = self.llm.generate(
            prompt=prompt,
        )

        # 6. Build structured source information
        sources = [
            Source(
                document_id=retrieved.chunk.document_id,
                document_name=retrieved.chunk.document.filename,
                page_number=retrieved.chunk.page_number,
                score=retrieved.score,
            )
            for retrieved in retrieved_chunks
        ]

        # 7. Return answer + sources
        return RAGResponse(
            answer=answer,
            sources=sources,
        )