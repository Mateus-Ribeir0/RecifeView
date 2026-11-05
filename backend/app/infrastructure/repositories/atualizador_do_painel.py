from collections.abc import Callable

from sqlalchemy import Engine, text

VIEWS_NA_ORDEM = (
    "mv_referencia_por_fonte",
    "mv_prazo_tipico_156",
    "mv_demanda",
    "mv_prazos_156",
    "mv_reincidencia_156",
    "mv_locais_cronicos_156",
    "mv_camara_indicacoes",
    "mv_ouvidoria",
    "mv_linha_do_tempo_156",
    "mv_linha_do_tempo_camara",
    "mv_linha_do_tempo_ouvidoria",
    "mv_fluxo_diario_156",
    "mv_entradas_diarias",
    "mv_indicadores_bairro",
    "mv_vocabulario",
)
PROGRESSO_COMPLETO = 100


class AtualizadorDoPainelSql:
    """Atualiza com CONCURRENTLY para o painel seguir respondendo durante a atualização."""

    def __init__(self, motor: Engine) -> None:
        self._motor = motor

    def _esta_preenchida(self, view: str) -> bool:
        with self._motor.connect() as conexao:
            return bool(
                conexao.scalar(
                    text(
                        "SELECT ispopulated FROM pg_matviews "
                        "WHERE schemaname = 'ouro' AND matviewname = :view"
                    ),
                    {"view": view},
                )
            )

    def atualizar(self, ao_avancar: Callable[[int], None]) -> None:
        for posicao, view in enumerate(VIEWS_NA_ORDEM, start=1):
            modo = "CONCURRENTLY" if self._esta_preenchida(view) else ""
            with self._motor.begin() as conexao:
                conexao.execute(text(f"REFRESH MATERIALIZED VIEW {modo} ouro.{view}"))
            ao_avancar(posicao * PROGRESSO_COMPLETO // len(VIEWS_NA_ORDEM))
