# RBAC dependencies
# require_member()
#       │
#       ▼
# authenticated + organization member


# require_admin()
#       │
#       ▼
# OWNER or ADMIN


# require_owner()
#       │
#       ▼
# OWNER only
# inside every endpoint.

# That's centralized authorization.
from fastapi import Depends, HTTPException, status

from app.api.organization_context import get_current_membership
from app.db.models.membership import Membership, MembershipRole


def require_member(
    membership: Membership = Depends(
        get_current_membership
    ),
) -> Membership:

    return membership


def require_admin(
    membership: Membership = Depends(
        get_current_membership
    ),
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
    membership: Membership = Depends(
        get_current_membership
    ),
) -> Membership:

    if membership.role != MembershipRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner privileges required",
        )

    return membership

