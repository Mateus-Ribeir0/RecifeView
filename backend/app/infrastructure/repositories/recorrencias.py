from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.filtros import Filtros
from app.domain.recorrencias import (
    PEDIDOS_DE_UM_PONTO_CRONICO,
    PONTOS_CRONICOS_LISTADOS,
    IntervalosDeRepeticao,
    PontoCronico,
    RecorrenciaPorCategoria,
)
from app.infrastructure.repositories.recorte import (
    Recorte,
    por_categoria,
    por_territorio,
    recorte_completo,
)


def _coluna_de_repetidos(sem_generico: bool) -> str:
    if sem_generico:
        return "sum(repetidos - repetidos_local_generico)"
    return "sum(repetidos)"


def _recorte_de_pontos(filtros: Filtros) -> Recorte:
    periodo = Recorte(
        ("ultimo_ano >= :ano_inicio", "primeiro_ano <= :ano_fim"),
        {"ano_inicio": filtros.ano_inicio, "ano_fim": filtros.ano_fim},
    )
    return periodo.com(por_territorio(filtros), por_categoria(filtros))


class RecorrenciaRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def por_categoria(self, filtros: Filtros, sem_generico: bool) -> list[RecorrenciaPorCategoria]:
        recorte = recorte_completo(filtros)
        consulta = f"""
        SELECT
            categoria, sum(registros)::int, {_coluna_de_repetidos(sem_generico)}::int,
            sum(intervalo_duplicidade)::int, sum(intervalo_intermediario)::int,
            sum(intervalo_reincidencia)::int
        FROM ouro.mv_reincidencia_156 {recorte.onde}
        GROUP BY categoria
        """
        linhas = self._sessao.execute(text(consulta), recorte.parametros)
        return [
            RecorrenciaPorCategoria(
                categoria,
                pedidos,
                repetidos,
                repetidos / pedidos * 100 if pedidos else 0.0,
                IntervalosDeRepeticao(duplicidade, intermediario, reincidencia),
            )
            for categoria, pedidos, repetidos, duplicidade, intermediario, reincidencia in linhas
            if categoria is not None
        ]

    def totais(
        self, filtros: Filtros, sem_generico: bool
    ) -> tuple[int, int, IntervalosDeRepeticao]:
        recorte = recorte_completo(filtros)
        consulta = f"""
        SELECT
            coalesce(sum(registros), 0)::int,
            coalesce({_coluna_de_repetidos(sem_generico)}, 0)::int,
            coalesce(sum(intervalo_duplicidade), 0)::int,
            coalesce(sum(intervalo_intermediario), 0)::int,
            coalesce(sum(intervalo_reincidencia), 0)::int
        FROM ouro.mv_reincidencia_156 {recorte.onde}
        """
        pedidos, repetidos, *intervalos = self._sessao.execute(
            text(consulta), recorte.parametros
        ).one()
        return pedidos, repetidos, IntervalosDeRepeticao(*intervalos)

    def contar_pontos_cronicos(self, filtros: Filtros) -> int:
        recorte = _recorte_de_pontos(filtros).com(
            Recorte(("pedidos >= :minimo",), {"minimo": PEDIDOS_DE_UM_PONTO_CRONICO})
        )
        consulta = f"SELECT count(*) FROM ouro.mv_locais_cronicos_156 {recorte.onde}"
        return self._sessao.scalar(text(consulta), recorte.parametros) or 0

    def listar_pontos_cronicos(self, filtros: Filtros) -> list[PontoCronico]:
        recorte = _recorte_de_pontos(filtros)
        consulta = f"""
        SELECT
            bairro_oficial, categoria, servico, pedidos, dias_distintos, primeiro_ano, ultimo_ano
        FROM ouro.mv_locais_cronicos_156 {recorte.onde}
        ORDER BY posicao LIMIT :limite
        """
        parametros = {**recorte.parametros, "limite": PONTOS_CRONICOS_LISTADOS}
        return [PontoCronico(*linha) for linha in self._sessao.execute(text(consulta), parametros)]
