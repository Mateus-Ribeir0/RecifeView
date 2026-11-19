from dataclasses import dataclass
from datetime import date

from app.application.casos_de_uso.corporativo.servicos import ServicosDoOrgao
from app.application.portas.encaminhamentos import FiltroDeEncaminhamentos, OrdemDaLista
from app.domain.demanda_do_orgao import DemandaDoOrgao, PeriodoEmAnos
from app.domain.encaminhamento.desempenho import (
    ContagemPorTema,
    IndicadoresDoOrgao,
    SemanaDoCiclo,
)
from app.domain.encaminhamento.encaminhamento import SITUACOES_ABERTAS, Encaminhamento
from app.domain.encaminhamento.mesmo_problema import agrupar_mesmo_problema
from app.domain.encaminhamento.orgaos import Orgao, nomes_na_fonte

MAIS_URGENTES_MOSTRADAS = 5
LIMITE_DE_ABERTAS_AGRUPADAS = 200


@dataclass(frozen=True)
class PainelDoOrgao:
    hoje: date
    indicadores: IndicadoresDoOrgao
    semanas: list[SemanaDoCiclo]
    abertas_por_bairro: dict[str, int]
    resolvidas_por_tema: list[ContagemPorTema]
    mais_urgentes: list[Encaminhamento]
    grupos_do_mesmo_problema: list[list[Encaminhamento]]
    pessoas_com_retorno: int


@dataclass(frozen=True)
class MontarPainelDoOrgao:
    servicos: ServicosDoOrgao

    def executar(self, orgao: Orgao) -> PainelDoOrgao:
        hoje = self.servicos.hoje()
        indicadores = self.servicos.indicadores
        abertas = self._abertas(orgao, hoje)
        return PainelDoOrgao(
            hoje=hoje,
            indicadores=next(iter(indicadores.por_orgao(hoje, orgao)), IndicadoresDoOrgao(orgao)),
            semanas=indicadores.semanas(hoje, orgao),
            abertas_por_bairro=indicadores.abertas_por_bairro(orgao),
            resolvidas_por_tema=indicadores.resolvidas_por_tema(orgao),
            mais_urgentes=abertas[:MAIS_URGENTES_MOSTRADAS],
            grupos_do_mesmo_problema=agrupar_mesmo_problema(abertas),
            pessoas_com_retorno=indicadores.pessoas_com_retorno(orgao),
        )

    def _abertas(self, orgao: Orgao, hoje: date) -> list[Encaminhamento]:
        filtro = FiltroDeEncaminhamentos(
            orgao=orgao,
            situacoes=SITUACOES_ABERTAS,
            ordem=OrdemDaLista.PRAZO_MAIS_PROXIMO,
            limite=LIMITE_DE_ABERTAS_AGRUPADAS,
        )
        return self.servicos.encaminhamentos.encaminhamentos.listar(filtro, hoje).itens


@dataclass(frozen=True)
class ConsultarDemandaDoOrgao:
    servicos: ServicosDoOrgao

    def executar(self, orgao: Orgao, periodo: PeriodoEmAnos) -> DemandaDoOrgao:
        return self.servicos.demanda.resumir(nomes_na_fonte(orgao), periodo)
