"""add ivfflat index on review.embedding

Revision ID: f3cd63243444
Revises: 0039f7c7b4c0
Create Date: 2025-09-10 09:37:11.831984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3cd63243444'
down_revision: Union[str, None] = '0039f7c7b4c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_review_embedding_ann
        ON review
        USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_review_embedding_ann")
