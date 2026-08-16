import uuid

from sqlalchemy.orm import Session

from app.db.models.ducument import Document, DocumentStatus
from app.storage.minio import MinioStorage


class DocumentService:

    def __init__(self, db: Session):
        self.db = db
        self.storage = MinioStorage()

    def upload_document(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> Document:

        storage_key = (
            f"{organization_id}/documents/"
            f"{uuid.uuid4()}.pdf"
        )


        try:
            self.storage.upload_file(
                object_name=storage_key,
                data=data,
                content_type=content_type,
            )

            # self.storage.upload_file(...)

            # document = Document(...)
            document = Document(
                organization_id=organization_id,
                uploaded_by=user_id,
                filename=filename,
                storage_key=storage_key,
                mime_type=content_type,
                file_size=len(data),
                status=DocumentStatus.UPLOADED,
            )

            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            return document

        except Exception:

            self.db.rollback()
            # roolbace and delte the record the from storage if the database operation fails
            self.storage.delete_file(storage_key)

            raise
        