
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

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
