from collections import Counter
from dataclasses import dataclass
from datetime import date

from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.acessos_corporativos import AcessosCorporativosRepository
from app.application.portas.encaminhamentos import FiltroDeEncaminhamentos, OrdemDaLista
from app.application.portas.indicadores import IndicadoresDoCicloRepository
from app.domain.acesso_corporativo import SituacaoDoAcesso
from app.domain.encaminhamento.desempenho import IndicadoresDoOrgao, SemanaDoCiclo
from app.domain.encaminhamento.encaminhamento import (
    SITUACOES_ABERTAS,
    CanalDeEnvio,
    Encaminhamento,
)
from app.domain.encaminhamento.mesmo_problema import agrupar_mesmo_problema
from app.domain.encaminhamento.orgaos import CATALOGO_DE_ORGAOS, Orgao

LIMITE_DE_ABERTOS_AGRUPADOS = 500


@dataclass(frozen=True)
class DesempenhoDoOrgao:
    indicadores: IndicadoresDoOrgao
    canal: CanalDeEnvio
    acessos_ativos: int


@dataclass(frozen=True)
class DesempenhoDosOrgaos:
    hoje: date
    orgaos: list[DesempenhoDoOrgao]
    semanas: list[SemanaDoCiclo]
    grupos_do_mesmo_problema: list[list[Encaminhamento]]


@dataclass(frozen=True)
class CompararOrgaos:
    """Todos os órgãos do catálogo aparecem, mesmo sem encaminhamento: a ausência também conta."""

    servicos: ServicosDeEncaminhamento
    indicadores: IndicadoresDoCicloRepository
    acessos: AcessosCorporativosRepository

    def executar(self) -> DesempenhoDosOrgaos:
        hoje = self.servicos.relogio.agora().date()
        medidos = {item.orgao: item for item in self.indicadores.por_orgao(hoje)}
        ativos = self._acessos_ativos()
        orgaos = [
            DesempenhoDoOrgao(
                medidos.get(dados.orgao, IndicadoresDoOrgao(dados.orgao)),
                self.servicos.canal_para(dados.orgao),
                ativos[dados.orgao],
            )
            for dados in CATALOGO_DE_ORGAOS
        ]
        return DesempenhoDosOrgaos(
            hoje,
            sorted(orgaos, key=lambda item: item.indicadores.encaminhados, reverse=True),
            self.indicadores.semanas(hoje),
            agrupar_mesmo_problema(self._abertos(hoje)),
        )

    def _acessos_ativos(self) -> Counter[Orgao]:
        agora = self.servicos.relogio.agora()
        return Counter(
            acesso.orgao
            for acesso in self.acessos.listar()
            if acesso.situacao(agora) is SituacaoDoAcesso.ATIVO
        )

    def _abertos(self, hoje: date) -> list[Encaminhamento]:
        filtro = FiltroDeEncaminhamentos(
            situacoes=SITUACOES_ABERTAS,
            ordem=OrdemDaLista.PRAZO_MAIS_PROXIMO,
            limite=LIMITE_DE_ABERTOS_AGRUPADOS,
        )
        return self.servicos.encaminhamentos.listar(filtro, hoje).itens
