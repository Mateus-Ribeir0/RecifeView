"""Liga o relato à conta de cidadão que o enviou, para ele acompanhar em "Meus relatos".

Relato enviado sem conta continua sem dono. A gestão não vê esta coluna em nenhuma tela.

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA = "app"


def upgrade() -> None:
    op.add_column(
        "contribuicao",
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA}.usuario.id")),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_app_contribuicao_usuario_id", "contribuicao", ["usuario_id"], schema=ESQUEMA
    )


def downgrade() -> None:
    op.drop_index("ix_app_contribuicao_usuario_id", "contribuicao", schema=ESQUEMA)
    op.drop_column("contribuicao", "usuario_id", schema=ESQUEMA)
