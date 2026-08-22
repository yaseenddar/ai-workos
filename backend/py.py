from app.workers.document_tasks import process_document

result = process_document.delay("test-document-123")

print(result.id)