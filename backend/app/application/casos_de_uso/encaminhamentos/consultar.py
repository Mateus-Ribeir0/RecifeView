from dataclasses import dataclass, field
from datetime import date

from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.encaminhamentos import (
    FiltroDeEncaminhamentos,
    PaginaDeEncaminhamentos,
    ResumoDosEncaminhamentos,
)
from app.domain.encaminhamento.encaminhamento import Encaminhamento
from app.domain.encaminhamento.mesmo_problema import (
    MesmoProblema,
    encontrar_mesmo_problema,
    encontrar_mesmo_problema_de_cada,
)


@dataclass(frozen=True)
class QuadroDeEncaminhamentos:
    hoje: date
    resumo: ResumoDosEncaminhamentos
    pagina: PaginaDeEncaminhamentos
    mesmo_problema: dict[int, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ListarEncaminhamentos:
    servicos: ServicosDeEncaminhamento

    def executar(self, filtro: FiltroDeEncaminhamentos) -> QuadroDeEncaminhamentos:
        hoje = self.servicos.relogio.agora().date()
        repositorio = self.servicos.encaminhamentos
        pagina = repositorio.listar(filtro, hoje)
        candidatos = repositorio.comparaveis([item.ocorrencia for item in pagina.itens])
        parecidos = encontrar_mesmo_problema_de_cada(pagina.itens, candidatos)
        contagem = {identificador: len(lista) for identificador, lista in parecidos.items()}
        return QuadroDeEncaminhamentos(hoje, repositorio.resumir(hoje), pagina, contagem)


@dataclass(frozen=True)
class DetalheDoEncaminhamento:
    encaminhamento: Encaminhamento
    mesmo_problema: list[MesmoProblema]
    registros_do_mesmo_local: int


@dataclass(frozen=True)
class DetalharEncaminhamento:
    servicos: ServicosDeEncaminhamento

    def executar(self, encaminhamento_id: int) -> DetalheDoEncaminhamento:
        encaminhamento = self.servicos.obter(encaminhamento_id)
        repositorio = self.servicos.encaminhamentos
        candidatos = repositorio.comparaveis([encaminhamento.ocorrencia])
        parecidos = encontrar_mesmo_problema(
            encaminhamento.ocorrencia,
            (item for item in candidatos if item.id != encaminhamento.id),
        )
        return DetalheDoEncaminhamento(
            encaminhamento,
            parecidos,
            repositorio.registros_do_mesmo_local(encaminhamento.ocorrencia),
        )
