from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return password_hasher.verify(
            password_hash,
            password,
        )
    except (VerifyMismatchError, VerificationError):
        return False


def create_access_token(
    user_id: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    return _create_token(
        user_id=user_id,
        token_type="access",
        secret_key=secret_key,
        algorithm=algorithm,
        expires_delta=timedelta(
            minutes=expires_minutes
        ),
    )


def create_refresh_token(
    user_id: str,
    secret_key: str,
    algorithm: str,
    expires_days: int,
) -> str:
    return _create_token(
        user_id=user_id,
        token_type="refresh",
        secret_key=secret_key,
        algorithm=algorithm,
        expires_delta=timedelta(
            days=expires_days
        ),
    )


def _create_token(
    user_id: str,
    token_type: str,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta,
) -> str:

    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta

    payload: dict[str, Any] = {
        "sub": user_id,
        "type": token_type,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def decode_token(
    token: str,
    secret_key: str,
    algorithm: str,
) -> dict[str, Any]:

    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
    )
