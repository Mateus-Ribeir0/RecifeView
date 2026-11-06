from dataclasses import dataclass

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.contribuicoes import (
    ContribuicaoRepository,
    LimiteDeEnvios,
    ReferenciaDoFormulario,
)
from app.application.portas.relogio import Relogio


@dataclass(frozen=True)
class ServicosDeContribuicoes:
    contribuicoes: ContribuicaoRepository
    referencia: ReferenciaDoFormulario
    limite: LimiteDeEnvios
    relogio: Relogio
    importacao: ServicosDeImportacao
    sal: str | None = None
