"""Prepara as contas de cidadão: confirmação de e-mail, bairro e códigos por e-mail.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA = "app"


def upgrade() -> None:
    op.add_column(
        "usuario", sa.Column("email_confirmado_em", sa.DateTime(timezone=True)), schema=ESQUEMA
    )
    op.add_column(
        "usuario",
        sa.Column("bairro_oficial", sa.Text(), sa.ForeignKey("ouro.dim_bairro.bairro_oficial")),
        schema=ESQUEMA,
    )
    op.execute(f"UPDATE {ESQUEMA}.usuario SET email_confirmado_em = criado_em")
    op.create_table(
        "codigo_de_conta",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA}.usuario.id"), nullable=False),
        sa.Column("finalidade", sa.String(30), nullable=False),
        sa.Column("hash_do_codigo", sa.String(64), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tentativas", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("usado_em", sa.DateTime(timezone=True)),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_app_codigo_de_conta_usuario_id", "codigo_de_conta", ["usuario_id"], schema=ESQUEMA
    )


def downgrade() -> None:
    op.drop_table("codigo_de_conta", schema=ESQUEMA)
    op.drop_column("usuario", "bairro_oficial", schema=ESQUEMA)
    op.drop_column("usuario", "email_confirmado_em", schema=ESQUEMA)
