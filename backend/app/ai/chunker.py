from typing import List

import tiktoken


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 800,
        overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

        self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk_pages(self, pages: list[dict]) -> List[dict]:
        chunks = []
        global_chunk_index = 0

        step = self.chunk_size - self.overlap

        for page in pages:
            text = page["text"]
            page_number = page["page_number"]

            if not text:
                continue

            tokens = self.encoding.encode(text)

            start = 0

            while start < len(tokens):
                end = start + self.chunk_size

                chunk_tokens = tokens[start:end]

                content = self.encoding.decode(chunk_tokens)

                chunks.append(
                    {
                        "chunk_index": global_chunk_index,
                        "page_number": page_number,
                        "content": content,
                    }
                )

                global_chunk_index += 1
                start += step

        return chunks