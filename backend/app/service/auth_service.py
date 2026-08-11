
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.membership import Membership, MembershipRole
from app.db.models.organization import Organization
from app.db.models.user import User


def register_user(
    db: Session,
    *,
    email: str,
    password: str,
    organization_name: str,
) -> tuple[User, Organization]:

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("User already exists")

    password_hash = hash_password(password)

    user = User(
        email=email,
        password_hash=password_hash,
    )

    organization = Organization(
        name=organization_name,
    )

    db.add(user)
    db.add(organization)

    db.flush() #This sends the INSERTs to PostgreSQL without committing the transaction.

    membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role=MembershipRole.OWNER,
    )

    db.add(membership)

    db.commit()

    db.refresh(user)
    db.refresh(organization)

    return user, organization
