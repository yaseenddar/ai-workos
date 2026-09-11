from abc import ABC, abstractmethod


class Reranker(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[str],
    ) -> list[int]:
        """
        Return document indexes ordered from
        most relevant to least relevant.
        """
        raise NotImplementedError