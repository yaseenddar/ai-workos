from pydantic import BaseModel, EmailStr

class OrganizationMemberResponse(BaseModel):
    user_id: str
    email: EmailStr
    role: str
    is_active: bool
