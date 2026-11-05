"""Cria as views materializadas que alimentam as telas do painel.

O SQL reproduz as tabelas agregadas do protótipo em Streamlit (`pipeline/agregados.py`).
As constantes de janela vêm de docs/dados.md. Cada view nasce vazia: a carga as preenche.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-05
"""

from collections.abc import Sequence
from dataclasses import dataclass

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


@dataclass(frozen=True)
class View:
    nome: str
    consulta: str
    chave_unica: tuple[str, ...]
    indices: tuple[str, ...] = ()


VW_REFERENCIA = """
CREATE VIEW ouro.vw_referencia AS
SELECT
    coalesce(max(data_do_retrato), current_date) AS data_referencia,
    greatest(
        DATE '2026-05-31',
        coalesce(max(periodo_fim) FILTER (WHERE NOT carga_inicial), DATE '2026-05-31')
    ) AS fim_da_simulacao,
    DATE '2022-01-01' AS inicio_da_simulacao,
    extract(year FROM coalesce(max(data_do_retrato), current_date))::int AS ano_maximo
FROM app.importacao
WHERE status IN ('CONCLUIDA', 'ATUALIZANDO_PAINEL')
"""

BASE_REINCIDENCIA = """
    SELECT
        chave_registro, ano, rpa, bairro_oficial, categoria, servico, data_abertura, id_local,
        servico_codigo,
        count(*) OVER (PARTITION BY id_local, servico_codigo) AS pedidos_no_local,
        data_abertura - lag(data_abertura) OVER (
            PARTITION BY id_local, servico_codigo ORDER BY data_abertura, chave_registro
        ) AS intervalo
    FROM ouro.fato_demanda
    WHERE fonte = '156_EMLURB' AND ano BETWEEN 2015 AND 2025 AND numero_informado
"""

ABERTO_RECENTE_156 = """
    f.situacao IS DISTINCT FROM 'ATENDIDA'
    AND f.ano_do_arquivo >= (
        SELECT primeiro_ano_recente FROM ouro.mv_referencia_por_fonte r WHERE r.fonte = f.fonte
    )
"""

ABERTA_RECENTE_OUVIDORIA = """
    f.situacao = 'ABERTO'
    AND f.ano_do_arquivo >= (
        SELECT primeiro_ano_recente FROM ouro.mv_referencia_por_fonte r WHERE r.fonte = f.fonte
    )
"""

VIEWS = (
    View(
        "mv_referencia_por_fonte",
        """
        SELECT fonte, max(ano_do_arquivo) - 1 AS primeiro_ano_recente
        FROM ouro.fato_demanda
        GROUP BY fonte
        """,
        ("fonte",),
    ),
    View(
        "mv_prazo_tipico_156",
        """
        SELECT
            categoria,
            percentile_cont(0.9) WITHIN GROUP (ORDER BY dias_ate_movimento) AS prazo_tipico_dias
        FROM ouro.fato_demanda
        WHERE fonte = '156_EMLURB' AND ano BETWEEN 2021 AND 2025 AND situacao = 'ATENDIDA'
            AND dias_ate_movimento IS NOT NULL AND categoria IS NOT NULL
        GROUP BY categoria
        """,
        ("categoria",),
    ),
    View(
        "mv_demanda",
        """
        SELECT
            fonte, ano, coalesce(extract(month FROM data_abertura)::int, 0) AS mes,
            rpa, bairro_oficial, categoria, iniciativa, count(*)::int AS n
        FROM ouro.fato_demanda
        WHERE ano BETWEEN 2012 AND (SELECT ano_maximo FROM ouro.vw_referencia)
        GROUP BY 1, 2, 3, 4, 5, 6, 7
        """,
        ("fonte", "ano", "mes", "rpa", "bairro_oficial", "categoria", "iniciativa"),
        ("ano", "fonte"),
    ),
    View(
        "mv_prazos_156",
        """
        SELECT ano, rpa, bairro_oficial, categoria, dias_ate_movimento AS dias, count(*)::int AS n
        FROM ouro.fato_demanda
        WHERE fonte = '156_EMLURB'
            AND ano BETWEEN 2012 AND (SELECT ano_maximo FROM ouro.vw_referencia)
            AND situacao = 'ATENDIDA' AND dias_ate_movimento IS NOT NULL
        GROUP BY 1, 2, 3, 4, 5
        """,
        ("ano", "rpa", "bairro_oficial", "categoria", "dias"),
        ("ano",),
    ),
    View(
        "mv_reincidencia_156",
        f"""
        WITH base AS ({BASE_REINCIDENCIA}),
        chaves AS (SELECT DISTINCT id_local, servico_codigo, pedidos_no_local FROM base),
        limite AS (
            SELECT percentile_cont(0.99) WITHIN GROUP (ORDER BY pedidos_no_local) AS valor
            FROM chaves
        )
        SELECT
            base.ano, base.rpa, base.bairro_oficial, base.categoria,
            count(*)::int AS registros,
            (count(*) FILTER (WHERE pedidos_no_local >= 2))::int AS repetidos,
            (count(*) FILTER (
                WHERE pedidos_no_local >= 2 AND pedidos_no_local > limite.valor
            ))::int AS repetidos_local_generico,
            (count(*) FILTER (WHERE intervalo <= 7))::int AS intervalo_duplicidade,
            (count(*) FILTER (WHERE intervalo BETWEEN 8 AND 29))::int AS intervalo_intermediario,
            (count(*) FILTER (WHERE intervalo >= 30))::int AS intervalo_reincidencia
        FROM base CROSS JOIN limite
        GROUP BY 1, 2, 3, 4
        """,
        ("ano", "rpa", "bairro_oficial", "categoria"),
        ("ano",),
    ),
    View(
        "mv_locais_cronicos_156",
        f"""
        WITH base AS ({BASE_REINCIDENCIA}),
        locais AS (
            SELECT
                (array_agg(bairro_oficial ORDER BY data_abertura, chave_registro)
                    FILTER (WHERE bairro_oficial IS NOT NULL))[1] AS bairro_oficial,
                (array_agg(rpa ORDER BY data_abertura, chave_registro)
                    FILTER (WHERE rpa IS NOT NULL))[1] AS rpa,
                (array_agg(categoria ORDER BY data_abertura, chave_registro)
                    FILTER (WHERE categoria IS NOT NULL))[1] AS categoria,
                (array_agg(servico ORDER BY data_abertura, chave_registro)
                    FILTER (WHERE servico IS NOT NULL))[1] AS servico,
                count(*)::int AS pedidos,
                min(ano)::int AS primeiro_ano,
                max(ano)::int AS ultimo_ano,
                count(DISTINCT data_abertura)::int AS dias_distintos
            FROM base
            WHERE pedidos_no_local >= 5
            GROUP BY id_local, servico_codigo
        )
        SELECT row_number() OVER (ORDER BY pedidos DESC, dias_distintos DESC) AS posicao, locais.*
        FROM locais
        """,
        ("posicao",),
        ("pedidos",),
    ),
    View(
        "mv_camara_indicacoes",
        """
        SELECT
            chave_registro, ano, rpa, bairro_oficial, bairro_recuperado, categoria, orgao,
            camara_canal_envio AS canal_envio,
            camara_desfecho AS desfecho,
            camara_data_envio_prefeitura IS NOT NULL AS enviada,
            camara_data_resposta IS NOT NULL AS respondida,
            camara_dias_ate_envio AS dias_ate_envio,
            camara_dias_ate_resposta AS dias_ate_resposta
        FROM ouro.fato_demanda
        WHERE fonte = 'CAMARA_REQUERIMENTOS' AND tipo_registro = 'INDICACAO'
        """,
        ("chave_registro",),
        ("ano",),
    ),
    View(
        "mv_ouvidoria",
        """
        SELECT
            ano, orgao, tipo_registro AS natureza, canal_entrada,
            ouv_no_prazo AS no_prazo, count(*)::int AS n
        FROM ouro.fato_demanda
        WHERE fonte = 'OUVIDORIA'
        GROUP BY 1, 2, 3, 4, 5
        """,
        ("ano", "orgao", "natureza", "canal_entrada", "no_prazo"),
        ("ano",),
    ),
    View(
        "mv_linha_do_tempo_156",
        f"""
        WITH anteriores AS (
            SELECT
                chave_registro,
                rank() OVER (
                    PARTITION BY id_local, servico_codigo ORDER BY data_abertura
                ) - 1 AS pedidos_anteriores
            FROM ouro.fato_demanda
            WHERE fonte = '156_EMLURB' AND numero_informado AND id_local IS NOT NULL
                AND data_abertura IS NOT NULL
        )
        SELECT
            f.chave_registro,
            f.data_abertura,
            CASE
                WHEN f.situacao = 'ATENDIDA' THEN f.data_ult_movimento
            END AS data_fim,
            f.rpa, f.bairro_oficial, f.categoria, f.servico, f.situacao,
            p.prazo_tipico_dias,
            a.pedidos_anteriores::int AS pedidos_anteriores
        FROM ouro.fato_demanda f
        LEFT JOIN ouro.mv_prazo_tipico_156 p USING (categoria)
        LEFT JOIN anteriores a USING (chave_registro)
        WHERE f.fonte = '156_EMLURB' AND (
            (f.situacao = 'ATENDIDA' AND f.data_ult_movimento >= DATE '2022-01-01')
            OR ({ABERTO_RECENTE_156})
        )
        """,
        ("chave_registro",),
        ("data_abertura", "data_fim", "bairro_oficial"),
    ),
    View(
        "mv_linha_do_tempo_camara",
        """
        WITH indicacoes AS (
            SELECT * FROM ouro.fato_demanda
            WHERE fonte = 'CAMARA_REQUERIMENTOS' AND tipo_registro = 'INDICACAO'
        ),
        respondidas AS (
            SELECT categoria, camara_dias_ate_resposta AS dias
            FROM indicacoes
            WHERE camara_data_resposta IS NOT NULL AND camara_dias_ate_resposta IS NOT NULL
        ),
        por_tema AS (
            SELECT categoria, percentile_cont(0.9) WITHIN GROUP (ORDER BY dias) AS prazo
            FROM respondidas
            GROUP BY categoria
            HAVING count(*) >= 30
        ),
        geral AS (
            SELECT percentile_cont(0.9) WITHIN GROUP (ORDER BY dias) AS prazo FROM respondidas
        ),
        repeticao AS (
            SELECT
                chave_registro,
                count(*) OVER (
                    PARTITION BY bairro_oficial, categoria
                    ORDER BY data_abertura
                    RANGE BETWEEN INTERVAL '90 days' PRECEDING AND INTERVAL '1 day' PRECEDING
                ) AS anteriores
            FROM indicacoes
            WHERE bairro_oficial IS NOT NULL
        )
        SELECT
            i.chave_registro,
            i.data_abertura,
            i.camara_data_envio_prefeitura AS data_envio,
            i.camara_data_resposta AS data_resposta,
            i.rpa, i.bairro_oficial, i.categoria, i.orgao,
            i.camara_canal_envio AS canal_envio,
            coalesce(t.prazo, g.prazo) AS prazo_tipico_dias,
            r.anteriores::int AS pedidos_anteriores
        FROM indicacoes i
        CROSS JOIN geral g
        LEFT JOIN por_tema t USING (categoria)
        LEFT JOIN repeticao r USING (chave_registro)
        WHERE i.camara_data_envio_prefeitura IS NOT NULL
            AND i.camara_desfecho IN (
                'ENVIADO, SEM RESPOSTA REGISTRADA', 'ENVIADO E COM RESPOSTA REGISTRADA'
            )
            AND (i.camara_data_resposta IS NULL OR i.camara_data_resposta >= DATE '2022-01-01')
        """,
        ("chave_registro",),
        ("data_envio", "data_resposta"),
    ),
    View(
        "mv_linha_do_tempo_ouvidoria",
        f"""
        SELECT
            f.chave_registro,
            f.data_abertura,
            f.ouv_data_prazo AS data_prazo,
            CASE WHEN f.situacao = 'CONCLUIDO' THEN f.data_ult_movimento END AS data_fim,
            f.orgao,
            f.servico AS assunto,
            f.tipo_registro AS natureza,
            f.canal_entrada
        FROM ouro.fato_demanda f
        WHERE f.fonte = 'OUVIDORIA' AND (
            (f.situacao = 'CONCLUIDO' AND f.data_ult_movimento >= DATE '2022-01-01')
            OR ({ABERTA_RECENTE_OUVIDORIA})
        )
        """,
        ("chave_registro",),
        ("data_abertura", "data_fim"),
    ),
    View(
        "mv_fluxo_diario_156",
        """
        WITH movimentos AS (
            SELECT data_abertura AS data, categoria, bairro_oficial, 1 AS entrou, 0 AS atendeu
            FROM ouro.fato_demanda
            WHERE fonte = '156_EMLURB' AND data_abertura IS NOT NULL
            UNION ALL
            SELECT data_ult_movimento, categoria, bairro_oficial, 0, 1
            FROM ouro.fato_demanda
            WHERE fonte = '156_EMLURB' AND situacao = 'ATENDIDA'
                AND data_ult_movimento IS NOT NULL
        )
        SELECT
            m.data, m.categoria, m.bairro_oficial,
            sum(m.entrou)::int AS entradas,
            sum(m.atendeu)::int AS atendidos
        FROM movimentos m
        CROSS JOIN ouro.vw_referencia r
        WHERE m.data BETWEEN r.inicio_da_simulacao AND r.fim_da_simulacao
        GROUP BY 1, 2, 3
        """,
        ("data", "categoria", "bairro_oficial"),
        ("data",),
    ),
    View(
        "mv_entradas_diarias",
        """
        SELECT f.fonte, f.data_abertura AS data, count(*)::int AS n
        FROM ouro.fato_demanda f
        CROSS JOIN ouro.vw_referencia r
        WHERE f.data_abertura BETWEEN r.inicio_da_simulacao AND r.fim_da_simulacao
        GROUP BY 1, 2
        """,
        ("fonte", "data"),
        ("data",),
    ),
    View(
        "mv_indicadores_bairro",
        """
        WITH bairros AS (SELECT * FROM ouro.dim_bairro WHERE populacao >= 1000),
        contagens AS (
            SELECT
                bairro_oficial,
                count(*) FILTER (
                    WHERE fonte = '156_EMLURB' AND ano BETWEEN 2021 AND 2025
                ) AS pedidos_156,
                count(*) FILTER (
                    WHERE fonte = 'DEFESA_CIVIL' AND iniciativa = 'CIDADAO'
                        AND ano BETWEEN 2021 AND 2024
                ) AS acoes_defesa_civil,
                count(*) FILTER (
                    WHERE fonte = 'SEDEC_CHAMADOS' AND ano BETWEEN 2021 AND 2023
                ) AS chamados_sedec,
                count(*) FILTER (
                    WHERE fonte = 'CAMARA_REQUERIMENTOS' AND tipo_registro = 'INDICACAO'
                        AND ano BETWEEN 2021 AND 2025
                ) AS indicacoes
            FROM ouro.fato_demanda
            WHERE bairro_oficial IS NOT NULL
            GROUP BY bairro_oficial
        ),
        prazos AS (
            SELECT
                bairro_oficial,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY dias_ate_movimento) AS mediana
            FROM ouro.fato_demanda
            WHERE fonte = '156_EMLURB' AND ano BETWEEN 2021 AND 2025 AND situacao = 'ATENDIDA'
                AND dias_ate_movimento > 0
            GROUP BY bairro_oficial
        ),
        com_numero AS (
            SELECT
                bairro_oficial,
                count(*) OVER (PARTITION BY id_local, servico_codigo) >= 2 AS repetido
            FROM ouro.fato_demanda
            WHERE fonte = '156_EMLURB' AND ano BETWEEN 2021 AND 2025 AND numero_informado
        ),
        reincidencia AS (
            SELECT bairro_oficial, avg(repetido::int) * 100 AS pct
            FROM com_numero
            GROUP BY bairro_oficial
        ),
        estoque AS (
            SELECT
                t.bairro_oficial,
                count(*) AS abertos,
                count(*) FILTER (
                    WHERE r.data_referencia - t.data_abertura > t.prazo_tipico_dias
                ) AS atrasados
            FROM ouro.mv_linha_do_tempo_156 t
            CROSS JOIN ouro.vw_referencia r
            WHERE t.data_fim IS NULL
            GROUP BY t.bairro_oficial
        )
        SELECT
            b.bairro_oficial, b.nome, b.rpa, b.populacao, b.pct_favela,
            c.pedidos_156 / 5.0 / b.populacao * 1000 AS taxa_156,
            coalesce(c.acoes_defesa_civil, 0) / 4.0 / b.populacao * 1000 AS taxa_defesa_civil,
            coalesce(c.chamados_sedec, 0) / 3.0 / b.populacao * 1000 AS taxa_sedec,
            coalesce(c.indicacoes, 0) / 5.0 / b.populacao * 10000 AS taxa_indicacoes,
            p.mediana AS mediana_dias_156,
            r.pct AS pct_reincidencia_156,
            coalesce(e.abertos, 0)::int AS abertos_156,
            e.atrasados::float / nullif(e.abertos, 0) * 100 AS pct_atraso_156
        FROM bairros b
        LEFT JOIN contagens c USING (bairro_oficial)
        LEFT JOIN prazos p USING (bairro_oficial)
        LEFT JOIN reincidencia r USING (bairro_oficial)
        LEFT JOIN estoque e USING (bairro_oficial)
        """,
        ("bairro_oficial",),
    ),
    View(
        "mv_vocabulario",
        """
        SELECT fonte, campo, valor, count(*)::int AS n
        FROM ouro.fato_demanda f
        CROSS JOIN LATERAL (
            VALUES
                ('categoria', f.categoria),
                ('situacao', f.situacao),
                ('orgao', f.orgao),
                ('tipo_registro', f.tipo_registro),
                ('canal_entrada', f.canal_entrada),
                ('iniciativa', f.iniciativa)
        ) AS v (campo, valor)
        WHERE valor IS NOT NULL
        GROUP BY 1, 2, 3
        """,
        ("fonte", "campo", "valor"),
    ),
)


def _criar_view(view: View) -> None:
    op.execute(f"CREATE MATERIALIZED VIEW ouro.{view.nome} AS {view.consulta} WITH NO DATA")
    colunas = ", ".join(view.chave_unica)
    op.execute(
        f"CREATE UNIQUE INDEX ux_{view.nome} ON ouro.{view.nome} ({colunas}) NULLS NOT DISTINCT"
    )
    for coluna in view.indices:
        op.execute(f"CREATE INDEX ix_{view.nome}_{coluna} ON ouro.{view.nome} ({coluna})")


def upgrade() -> None:
    op.execute(VW_REFERENCIA)
    for view in VIEWS:
        _criar_view(view)


def downgrade() -> None:
    for view in reversed(VIEWS):
        op.execute(f"DROP MATERIALIZED VIEW ouro.{view.nome}")
    op.execute("DROP VIEW ouro.vw_referencia")
