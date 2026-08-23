from typing import List


class TextChunker:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: list[dict]) -> List[dict]:
        chunks = []

        for page in pages:
            text = page["text"]
            page_number = page["page_number"]

            start = 0
            chunk_index = 0

            while start < len(text):
                end = start + self.chunk_size

                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "page_number": page_number,
                        "content": text[start:end],
                    }
                )

                chunk_index += 1
                start += self.chunk_size - self.overlap

        return chunks