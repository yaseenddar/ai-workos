from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.api.v1.router import api_router
from app.storage import MinioStorage

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage = MinioStorage()
    yield
    
app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan   
)

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    api_router,
    prefix="/api/v1",
)

