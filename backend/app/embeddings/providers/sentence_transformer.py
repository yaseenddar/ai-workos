from sentence_transformers import SentenceTransformer

from app.embeddings.service import EmbeddingService
from app.core.config import get_settings

class SentenceTransformerProvider(EmbeddingService):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model)

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text,convert_to_numpy=True).tolist()

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return self.model.encode(texts,convert_to_numpy=True).tolist()