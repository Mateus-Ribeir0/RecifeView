"""Cria as tabelas de acesso: usuário, sessão e evento de acesso.

Revision ID: 0001
Revises:
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA = "app"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {ESQUEMA}")
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("perfil", sa.String(30), nullable=False),
        sa.Column("hash_da_senha", sa.String(255), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("deve_trocar_senha", sa.Boolean(), nullable=False),
        sa.Column("tentativas_falhas", sa.Integer(), nullable=False),
        sa.Column("bloqueado_ate", sa.DateTime(timezone=True)),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema=ESQUEMA,
    )
    op.create_table(
        "sessao",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA}.usuario.id"), nullable=False),
        sa.Column("hash_do_token", sa.String(64), nullable=False, unique=True),
        sa.Column("criada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revogada_em", sa.DateTime(timezone=True)),
        schema=ESQUEMA,
    )
    op.create_index("ix_app_sessao_usuario_id", "sessao", ["usuario_id"], schema=ESQUEMA)
    op.create_table(
        "evento_de_acesso",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA}.usuario.id")),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("ocorrido_em", sa.DateTime(timezone=True), nullable=False),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_app_evento_de_acesso_usuario_id", "evento_de_acesso", ["usuario_id"], schema=ESQUEMA
    )
    op.create_index(
        "ix_app_evento_de_acesso_ocorrido_em", "evento_de_acesso", ["ocorrido_em"], schema=ESQUEMA
    )


def downgrade() -> None:
    op.drop_table("evento_de_acesso", schema=ESQUEMA)
    op.drop_table("sessao", schema=ESQUEMA)
    op.drop_table("usuario", schema=ESQUEMA)
