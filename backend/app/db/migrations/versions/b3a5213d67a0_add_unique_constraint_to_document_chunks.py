"""add unique constraint to document chunks

Revision ID: b3a5213d67a0
Revises: c59157a10580
Create Date: 2026-09-01 23:03:37.209999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3a5213d67a0'
down_revision: Union[str, Sequence[str], None] = 'c59157a10580'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_document_chunks_document_id_chunk_index",
        "document_chunks",
        ["document_id", "chunk_index"],
    )

def downgrade() -> None:
    op.drop_constraint(
        "uq_document_chunks_document_id_chunk_index",
        "document_chunks",
        type_="unique",
    )
