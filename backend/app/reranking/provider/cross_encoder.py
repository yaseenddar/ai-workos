from sentence_transformers import CrossEncoder

from app.reranking.service import Reranker


class CrossEncoderReranker(Reranker):

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: list[str],
    ) -> list[int]:

        pairs = [
            (query, document)
            for document in documents
        ]

        scores = self.model.predict(pairs)
        
        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        return ranked_indexes