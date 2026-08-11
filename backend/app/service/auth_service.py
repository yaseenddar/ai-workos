
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.membership import Membership, MembershipRole
from app.db.models.organization import Organization
from app.db.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
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

def authenticate_user(
    db: Session,
    *,
    email: str,
    password: str,
) -> User | None:

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def login_user(
    db: Session,
    *,
    email: str,
    password: str,
    secret_key: str,
    algorithm: str,
    access_token_expire_minutes: int,
    refresh_token_expire_days: int,
) -> tuple[str, str] | None:

    user = authenticate_user(
        db,
        email=email,
        password=password,
    )

    if user is None:
        return None

    access_token = create_access_token(
        user_id=str(user.id),
        secret_key=secret_key,
        algorithm=algorithm,
        expires_minutes=access_token_expire_minutes,
    )

    refresh_token = create_refresh_token(
        user_id=str(user.id),
        secret_key=secret_key,
        algorithm=algorithm,
        expires_days=refresh_token_expire_days,
    )

    return access_token, refresh_token
