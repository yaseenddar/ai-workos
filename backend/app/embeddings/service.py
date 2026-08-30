from abc import ABC,abstractmethod

class EmbeddingService(ABC):
    
    @abstractmethod
    def embed_text(self,text:str) -> list[float]:
        """Generate an embedding for a single piece of text."""
        raise NotImplementedError
    
    @abstractmethod
    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple pieces of text."""
        raise NotImplementedError