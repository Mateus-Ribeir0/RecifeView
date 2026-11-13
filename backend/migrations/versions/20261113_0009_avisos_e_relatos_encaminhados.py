"""Guarda a preferência de avisos da conta, o lembrete ao órgão e o relato encaminhado.

O encaminhamento de uma ocorrência do formulário aponta para o relato principal e guarda o local
aproximado (rua oficial e faixa de numeração) que foi na mensagem, porque o endereço do relato é
apagado em 90 dias (ADR 0011).

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA = "app"


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column("recebe_avisos", sa.Boolean(), nullable=False, server_default=sa.true()),
        schema=ESQUEMA,
    )
    op.add_column(
        "encaminhamento",
        sa.Column(
            "contribuicao_id",
            sa.Uuid(),
            sa.ForeignKey(f"{ESQUEMA}.contribuicao.id", ondelete="SET NULL"),
        ),
        schema=ESQUEMA,
    )
    op.add_column("encaminhamento", sa.Column("referencia_de_local", sa.Text()), schema=ESQUEMA)
    op.add_column(
        "encaminhamento",
        sa.Column("lembrete_enviado_em", sa.DateTime(timezone=True)),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_app_encaminhamento_contribuicao_id",
        "encaminhamento",
        ["contribuicao_id"],
        schema=ESQUEMA,
    )


def downgrade() -> None:
    op.drop_index("ix_app_encaminhamento_contribuicao_id", "encaminhamento", schema=ESQUEMA)
    op.drop_column("encaminhamento", "lembrete_enviado_em", schema=ESQUEMA)
    op.drop_column("encaminhamento", "referencia_de_local", schema=ESQUEMA)
    op.drop_column("encaminhamento", "contribuicao_id", schema=ESQUEMA)
    op.drop_column("usuario", "recebe_avisos", schema=ESQUEMA)
