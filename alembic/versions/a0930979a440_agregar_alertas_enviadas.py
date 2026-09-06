"""agregar alertas enviadas

Revision ID: a0930979a440
Revises: 21de662ca10c
Create Date: 2026-09-06 08:43:42.105431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0930979a440'
down_revision: Union[str, Sequence[str], None] = '21de662ca10c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alertas_enviadas",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "producto_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "precio",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "fecha_envio",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"],
            ["productos_monitoreados.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("producto_id"),
    )


def downgrade() -> None:
    op.drop_table("alertas_enviadas")
