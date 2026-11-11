"""Guarda o protocolo da fonte e cria os encaminhamentos aos órgãos e os pedidos acompanhados.

O protocolo serve só à consulta exata pelo cidadão (ADR 0011). O encaminhamento guarda uma cópia
do que foi mandado ao órgão, porque o registro de origem pode ser substituído por uma importação.

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA_DA_APLICACAO = "app"
ESQUEMA_ANALITICO = "ouro"
TABELAS_DE_DEMANDA = ("fato_demanda", "fato_demanda_substituida")


def _guardar_protocolo() -> None:
    for tabela in TABELAS_DE_DEMANDA:
        op.add_column(tabela, sa.Column("protocolo", sa.Text()), schema=ESQUEMA_ANALITICO)
    op.create_index(
        "ix_ouro_fato_demanda_protocolo",
        "fato_demanda",
        ["protocolo"],
        schema=ESQUEMA_ANALITICO,
        postgresql_where=sa.text("protocolo IS NOT NULL"),
    )


def _criar_encaminhamento() -> None:
    op.create_table(
        "encaminhamento",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("chave_registro", sa.BigInteger(), nullable=False),
        sa.Column("fonte", sa.String(30), nullable=False),
        sa.Column("data_abertura", sa.Date()),
        sa.Column("categoria", sa.Text()),
        sa.Column("servico", sa.Text()),
        sa.Column("bairro_oficial", sa.Text()),
        sa.Column("rpa", sa.Text()),
        sa.Column("situacao_na_fonte", sa.Text()),
        sa.Column("orgao_na_fonte", sa.Text()),
        sa.Column("protocolo_de_origem", sa.Text()),
        sa.Column("nota", sa.Float()),
        sa.Column("orgao", sa.String(30), nullable=False),
        sa.Column("orgao_sugerido", sa.String(30)),
        sa.Column("canal", sa.String(20), nullable=False),
        sa.Column("situacao", sa.String(20), nullable=False),
        sa.Column("justificativa", sa.Text()),
        sa.Column("automatico", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("criado_por", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id")),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prazo_de_resposta", sa.Date(), nullable=False),
        sa.Column("hash_do_token", sa.String(64), nullable=False, unique=True),
        sa.Column("token_expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("protocolo_do_orgao", sa.Text()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        schema=ESQUEMA_DA_APLICACAO,
    )
    for coluna in ("chave_registro", "situacao", "orgao"):
        op.create_index(
            f"ix_app_encaminhamento_{coluna}",
            "encaminhamento",
            [coluna],
            schema=ESQUEMA_DA_APLICACAO,
        )


def _criar_evento_de_encaminhamento() -> None:
    op.create_table(
        "evento_de_encaminhamento",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "encaminhamento_id",
            sa.Integer(),
            sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.encaminhamento.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("situacao", sa.String(20), nullable=False),
        sa.Column("autor", sa.String(20), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id")),
        sa.Column("ocorrido_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("observacao", sa.Text()),
        sa.Column("protocolo_do_orgao", sa.Text()),
        schema=ESQUEMA_DA_APLICACAO,
    )
    op.create_index(
        "ix_app_evento_de_encaminhamento_encaminhamento_id",
        "evento_de_encaminhamento",
        ["encaminhamento_id"],
        schema=ESQUEMA_DA_APLICACAO,
    )


def _criar_pedido_acompanhado() -> None:
    op.create_table(
        "pedido_acompanhado",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column(
            "usuario_id",
            sa.Uuid(),
            sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("protocolo", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("usuario_id", "protocolo"),
        schema=ESQUEMA_DA_APLICACAO,
    )


def upgrade() -> None:
    _guardar_protocolo()
    _criar_encaminhamento()
    _criar_evento_de_encaminhamento()
    _criar_pedido_acompanhado()


def downgrade() -> None:
    op.drop_table("pedido_acompanhado", schema=ESQUEMA_DA_APLICACAO)
    op.drop_table("evento_de_encaminhamento", schema=ESQUEMA_DA_APLICACAO)
    op.drop_table("encaminhamento", schema=ESQUEMA_DA_APLICACAO)
    op.drop_index("ix_ouro_fato_demanda_protocolo", "fato_demanda", schema=ESQUEMA_ANALITICO)
    for tabela in TABELAS_DE_DEMANDA:
        op.drop_column(tabela, "protocolo", schema=ESQUEMA_ANALITICO)
