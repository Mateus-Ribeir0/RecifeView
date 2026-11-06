"""Cria a quarentena do formulário público, os pares do pente fino e a lista de vias.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA_DA_APLICACAO = "app"
ESQUEMA_ANALITICO = "ouro"


def _criar_contribuicao() -> None:
    op.create_table(
        "contribuicao",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("chave_de_envio", sa.String(64), nullable=False, unique=True),
        sa.Column("recebida_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_relato", sa.Date(), nullable=False),
        sa.Column("categoria", sa.Text(), nullable=False),
        sa.Column("servico_codigo", sa.Text(), nullable=False),
        sa.Column("servico", sa.Text(), nullable=False),
        sa.Column(
            "bairro_oficial",
            sa.Text(),
            sa.ForeignKey(f"{ESQUEMA_ANALITICO}.dim_bairro.bairro_oficial"),
            nullable=False,
        ),
        sa.Column("logradouro", sa.Text()),
        sa.Column("numero", sa.Text()),
        sa.Column("detalhe", sa.Text()),
        sa.Column("id_local", sa.Text()),
        sa.Column("numero_informado", sa.Boolean(), nullable=False),
        sa.Column("retorno", sa.String(30), nullable=False),
        sa.Column("resultado", sa.String(20), nullable=False),
        sa.Column(
            "principal_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.contribuicao.id")
        ),
        sa.Column(
            "importacao_id", sa.Integer(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.importacao.id")
        ),
        sa.Column(
            "retirada_por", sa.Integer(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.importacao.id")
        ),
        sa.Column("expurgada_em", sa.DateTime(timezone=True)),
        schema=ESQUEMA_DA_APLICACAO,
    )
    op.create_index(
        "ix_app_contribuicao_bloco",
        "contribuicao",
        ["bairro_oficial", "categoria", "data_relato"],
        schema=ESQUEMA_DA_APLICACAO,
    )
    op.create_index(
        "ix_app_contribuicao_principal_id",
        "contribuicao",
        ["principal_id"],
        schema=ESQUEMA_DA_APLICACAO,
    )


def _criar_par_de_contribuicoes() -> None:
    contribuicao = f"{ESQUEMA_DA_APLICACAO}.contribuicao.id"
    op.create_table(
        "par_de_contribuicoes",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("primeira_id", sa.Uuid(), sa.ForeignKey(contribuicao), nullable=False),
        sa.Column("segunda_id", sa.Uuid(), sa.ForeignKey(contribuicao), nullable=False),
        sa.Column("pontuacao", sa.Float(), nullable=False),
        sa.Column("motivos", postgresql.JSONB(), nullable=False),
        sa.Column("decisao", sa.String(20)),
        sa.Column("decidido_por", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id")),
        sa.Column("decidido_em", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("primeira_id", "segunda_id"),
        schema=ESQUEMA_DA_APLICACAO,
    )


def _criar_dim_logradouro() -> None:
    op.create_table(
        "dim_logradouro",
        sa.Column(
            "bairro_oficial",
            sa.Text(),
            sa.ForeignKey(f"{ESQUEMA_ANALITICO}.dim_bairro.bairro_oficial"),
            primary_key=True,
        ),
        sa.Column("logradouro", sa.Text(), primary_key=True),
        sa.Column("pedidos", sa.Integer(), nullable=False),
        schema=ESQUEMA_ANALITICO,
    )


def upgrade() -> None:
    _criar_contribuicao()
    _criar_par_de_contribuicoes()
    _criar_dim_logradouro()


def downgrade() -> None:
    op.drop_table("dim_logradouro", schema=ESQUEMA_ANALITICO)
    op.drop_table("par_de_contribuicoes", schema=ESQUEMA_DA_APLICACAO)
    op.drop_table("contribuicao", schema=ESQUEMA_DA_APLICACAO)
