import uuid

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.ducument import Document, DocumentStatus
from app.storage.minio import MinioStorage
from app.ai.parser import PDFParser
from app.ai.chunker import TextChunker
from app.db.models import DocumentChunk

@celery_app.task(name="documents.process")
def process_document(document_id: str):
    db = SessionLocal()
    storage = MinioStorage()
    parser = PDFParser()

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

        print(f"Total chunks: {len(chunks)}")

        for chunk in chunks:
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk["chunk_index"],
                    page_number=chunk["page_number"],
                    content=chunk["content"],
                    token_count=len(chunk["content"].split()),
                    embedding_id=None,
                    
                )
            )
        db.commit()
        document.status = DocumentStatus.INDEXED
        db.commit()
        return {
            "document_id": document_id,
            "status": document.status.value,
            "pages": len(pages),
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
        