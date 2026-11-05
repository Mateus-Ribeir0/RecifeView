from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.domain.importacao.normalizador import Referencias

VOCABULARIO_PREENCHIDO = """
SELECT ispopulated FROM pg_matviews
WHERE schemaname = 'ouro' AND matviewname = 'mv_vocabulario'
"""


class ReferenciasSql:
    def __init__(self, fabrica: sessionmaker[Session]) -> None:
        self._fabrica = fabrica

    def carregar(self) -> Referencias:
        with self._fabrica() as sessao:
            consulta = text("SELECT bairro_oficial, rpa FROM ouro.dim_bairro")
            bairros: dict[str, str] = {bairro: rpa for bairro, rpa in sessao.execute(consulta)}
            if not sessao.scalar(text(VOCABULARIO_PREENCHIDO)):
                return Referencias(bairros, {})
            linhas = sessao.execute(text("SELECT fonte, campo, valor FROM ouro.mv_vocabulario"))
            valores: dict[tuple[str, str], set[str]] = defaultdict(set)
            for fonte, campo, valor in linhas:
                valores[(fonte, campo)].add(valor)
        return Referencias(bairros, {chave: frozenset(v) for chave, v in valores.items()})
