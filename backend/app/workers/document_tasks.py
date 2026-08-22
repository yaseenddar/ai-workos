import uuid

from app.worker.celery_app import celery_app

S
@celery_app.task(name="documents.process")
def process_document(document_id: str):

    print(f"Processing document {document_id}")

    return {"document_id": document_id}