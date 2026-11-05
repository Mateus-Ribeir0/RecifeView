from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.sobre import ANO_INICIAL_DA_COBERTURA, CoberturaPorFonte, CorrecaoAplicada

COBERTURA = """
SELECT fonte, ano, sum(n)::int FROM ouro.mv_demanda
WHERE ano >= :ano_inicial
GROUP BY fonte, ano ORDER BY fonte, ano
"""
CORRECOES = """
SELECT correcao.key, sum(correcao.value::int)::int
FROM app.importacao i
CROSS JOIN LATERAL jsonb_each_text(i.resultado -> 'correcoes') AS correcao
WHERE i.status = 'CONCLUIDA'
GROUP BY correcao.key ORDER BY 2 DESC
"""
REGISTROS = "SELECT coalesce(sum(registros), 0)::int FROM ouro.mv_referencia_por_fonte"


class SobreRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def cobertura(self) -> list[CoberturaPorFonte]:
        parametros = {"ano_inicial": ANO_INICIAL_DA_COBERTURA}
        return [
            CoberturaPorFonte(*linha) for linha in self._sessao.execute(text(COBERTURA), parametros)
        ]

    def correcoes(self) -> list[CorrecaoAplicada]:
        return [CorrecaoAplicada(*linha) for linha in self._sessao.execute(text(CORRECOES))]

    def registros_na_base(self) -> int:
        return self._sessao.scalar(text(REGISTROS)) or 0
