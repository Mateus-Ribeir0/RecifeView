"""Cria o acesso corporativo dos órgãos, as notificações e o que o mesmo problema precisa.

A conta corporativa guarda o órgão; o convite guarda só o hash do token do link. O
encaminhamento passa a guardar o pseudônimo do local e o código do serviço, para comparar
encaminhamentos pela regra do pente fino, e o evento ganha a resposta ao cidadão e a previsão
(ADR 0013). A view por órgão alimenta a tela "Dados do órgão" sem varrer a tabela fato.

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA = "app"
ESQUEMA_ANALITICO = "ouro"
USUARIO = f"{ESQUEMA}.usuario.id"

PREENCHER_COMPARACAO = """
UPDATE app.encaminhamento e
SET servico_codigo = f.servico_codigo,
    id_local = f.id_local,
    numero_informado = f.numero_informado
FROM ouro.fato_demanda f
WHERE f.chave_registro = e.chave_registro
"""
DEMANDA_POR_ORGAO = """
CREATE MATERIALIZED VIEW ouro.mv_demanda_por_orgao AS
SELECT
    fonte, ano, upper(trim(orgao)) AS orgao_na_fonte, bairro_oficial, categoria, situacao,
    count(*)::int AS n
FROM ouro.fato_demanda
WHERE orgao IS NOT NULL AND trim(orgao) <> ''
    AND iniciativa IS DISTINCT FROM 'PROATIVA'
    AND ano BETWEEN 2012 AND (SELECT ano_maximo FROM ouro.vw_referencia)
GROUP BY 1, 2, 3, 4, 5, 6
"""


def _criar_convite() -> None:
    op.create_table(
        "convite_de_acesso",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "usuario_id", sa.Uuid(), sa.ForeignKey(USUARIO, ondelete="CASCADE"), nullable=False
        ),
        sa.Column("hash_do_token", sa.String(64), nullable=False, unique=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado_em", sa.DateTime(timezone=True)),
        sa.Column("criado_por", sa.Uuid(), sa.ForeignKey(USUARIO)),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_app_convite_de_acesso_usuario_id", "convite_de_acesso", ["usuario_id"], schema=ESQUEMA
    )


def _criar_notificacao() -> None:
    op.create_table(
        "notificacao",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "usuario_id", sa.Uuid(), sa.ForeignKey(USUARIO, ondelete="CASCADE"), nullable=False
        ),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("caminho", sa.Text(), nullable=False),
        sa.Column(
            "criada_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("lida_em", sa.DateTime(timezone=True)),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_app_notificacao_usuario_id_criada_em",
        "notificacao",
        ["usuario_id", "criada_em"],
        schema=ESQUEMA,
    )


def _guardar_comparacao_no_encaminhamento() -> None:
    op.add_column("encaminhamento", sa.Column("servico_codigo", sa.Text()), schema=ESQUEMA)
    op.add_column("encaminhamento", sa.Column("id_local", sa.Text()), schema=ESQUEMA)
    op.add_column("encaminhamento", sa.Column("numero_informado", sa.Boolean()), schema=ESQUEMA)
    op.execute(PREENCHER_COMPARACAO)
    op.add_column(
        "evento_de_encaminhamento", sa.Column("resposta_ao_cidadao", sa.Text()), schema=ESQUEMA
    )
    op.add_column("evento_de_encaminhamento", sa.Column("previsao", sa.Date()), schema=ESQUEMA)


def _indexar_local_na_base() -> None:
    op.create_index(
        "ix_ouro_fato_demanda_local",
        "fato_demanda",
        ["fonte", "id_local", "categoria", "data_abertura"],
        schema=ESQUEMA_ANALITICO,
        postgresql_where=sa.text("id_local IS NOT NULL"),
    )


def _criar_demanda_por_orgao() -> None:
    op.execute(DEMANDA_POR_ORGAO)
    op.execute(
        "CREATE UNIQUE INDEX ux_mv_demanda_por_orgao ON ouro.mv_demanda_por_orgao "
        "(fonte, ano, orgao_na_fonte, bairro_oficial, categoria, situacao) NULLS NOT DISTINCT"
    )
    op.execute(
        "CREATE INDEX ix_mv_demanda_por_orgao_orgao_na_fonte "
        "ON ouro.mv_demanda_por_orgao (orgao_na_fonte)"
    )


def upgrade() -> None:
    op.add_column("usuario", sa.Column("orgao", sa.String(30)), schema=ESQUEMA)
    _criar_convite()
    _criar_notificacao()
    _guardar_comparacao_no_encaminhamento()
    _indexar_local_na_base()
    _criar_demanda_por_orgao()


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW ouro.mv_demanda_por_orgao")
    op.drop_index("ix_ouro_fato_demanda_local", "fato_demanda", schema=ESQUEMA_ANALITICO)
    op.drop_column("evento_de_encaminhamento", "previsao", schema=ESQUEMA)
    op.drop_column("evento_de_encaminhamento", "resposta_ao_cidadao", schema=ESQUEMA)
    for coluna in ("numero_informado", "id_local", "servico_codigo"):
        op.drop_column("encaminhamento", coluna, schema=ESQUEMA)
    op.drop_table("notificacao", schema=ESQUEMA)
    op.drop_table("convite_de_acesso", schema=ESQUEMA)
    op.drop_column("usuario", "orgao", schema=ESQUEMA)
