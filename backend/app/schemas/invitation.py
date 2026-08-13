
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.db.models.membership import MembershipRole


class CreateInvitationRequest(BaseModel):
    email: EmailStr
    role: MembershipRole = MembershipRole.MEMBER


class InvitationResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    expires_at: datetime
    invitation_token: str


class AcceptInvitationRequest(BaseModel):
    token: str
