
# ┌──────────────────┐
# │  organizations   │
# ├──────────────────┤
# │ id               │
# │ name             │
# │ created_at       │
# │ updated_at       │
# └────────┬─────────┘
#          │
#          │ 1
#          │
#          │ N
# ┌────────▼─────────┐
# │   memberships    │
# ├──────────────────┤
# │ id               │
# │ user_id          │
# │ organization_id  │
# │ role             │
# │ created_at       │
# └────────┬─────────┘
#          │
#          │ N
#          │
#          │ 1
# ┌────────▼─────────┐
# │      users       │
# ├──────────────────┤
# │ id               │
# │ email            │
# │ password_hash    │
# │ is_active        │
# │ created_at       │
# │ updated_at       │
# └──────────────────┘


import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
