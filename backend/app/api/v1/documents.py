from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentUploadResponse
from app.service.document_service import DocumentService

from app.db.models.user import User
from app.db.models.membership import Membership

from app.api.dependencies import get_current_user
from app.api.dependencies import require_member

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: Membership = Depends(require_member),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    data = await file.read()

    service = DocumentService(db)

    document = service.upload_document(
        organization_id=membership.organization_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
    )

    return document