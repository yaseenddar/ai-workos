
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.permissions import require_admin
from app.db.models.membership import Membership
from app.db.session import get_db
from app.schemas.invitation import (
    CreateInvitationRequest,
    InvitationResponse,
)
from app.service.invitation_service import create_invitation


router = APIRouter(
    prefix="/organizations/invitations",
    tags=["Invitations"],
)


@router.post(
    "",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def invite_member(
    payload: CreateInvitationRequest,
    membership: Membership = Depends(require_admin),
    db=Depends(get_db),
):
    try:
        invitation, token = create_invitation(
            db,
            organization_id=membership.organization_id,
            invited_by_user_id=membership.user_id,
            email=payload.email,
            role=payload.role,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return InvitationResponse(
        id=str(invitation.id),
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        invitation_token=token,
    )

