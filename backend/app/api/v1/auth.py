from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.service.auth_service import register_user


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
