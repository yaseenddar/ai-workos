
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(
        min_length=2,
        max_length=255,
    )


class RegisterResponse(BaseModel):
    user_id: str
    organization_id: str
    email: EmailStr
