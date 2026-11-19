from dataclasses import dataclass, field, replace
from enum import StrEnum

from app.application.casos_de_uso.corporativo.servicos import (
    SITUACOES_VISIVEIS_AO_ORGAO,
    ServicosDoOrgao,
)
from app.application.portas.encaminhamentos import FiltroDeEncaminhamentos, OrdemDaLista
from app.application.portas.indicadores import OpcoesDeFiltro
from app.domain.encaminhamento.desempenho import IndicadoresDoOrgao
from app.domain.encaminhamento.encaminhamento import (
    SITUACOES_ABERTAS,
    Encaminhamento,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.mesmo_problema import (
    MesmoProblema,
    encontrar_mesmo_problema,
    encontrar_mesmo_problema_de_cada,
)
from app.domain.encaminhamento.orgaos import Orgao

ITENS_POR_PAGINA = 30


class AbaDoOrgao(StrEnum):
    NOVAS = "novas"
    EM_ATENDIMENTO = "em_atendimento"
    VENCIDAS = "vencidas"
    RESOLVIDAS = "resolvidas"
    DEVOLVIDAS = "devolvidas"
    TODAS = "todas"


FILTROS_DAS_ABAS: dict[AbaDoOrgao, FiltroDeEncaminhamentos] = {
    AbaDoOrgao.NOVAS: FiltroDeEncaminhamentos(
        situacoes=frozenset({SituacaoDoEncaminhamento.ENVIADO}),
        ordem=OrdemDaLista.PRAZO_MAIS_PROXIMO,
    ),
    AbaDoOrgao.EM_ATENDIMENTO: FiltroDeEncaminhamentos(
        situacoes=frozenset({SituacaoDoEncaminhamento.RECEBIDO}),
        ordem=OrdemDaLista.PRAZO_MAIS_PROXIMO,
    ),
    AbaDoOrgao.VENCIDAS: FiltroDeEncaminhamentos(
        so_atrasados=True, ordem=OrdemDaLista.PRAZO_MAIS_PROXIMO
    ),
    AbaDoOrgao.RESOLVIDAS: FiltroDeEncaminhamentos(
        situacoes=frozenset({SituacaoDoEncaminhamento.RESOLVIDO}),
        ordem=OrdemDaLista.ATUALIZADOS_POR_ULTIMO,
    ),
    AbaDoOrgao.DEVOLVIDAS: FiltroDeEncaminhamentos(
        situacoes=frozenset({SituacaoDoEncaminhamento.DEVOLVIDO}),
        ordem=OrdemDaLista.ATUALIZADOS_POR_ULTIMO,
    ),
    AbaDoOrgao.TODAS: FiltroDeEncaminhamentos(situacoes=SITUACOES_VISIVEIS_AO_ORGAO),
}


def contar_por_aba(indicadores: IndicadoresDoOrgao) -> dict[AbaDoOrgao, int]:
    return {
        AbaDoOrgao.NOVAS: indicadores.novas,
        AbaDoOrgao.EM_ATENDIMENTO: indicadores.em_atendimento,
        AbaDoOrgao.VENCIDAS: indicadores.vencidas,
        AbaDoOrgao.RESOLVIDAS: indicadores.resolvidas,
        AbaDoOrgao.DEVOLVIDAS: indicadores.devolvidas,
        AbaDoOrgao.TODAS: indicadores.encaminhados,
    }


@dataclass(frozen=True)
class PedidoDaFila:
    aba: AbaDoOrgao = AbaDoOrgao.NOVAS
    bairro: str | None = None
    categoria: str | None = None
    deslocamento: int = 0


@dataclass(frozen=True)
class ItemDaFila:
    encaminhamento: Encaminhamento
    mesmo_problema_no_orgao: int = 0
    mesmo_problema_em_outros_orgaos: int = 0
    pessoas_que_acompanham: int = 0


@dataclass(frozen=True)
class FilaDoOrgao:
    itens: list[ItemDaFila]
    total: int
    por_aba: dict[AbaDoOrgao, int]
    opcoes: OpcoesDeFiltro = field(default_factory=OpcoesDeFiltro)


def _separar_por_orgao(parecidos: list[MesmoProblema], orgao: Orgao) -> tuple[int, int]:
    no_orgao = sum(1 for item in parecidos if item.encaminhamento.orgao is orgao)
    return no_orgao, len(parecidos) - no_orgao


@dataclass(frozen=True)
class ListarOcorrenciasDoOrgao:
    servicos: ServicosDoOrgao

    def executar(self, orgao: Orgao, pedido: PedidoDaFila) -> FilaDoOrgao:
        hoje = self.servicos.hoje()
        repositorio = self.servicos.encaminhamentos.encaminhamentos
        filtro = replace(
            FILTROS_DAS_ABAS[pedido.aba],
            orgao=orgao,
            bairro=pedido.bairro,
            categoria=pedido.categoria,
            limite=ITENS_POR_PAGINA,
            deslocamento=pedido.deslocamento,
        )
        pagina = repositorio.listar(filtro, hoje)
        candidatos = repositorio.comparaveis([item.ocorrencia for item in pagina.itens])
        parecidos = encontrar_mesmo_problema_de_cada(pagina.itens, candidatos)
        pessoas = self.servicos.pessoas.contar(pagina.itens)
        itens = [
            ItemDaFila(
                item,
                *_separar_por_orgao(parecidos[item.id], orgao),
                pessoas.get(item.id, 0),
            )
            for item in pagina.itens
        ]
        indicadores = next(
            iter(self.servicos.indicadores.por_orgao(hoje, orgao)), IndicadoresDoOrgao(orgao)
        )
        opcoes = self.servicos.indicadores.opcoes_de_filtro(orgao)
        return FilaDoOrgao(itens, pagina.total, contar_por_aba(indicadores), opcoes)


@dataclass(frozen=True)
class OcorrenciaDoOrgao:
    encaminhamento: Encaminhamento
    mesmo_problema: list[MesmoProblema]
    pessoas_que_acompanham: int
    registros_do_mesmo_local: int

    @property
    def pode_responder(self) -> bool:
        return self.encaminhamento.situacao in SITUACOES_ABERTAS


@dataclass(frozen=True)
class ConsultarOcorrenciaDoOrgao:
    servicos: ServicosDoOrgao

    def executar(self, orgao: Orgao, encaminhamento_id: int) -> OcorrenciaDoOrgao:
        encaminhamento = self.servicos.do_orgao(encaminhamento_id, orgao)
        repositorio = self.servicos.encaminhamentos.encaminhamentos
        candidatos = repositorio.comparaveis([encaminhamento.ocorrencia])
        parecidos = encontrar_mesmo_problema(
            encaminhamento.ocorrencia,
            (item for item in candidatos if item.id != encaminhamento.id),
        )
        pessoas = self.servicos.pessoas.contar([encaminhamento])
        return OcorrenciaDoOrgao(
            encaminhamento,
            parecidos,
            pessoas.get(encaminhamento.id, 0),
            repositorio.registros_do_mesmo_local(encaminhamento.ocorrencia),
        )
