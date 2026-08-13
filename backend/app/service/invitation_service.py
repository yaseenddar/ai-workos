
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.token import generate_token, hash_token

from app.db.models.activation import (
    InvitationStatus,
    OrganizationInvitation,
)
from app.db.models.membership import MembershipRole


def create_invitation(
    db: Session,
    *,
    organization_id,
    invited_by_user_id,
    email: str,
    role: MembershipRole,
):
    existing = db.scalar(
        select(OrganizationInvitation).where(
            OrganizationInvitation.email == email,
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.status == InvitationStatus.PENDING,
        )
    )

    if existing:
        raise ValueError("Pending invitation already exists")

    raw_token = generate_token()

    invitation = OrganizationInvitation(
        organization_id=organization_id,
        invited_by_user_id=invited_by_user_id,
        email=email,
        role=role.value,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation, raw_token
