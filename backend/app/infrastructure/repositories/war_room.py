from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.fontes import Fonte
from app.domain.prioridade import Ocorrencia
from app.domain.war_room import (
    DIAS_SIMULADOS,
    MAIS_ENTRADAS_DO_DIA,
    SEGUNDOS_POR_DIA,
    AlemDoPrazoDaOuvidoria,
    CalendarioDaWarRoom,
    DiaDaSerie,
    EntradaPorCategoria,
    EntradasDoDia,
    SemRespostaDaCamara,
)

CALENDARIO = """
SELECT
    r.data_referencia,
    (SELECT min(data) FROM ouro.mv_fluxo_diario_156),
    (SELECT max(data) FROM ouro.mv_fluxo_diario_156),
    (SELECT max(data_abertura) FROM ouro.mv_linha_do_tempo_156),
    (SELECT max(data_abertura) FROM ouro.mv_linha_do_tempo_ouvidoria)
FROM ouro.vw_referencia r
"""
ABERTOS_DO_156 = """
SELECT
    data_abertura, :dia - data_abertura, prazo_tipico_dias, pedidos_anteriores, bairro_oficial,
    rpa, categoria, servico, situacao
FROM ouro.mv_linha_do_tempo_156
WHERE data_abertura <= :dia AND (data_fim IS NULL OR data_fim > :dia)
"""
ENTRADAS_DO_DIA = """
SELECT sum(entradas)::int, sum(atendidos)::int FROM ouro.mv_fluxo_diario_156 WHERE data = :dia
"""
MEDIA_DO_DIA_DA_SEMANA = """
WITH por_dia AS (
    SELECT data, sum(entradas) AS entradas FROM ouro.mv_fluxo_diario_156 GROUP BY data
)
SELECT avg(entradas)::float FROM por_dia
WHERE extract(isodow FROM data) = extract(isodow FROM CAST(:dia AS date))
"""
OUTRAS_PORTAS = "SELECT fonte, n FROM ouro.mv_entradas_diarias WHERE data = :dia"
SERIE = """
SELECT data, sum(entradas)::int, sum(atendidos)::int
FROM ouro.mv_fluxo_diario_156
WHERE data BETWEEN :inicio AND :fim
GROUP BY data ORDER BY data
"""
SEM_RESPOSTA_DA_CAMARA = """
WITH abertas AS (
    SELECT categoria, :dia - data_envio AS idade
    FROM ouro.mv_linha_do_tempo_camara
    WHERE data_envio <= :dia AND (data_resposta IS NULL OR data_resposta > :dia)
)
SELECT
    count(*)::int,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY idade),
    (SELECT categoria FROM abertas WHERE categoria IS NOT NULL
        GROUP BY categoria ORDER BY count(*) DESC, categoria LIMIT 1),
    (SELECT count(*) FROM abertas WHERE categoria IS NOT NULL
        GROUP BY categoria ORDER BY count(*) DESC, categoria LIMIT 1)
FROM abertas
"""
ALEM_DO_PRAZO_DA_OUVIDORIA = """
WITH atrasadas AS (
    SELECT orgao, :dia - data_prazo AS dias
    FROM ouro.mv_linha_do_tempo_ouvidoria
    WHERE data_abertura <= :dia AND (data_fim IS NULL OR data_fim > :dia) AND data_prazo < :dia
)
SELECT
    count(*)::int,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY dias),
    (SELECT orgao FROM atrasadas WHERE orgao IS NOT NULL
        GROUP BY orgao ORDER BY count(*) DESC, orgao LIMIT 1),
    (SELECT count(*) FROM atrasadas WHERE orgao IS NOT NULL
        GROUP BY orgao ORDER BY count(*) DESC, orgao LIMIT 1)
FROM atrasadas
"""
COLUNAS_DA_ENTRADA = {"categoria": "categoria", "bairro_oficial": "bairro_oficial"}


class WarRoomRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def calendario(self) -> CalendarioDaWarRoom:
        hoje, primeiro, ultimo, ultimo_156, ultimo_ouvidoria = self._sessao.execute(
            text(CALENDARIO)
        ).one()
        return CalendarioDaWarRoom(
            hoje,
            primeiro or hoje,
            ultimo or hoje,
            ultimo_156,
            ultimo_ouvidoria,
            SEGUNDOS_POR_DIA,
            DIAS_SIMULADOS,
        )

    def abertos_156(self, dia: date) -> list[Ocorrencia]:
        linhas = self._sessao.execute(text(ABERTOS_DO_156), {"dia": dia})
        return [Ocorrencia(*linha) for linha in linhas]

    def entradas_do_dia(self, dia: date) -> EntradasDoDia | None:
        entradas, atendidos = self._sessao.execute(text(ENTRADAS_DO_DIA), {"dia": dia}).one()
        if entradas is None:
            return None
        media = self._sessao.scalar(text(MEDIA_DO_DIA_DA_SEMANA), {"dia": dia}) or 0.0
        linhas = self._sessao.execute(text(OUTRAS_PORTAS), {"dia": dia})
        portas: dict[str, int] = {fonte: n for fonte, n in linhas}
        return EntradasDoDia(
            entradas,
            atendidos,
            media,
            portas.get(Fonte.CAMARA.value, 0),
            portas.get(Fonte.OUVIDORIA.value, 0),
            portas.get(Fonte.DEFESA_CIVIL.value, 0),
        )

    def serie(self, inicio: date, fim: date) -> list[DiaDaSerie]:
        linhas = self._sessao.execute(text(SERIE), {"inicio": inicio, "fim": fim})
        por_dia = {
            data: DiaDaSerie(data, entradas, atendidos) for data, entradas, atendidos in linhas
        }
        dias = (fim - inicio).days + 1
        calendario = [inicio + timedelta(days=indice) for indice in range(dias)]
        return [por_dia.get(data, DiaDaSerie(data, 0, 0)) for data in calendario]

    def sem_resposta_da_camara(self, dia: date) -> SemRespostaDaCamara:
        total, mediana, tema, quantidade = self._sessao.execute(
            text(SEM_RESPOSTA_DA_CAMARA), {"dia": dia}
        ).one()
        return SemRespostaDaCamara(total, mediana, tema, quantidade or 0)

    def alem_do_prazo_da_ouvidoria(self, dia: date) -> AlemDoPrazoDaOuvidoria:
        total, mediana, orgao, quantidade = self._sessao.execute(
            text(ALEM_DO_PRAZO_DA_OUVIDORIA), {"dia": dia}
        ).one()
        return AlemDoPrazoDaOuvidoria(total, mediana, orgao, quantidade or 0)

    def mais_entradas(self, dia: date, coluna: str) -> list[EntradaPorCategoria]:
        nome = COLUNAS_DA_ENTRADA[coluna]
        consulta = f"""
        SELECT {nome}, sum(entradas)::int AS n
        FROM ouro.mv_fluxo_diario_156
        WHERE data = :dia AND entradas > 0 AND {nome} IS NOT NULL
        GROUP BY {nome} ORDER BY n DESC, {nome} LIMIT :limite
        """
        parametros = {"dia": dia, "limite": MAIS_ENTRADAS_DO_DIA}
        return [
            EntradaPorCategoria(*linha)
            for linha in self._sessao.execute(text(consulta), parametros)
        ]
