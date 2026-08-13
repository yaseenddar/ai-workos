from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.organization import router as organization_router
from app.api.v1.members import router as members_router
from app.api.v1.invitations import router as invitations
api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(organization_router)
api_router.include_router(members_router)
api_router.include_router(invitations)
