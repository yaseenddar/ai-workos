"""add organization invitations

Revision ID: f4192cc26278
Revises: 28f1d0585bb2
Create Date: 2026-08-13 19:23:02.953151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4192cc26278'
down_revision: Union[str, Sequence[str], None] = '28f1d0585bb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    invitation_status = postgresql.ENUM(
        "PENDING",
        "ACCEPTED",
        "REVOKED",
        "EXPIRED",
        name="invitationstatus",
        create_type=False,  # Don't create the type if it already exists
    )

    # # Create the PostgreSQL enum
    invitation_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("invited_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("status", invitation_status, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(
            ["invited_by_user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_organization_invitations_email"),
        "organization_invitations",
        ["email"],
    )
    op.create_index(
        op.f("ix_organization_invitations_organization_id"),
        "organization_invitations",
        ["organization_id"],
    )
    op.create_index(
        op.f("ix_organization_invitations_token_hash"),
        "organization_invitations",
        ["token_hash"],
        unique=True,
    )
def downgrade() -> None:
    op.drop_index(op.f("ix_organization_invitations_token_hash"),
                    table_name="organization_invitations")
    op.drop_index(op.f("ix_organization_invitations_organization_id"),
                    table_name="organization_invitations")
    op.drop_index(op.f("ix_organization_invitations_email"),
                    table_name="organization_invitations")
    op.drop_table("organization_invitations")

    op.execute("DROP TYPE IF EXISTS invitationstatus")