import uuid
from datetime import datetime
from pydantic import BaseModel

from app.db.models.ducument import DocumentStatus


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: DocumentStatus
    created_at: datetime

    model_config = {
        "from_attributes": True
    }