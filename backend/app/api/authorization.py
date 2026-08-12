
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.membership import Membership, MembershipRole
from app.db.models.user import User
from app.db.session import get_db


def get_membership(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Membership:

    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == organization_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not belong to this organization",
        )

    return membership


def require_admin(
    membership: Membership = Depends(get_membership),
) -> Membership:

    if membership.role not in {
        MembershipRole.OWNER,
        MembershipRole.ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return membership


def require_owner(
    membership: Membership = Depends(get_membership),
) -> Membership:

    if membership.role != MembershipRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner privileges required",
        )

    return membership
