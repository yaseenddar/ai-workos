from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.service.auth_service import register_user

from app.core.config import get_settings
from app.schemas.auth import LoginRequest, TokenResponse
from app.service.auth_service import login_user

from app.api.dependencies import get_current_user
from app.db.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register",response_model=RegisterResponse,status_code=status.HTTP_201_CREATED,)
def register(payload: RegisterRequest,db: Session = Depends(get_db),):
    
    try:
        user, organization = register_user(
            db,
            email=payload.email,
            password=payload.password,
            organization_name=payload.organization_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return RegisterResponse(
        user_id=str(user.id),
        organization_id=str(organization.id),
        email=user.email,
    )
@router.post("/login",response_model=TokenResponse,)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    settings = get_settings()

    tokens = login_user(
        db,
        email=payload.email,
        password=payload.password,
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=(
            settings.access_token_expire_minutes
        ),
        refresh_token_expire_days=(
            settings.refresh_token_expire_days
        ),
    )

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token, refresh_token = tokens

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )




@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "is_active": current_user.is_active,
    }
