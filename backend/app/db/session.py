from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings
# SQLAlchemy maintains a connection pool underneath.
# Application
#     │
#     ▼
# SQLAlchemy
#     │
#     ▼
# Connection Pool
#  ┌──┼──┬──┐
#  ▼  ▼  ▼  ▼
#  DB DB DB DB

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()