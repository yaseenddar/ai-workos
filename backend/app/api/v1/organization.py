
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.authorization import get_membership
from app.db.models.membership import Membership


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/{organization_id}")
def get_organization(
    organization_id: UUID,
    membership: Membership = Depends(get_membership),
):
    return {
        "organization_id": str(
            membership.organization_id
        ),
        "role": membership.role.value,
    }
