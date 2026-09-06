from app.retrieval.models.retrieved_chunk import RetrievedChunk


class ContextBuilder:

    def build(
        self,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:

        context_parts = []

        for index, retrieved in enumerate(
            retrieved_chunks,
            start=1,
        ):
            chunk = retrieved.chunk

            context_parts.append(
                f"[Source {index} | Page {chunk.page_number}]\n"
                f"{chunk.content}"
            )

        return "\n\n".join(context_parts)