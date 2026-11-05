"""Cria a base analítica: dimensão de bairros, tabela fato, importações e auditoria de consultas.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA_ANALITICO = "ouro"
ESQUEMA_DA_APLICACAO = "app"

# IBGE, Censo 2022 (tabelas 9922, 9923 e 10206): nome, RPA, população, domicílios, % em favela.
BAIRROS = [
    ("AFLITOS", "Aflitos", "3", 4990, 1998, 0.0),
    ("AFOGADOS", "Afogados", "5", 31457, 11522, 28.9),
    ("AGUA FRIA", "Água Fria", "2", 39012, 13482, 17.7),
    ("ALTO DO MANDU", "Alto do Mandu", "3", 4221, 1489, 0.0),
    ("ALTO JOSE BONIFACIO", "Alto José Bonifácio", "3", 10365, 3605, 17.8),
    ("ALTO JOSE DO PINHO", "Alto José do Pinho", "3", 11313, 3945, 6.5),
    ("ALTO SANTA TEREZINHA", "Alto Santa Terezinha", "2", 6620, 2305, 100.0),
    ("APIPUCOS", "Apipucos", "3", 2523, 868, 55.4),
    ("AREIAS", "Areias", "5", 26740, 9692, 26.8),
    ("ARRUDA", "Arruda", "2", 12797, 4609, 16.8),
    ("BARRO", "Barro", "5", 30565, 10951, 22.6),
    ("BEBERIBE", "Beberibe", "2", 7089, 2603, 22.8),
    ("BOA VIAGEM", "Boa Viagem", "6", 125805, 50663, 7.9),
    ("BOA VISTA", "Boa Vista", "1", 13147, 6133, 0.0),
    ("BOMBA DO HEMETERIO", "Bomba do Hemetério", "2", 7728, 2696, 54.9),
    ("BONGI", "Bongi", "5", 7060, 2546, 3.6),
    ("BRASILIA TEIMOSA", "Brasília Teimosa", "6", 16685, 6118, 5.3),
    ("BREJO DA GUABIRABA", "Brejo da Guabiraba", "3", 10620, 3760, 15.3),
    ("BREJO DE BEBERIBE", "Brejo de Beberibe", "3", 7738, 2754, 17.0),
    ("CABANGA", "Cabanga", "1", 1831, 625, 51.9),
    ("CACOTE", "Caçote", "5", 8738, 3182, 99.9),
    ("CAJUEIRO", "Cajueiro", "2", 5062, 1862, 4.4),
    ("CAMPINA DO BARRETO", "Campina do Barreto", "2", 8757, 3093, 0.0),
    ("CAMPO GRANDE", "Campo Grande", "2", 31783, 11586, 16.3),
    ("CASA AMARELA", "Casa Amarela", "3", 32450, 12360, 0.6),
    ("CASA FORTE", "Casa Forte", "3", 6307, 2325, 0.0),
    ("CAXANGA", "Caxangá", "4", 13813, 5067, 27.9),
    ("CIDADE UNIVERSITARIA", "Cidade Universitária", "4", 1819, 675, 86.8),
    ("COELHOS", "Coelhos", "1", 5923, 2198, 33.4),
    ("COHAB", "Cohab - Ibura de Cima", "6", 62632, 21926, 35.9),
    ("COQUEIRAL", "Coqueiral", "5", 9427, 3443, 33.9),
    ("CORDEIRO", "Cordeiro", "4", 37660, 13768, 5.2),
    ("CORREGO DO JENIPAPO", "Córrego do Jenipapo", "3", 8086, 2854, 11.6),
    ("CURADO", "Curado", "5", 16559, 5916, 49.3),
    ("DERBY", "Derby", "3", 1867, 704, 0.0),
    ("DOIS IRMAOS", "Dois Irmãos", "3", 3026, 1093, 19.7),
    ("DOIS UNIDOS", "Dois Unidos", "2", 31437, 11063, 72.0),
    ("ENCRUZILHADA", "Encruzilhada", "2", 15249, 5929, 0.0),
    ("ENGENHO DO MEIO", "Engenho do Meio", "4", 9849, 3494, 1.6),
    ("ESPINHEIRO", "Espinheiro", "3", 10741, 4374, 2.8),
    ("ESTANCIA", "Estância", "5", 7408, 2719, 42.8),
    ("FUNDAO", "Fundão", "2", 7793, 2811, 14.1),
    ("GRACAS", "Graças", "3", 19694, 7944, 0.0),
    ("GUABIRABA", "Guabiraba", "3", 11095, 3934, 53.2),
    ("HIPODROMO", "Hipódromo", "2", 2091, 756, 0.0),
    ("IBURA", "Ibura", "6", 45448, 16241, 30.5),
    ("ILHA DO LEITE", "Ilha do Leite", "1", 990, 489, 0.0),
    ("ILHA DO RETIRO", "Ilha do Retiro", "4", 3946, 1408, 39.1),
    ("ILHA JOANA BEZERRA", "Ilha Joana Bezerra", "1", 12257, 4260, 50.6),
    ("IMBIRIBEIRA", "Imbiribeira", "6", 52158, 19321, 36.7),
    ("IPSEP", "Ipsep", "6", 20610, 7721, 12.3),
    ("IPUTINGA", "Iputinga", "4", 49944, 18648, 28.4),
    ("JAQUEIRA", "Jaqueira", "3", 1342, 509, 0.0),
    ("JARDIM SAO PAULO", "Jardim São Paulo", "5", 29996, 10919, 23.8),
    ("JIQUIA", "Jiquiá", "5", 12051, 4269, 57.8),
    ("JORDAO", "Jordão", "6", 20449, 7172, 46.6),
    ("LINHA DO TIRO", "Linha do Tiro", "2", 14202, 4900, 79.2),
    ("MACAXEIRA", "Macaxeira", "3", 20126, 6902, 14.6),
    ("MADALENA", "Madalena", "4", 25832, 9964, 15.8),
    ("MANGABEIRA", "Mangabeira", "3", 6397, 2348, 0.0),
    ("MANGUEIRA", "Mangueira", "5", 7664, 2815, 10.8),
    ("MONTEIRO", "Monteiro", "3", 6738, 2342, 10.0),
    ("MORRO DA CONCEICAO", "Morro da Conceição", "3", 8217, 2911, 0.0),
    ("MUSTARDINHA", "Mustardinha", "5", 10642, 3740, 0.0),
    ("NOVA DESCOBERTA", "Nova Descoberta", "3", 28697, 10267, 6.1),
    ("PAISSANDU", "Paissandu", "1", 568, 275, 0.0),
    ("PARNAMIRIM", "Parnamirim", "3", 6954, 2573, 3.1),
    ("PASSARINHO", "Passarinho", "3", 24306, 8358, 73.3),
    ("PAU FERRO", "Pau Ferro", "3", 89, 27, 0.0),
    ("PEIXINHOS", "Peixinhos", "2", 2915, 951, 7.4),
    ("PINA", "Pina", "6", 29195, 11653, 30.5),
    ("POCO", "Poço", "3", 5542, 1965, 16.7),
    ("PONTO DE PARADA", "Ponto de Parada", "2", 2382, 925, 0.0),
    ("PORTO DA MADEIRA", "Porto da Madeira", "2", 6495, 2371, 6.3),
    ("PRADO", "Prado", "4", 11412, 4193, 13.3),
    ("RECIFE", "Recife", "1", 541, 184, 0.0),
    ("ROSARINHO", "Rosarinho", "2", 7271, 2818, 13.3),
    ("SAN MARTIN", "San Martin", "5", 23074, 8273, 8.8),
    ("SANCHO", "Sancho", "5", 12768, 2599, 23.2),
    ("SANTANA", "Santana", "3", 2574, 1013, 12.5),
    ("SANTO AMARO", "Santo Amaro", "1", 27103, 10046, 53.2),
    ("SANTO ANTONIO", "Santo Antônio", "1", 447, 227, 0.0),
    ("SAO JOSE", "São José", "1", 8876, 3154, 45.4),
    ("SITIO DOS PINTOS - SAO BRAS", "Sítio dos Pintos - São Brás", "3", 7996, 2943, 43.0),
    ("SOLEDADE", "Soledade", "1", 2081, 1084, 0.0),
    ("TAMARINEIRA", "Tamarineira", "3", 13236, 5057, 0.0),
    ("TEJIPIO", "Tejipió", "5", 9835, 3748, 0.0),
    ("TORRE", "Torre", "4", 20872, 8185, 1.7),
    ("TORREAO", "Torreão", "2", 1566, 602, 0.0),
    ("TORROES", "Torrões", "4", 31130, 10986, 20.9),
    ("TOTO", "Totó", "5", 2074, 753, 0.0),
    ("VARZEA", "Várzea", "4", 70946, 26536, 47.5),
    ("VASCO DA GAMA", "Vasco da Gama", "3", 26631, 9495, 9.3),
    ("ZUMBI", "Zumbi", "4", 4763, 1881, 12.7),
]


def _colunas_da_demanda() -> list[sa.Column[object]]:
    return [
        sa.Column("chave_registro", sa.BigInteger(), nullable=False),
        sa.Column("assinatura", sa.BigInteger(), nullable=False),
        sa.Column("importacao_id", sa.Integer(), nullable=False),
        sa.Column("fonte", sa.String(30), nullable=False),
        sa.Column("ano", sa.SmallInteger()),
        sa.Column("data_abertura", sa.Date()),
        sa.Column("data_ult_movimento", sa.Date()),
        sa.Column("dias_ate_movimento", sa.Integer()),
        sa.Column("prazo_negativo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("categoria", sa.Text()),
        sa.Column("servico_codigo", sa.Text()),
        sa.Column("servico", sa.Text()),
        sa.Column("tipo_registro", sa.Text()),
        sa.Column("orgao", sa.Text()),
        sa.Column("canal_entrada", sa.Text()),
        sa.Column("bairro_oficial", sa.Text()),
        sa.Column("bairro_recuperado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rpa", sa.Text()),
        sa.Column("situacao", sa.Text()),
        sa.Column("iniciativa", sa.Text()),
        sa.Column("id_local", sa.Text()),
        sa.Column("numero_informado", sa.Boolean()),
        sa.Column("ouv_data_prazo", sa.Date()),
        sa.Column("ouv_no_prazo", sa.Boolean()),
        sa.Column("camara_data_envio_prefeitura", sa.Date()),
        sa.Column("camara_canal_envio", sa.Text()),
        sa.Column("camara_dias_ate_envio", sa.Integer()),
        sa.Column("camara_data_resposta", sa.Date()),
        sa.Column("camara_dias_ate_resposta", sa.Integer()),
        sa.Column("camara_desfecho", sa.Text()),
        sa.Column("arquivo_origem", sa.Text()),
        sa.Column("ano_do_arquivo", sa.SmallInteger()),
    ]


def _criar_importacao() -> None:
    op.create_table(
        "importacao",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("nome_do_arquivo", sa.Text(), nullable=False),
        sa.Column("tamanho_em_bytes", sa.BigInteger(), nullable=False),
        sa.Column("hash_do_arquivo", sa.String(64), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id")),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("progresso", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("fonte", sa.String(30)),
        sa.Column("layout", sa.String(30)),
        sa.Column("data_do_retrato", sa.Date()),
        sa.Column("periodo_inicio", sa.Date()),
        sa.Column("periodo_fim", sa.Date()),
        sa.Column("carga_inicial", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("arquivo_guardado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("estrutura", postgresql.JSONB()),
        sa.Column("decisoes", postgresql.JSONB()),
        sa.Column("pendencias", postgresql.JSONB()),
        sa.Column("resultado", postgresql.JSONB()),
        sa.Column("mensagem_de_erro", sa.Text()),
        sa.Column("criada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("concluida_em", sa.DateTime(timezone=True)),
        sa.Column("desfeita_em", sa.DateTime(timezone=True)),
        sa.Column("desfeita_por", sa.Uuid(), sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id")),
        schema=ESQUEMA_DA_APLICACAO,
    )
    op.create_index(
        "ix_app_importacao_hash_do_arquivo",
        "importacao",
        ["hash_do_arquivo"],
        schema=ESQUEMA_DA_APLICACAO,
    )


def _criar_consulta_auditada() -> None:
    op.create_table(
        "consulta_auditada",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "usuario_id",
            sa.Uuid(),
            sa.ForeignKey(f"{ESQUEMA_DA_APLICACAO}.usuario.id"),
            nullable=False,
        ),
        sa.Column("rota", sa.Text(), nullable=False),
        sa.Column("filtros", postgresql.JSONB(), nullable=False),
        sa.Column("ocorrida_em", sa.DateTime(timezone=True), nullable=False),
        schema=ESQUEMA_DA_APLICACAO,
    )
    op.create_index(
        "ix_app_consulta_auditada_ocorrida_em",
        "consulta_auditada",
        ["ocorrida_em"],
        schema=ESQUEMA_DA_APLICACAO,
    )


def _criar_dim_bairro() -> None:
    tabela = op.create_table(
        "dim_bairro",
        sa.Column("bairro_oficial", sa.Text(), primary_key=True),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("rpa", sa.Text(), nullable=False),
        sa.Column("populacao", sa.Integer(), nullable=False),
        sa.Column("domicilios", sa.Integer(), nullable=False),
        sa.Column("pct_favela", sa.Float(), nullable=False),
        schema=ESQUEMA_ANALITICO,
    )
    colunas = ("bairro_oficial", "nome", "rpa", "populacao", "domicilios", "pct_favela")
    op.bulk_insert(tabela, [dict(zip(colunas, bairro, strict=True)) for bairro in BAIRROS])


def _criar_tabelas_de_demanda() -> None:
    op.create_table(
        "fato_demanda",
        *_colunas_da_demanda(),
        sa.PrimaryKeyConstraint("chave_registro"),
        sa.ForeignKeyConstraint(["importacao_id"], [f"{ESQUEMA_DA_APLICACAO}.importacao.id"]),
        schema=ESQUEMA_ANALITICO,
    )
    op.create_index(
        "ix_ouro_fato_demanda_importacao_id",
        "fato_demanda",
        ["importacao_id"],
        schema=ESQUEMA_ANALITICO,
    )
    op.create_table(
        "fato_demanda_substituida",
        sa.Column("substituida_por", sa.Integer(), nullable=False),
        *_colunas_da_demanda(),
        sa.PrimaryKeyConstraint("substituida_por", "chave_registro"),
        sa.ForeignKeyConstraint(["substituida_por"], [f"{ESQUEMA_DA_APLICACAO}.importacao.id"]),
        schema=ESQUEMA_ANALITICO,
    )


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {ESQUEMA_ANALITICO}")
    _criar_importacao()
    _criar_consulta_auditada()
    _criar_dim_bairro()
    _criar_tabelas_de_demanda()


def downgrade() -> None:
    op.drop_table("fato_demanda_substituida", schema=ESQUEMA_ANALITICO)
    op.drop_table("fato_demanda", schema=ESQUEMA_ANALITICO)
    op.drop_table("dim_bairro", schema=ESQUEMA_ANALITICO)
    op.drop_table("consulta_auditada", schema=ESQUEMA_DA_APLICACAO)
    op.drop_table("importacao", schema=ESQUEMA_DA_APLICACAO)
    op.execute(f"DROP SCHEMA IF EXISTS {ESQUEMA_ANALITICO}")
