from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.permissions import require_member
from app.db.models.membership import Membership
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import OrganizationMemberResponse


router = APIRouter(
    prefix="/organizations/members",
    tags=["Organization Members"],
)


@router.get("",response_model=list[OrganizationMemberResponse],)
def list_members(membership: Membership = Depends(require_member),db: Session = Depends(get_db),):
    rows = db.execute(
        select(User, Membership)
        .join(
            Membership,
            Membership.user_id == User.id,
        )
        .where(
            Membership.organization_id
            == membership.organization_id
        )
    ).all()

    return [
        OrganizationMemberResponse(
            user_id=str(user.id),
            email=user.email,
            role=member.role.value,
            is_active=user.is_active,
        )
        for user, member in rows
    ]

