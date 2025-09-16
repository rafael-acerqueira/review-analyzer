"""add review.embedding vector

Revision ID: 0039f7c7b4c0
Revises: 4d1134228d08
Create Date: 2025-09-10 09:36:17.958315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0039f7c7b4c0'
down_revision: Union[str, None] = '4d1134228d08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column("review", sa.Column("embedding", Vector(dim=384), nullable=True))

def downgrade():
    op.drop_column("review", "embedding")
