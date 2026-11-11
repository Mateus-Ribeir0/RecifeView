from dataclasses import dataclass
from datetime import date

from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.encaminhamentos import (
    FiltroDeEncaminhamentos,
    PaginaDeEncaminhamentos,
    ResumoDosEncaminhamentos,
)


@dataclass(frozen=True)
class QuadroDeEncaminhamentos:
    hoje: date
    resumo: ResumoDosEncaminhamentos
    pagina: PaginaDeEncaminhamentos


@dataclass(frozen=True)
class ListarEncaminhamentos:
    servicos: ServicosDeEncaminhamento

    def executar(self, filtro: FiltroDeEncaminhamentos) -> QuadroDeEncaminhamentos:
        hoje = self.servicos.relogio.agora().date()
        repositorio = self.servicos.encaminhamentos
        return QuadroDeEncaminhamentos(
            hoje, repositorio.resumir(hoje), repositorio.listar(filtro, hoje)
        )
