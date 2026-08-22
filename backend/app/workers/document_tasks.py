import uuid

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.ducument import Document, DocumentStatus

@celery_app.task(name="documents.process")
def process_document(document_id: str):

    db = SessionLocal()
    try:
        # convert the string received from Celery into UUID
        document_uuid = uuid.UUID(document_id)
        
        # Find the document 
        document = db.get(Document,document_uuid)
        
        if document is None:
            raise ValueError(f"Document {document_id} not found")
        
        # Mark document as processing
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        print(f"Document {document_id} is now PROCESSING")
        
        return {
            "document_id" : document_id,
            "status":"PROCESSING"
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        
    
