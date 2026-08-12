
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.membership import Membership
from app.db.models.user import User
from app.db.session import get_db


# Now every protected organization-aware endpoint can simply depend on:
def get_current_membership(
    x_organization_id: UUID | None = Header(
        default=None,
        alias="X-Organization-ID",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Membership:

    if x_organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Organization-ID header is required",
        )

    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == x_organization_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not belong to this organization",
        )

    return membership
