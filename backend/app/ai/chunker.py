from app.ai.tokenizer import count_tokens


class TextChunker:

    CHUNK_SIZE = 500
    OVERLAP = 100

    @classmethod
    def chunk_pages(cls, pages):

        chunks = []
        chunk_index = 0

        for page in pages:

            words = page["text"].split()

            start = 0

            while start < len(words):

                end = start + cls.CHUNK_SIZE

                content = " ".join(words[start:end])

                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "page_number": page["page"],
                        "content": content,
                        "token_count": count_tokens(content),
                    }
                )

                chunk_index += 1

                start += cls.CHUNK_SIZE - cls.OVERLAP

        return chunks