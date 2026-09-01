import uuid

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.ducument import Document, DocumentStatus
from app.storage.minio import MinioStorage
from app.ai.parser import PDFParser
from app.ai.chunker import TextChunker
from app.db.models import DocumentChunk
from app.ai.tokenizer import count_tokens
from app.embeddings.providers.sentence_transformer import SentenceTransformerProvider
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.store import VectorStore


@celery_app.task(name="documents.process")
def process_document(document_id: str):
    db = SessionLocal()
    storage = MinioStorage()
    parser = PDFParser()
    embedding_service = SentenceTransformerProvider()
    vector_store = VectorStore(get_qdrant_client())
    
    try:
        document_uuid = uuid.UUID(document_id)

        document = db.get(Document, document_uuid)

        if document is None:
            raise ValueError(f"Document {document_id} not found")

        # Mark as processing
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        # Download PDF from MinIO
        pdf_bytes = storage.download_file(document.storage_key)

        # Parse PDF into pages
        pages = parser.parse(pdf_bytes)

        print(f"Processing: {document.filename}")
        print(f"Pages extracted: {len(pages)}")

        for page in pages:
            preview = page["text"][:80].replace("\n", " ")
            print(f"Page {page['page_number']}: {preview}")

        chunker = TextChunker()
        chunks = chunker.chunk_pages(pages)
        
        document_chunks = []
        
        print(f"Total chunks: {len(chunks)}")

        for chunk in chunks:
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk["chunk_index"],
                page_number=chunk["page_number"],
                content=chunk["content"],
                token_count=count_tokens(
                    chunk["content"]
                ),
                embedding_id=None,
            )

            db.add(document_chunk)
            document_chunks.append(document_chunk)
        db.commit()
       # Make sure there is something to embed
        if not document_chunks:
            raise ValueError(
                "No text chunks were generated from the document"
            )

        # Extract chunk text
        texts = [
            chunk.content
            for chunk in document_chunks
        ]

        # Generate embeddings in one batch
        vectors = embedding_service.embed_documents(
            texts
        )

        print(
            f"Embeddings generated: {len(vectors)}"
        )

        print(
            f"Vector dimensions: "
            f"{[len(vector) for vector in vectors]}"
        )

        # TODO: Upsert vectors into Qdrant
        # Ensure Qdrant collection exists
        vector_store.ensure_collection()

        # Build Qdrant point data
        chunk_ids = [
            chunk.id
            for chunk in document_chunks
        ]

        payloads = [
            {
                "organization_id": str(document.organization_id),
                "document_id": str(document.id),
                "chunk_id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
            }
            for chunk in document_chunks
        ]

        # Store all embeddings in Qdrant
        vector_store.upsert_many(
            chunk_ids=chunk_ids,
            vectors=vectors,
            payloads=payloads,
        )

        print(
            f"Indexed {len(vectors)} vectors in Qdrant"
        )
        # Document will become INDEXED only
        # after Qdrant indexing is successful.
        document.status = DocumentStatus.INDEXED
        db.commit()
        return {
            "message": "Document processed successfully",
            "document_id": document_id,
            "status": document.status.value,
            "pages": len(pages),
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
        