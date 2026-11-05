from dataclasses import dataclass

from app.domain.visao_geral import ResumoDasIndicacoes

CATEGORIAS_NO_MAPA_DE_CALOR = 9
ORGAOS_NO_MAPA_DE_CALOR = 7
ORGAOS_NO_SANKEY = 5
ORGAO_AGRUPADO = "OUTROS"
CANAIS_PRINCIPAIS_DA_OUVIDORIA = (
    "0800",
    "SITE",
    "E-MAIL",
    "ATENDIMENTO PESSOAL",
    "APP CONECTA RECIFE",
)
CANAL_AGRUPADO = "OUTROS"
CANAL_DO_APP = "APP CONECTA RECIFE"
DESFECHOS = {
    "ENVIADO E COM RESPOSTA REGISTRADA": "com resposta",
    "ENVIADO, SEM RESPOSTA REGISTRADA": "sem resposta",
    "SEM ENVIO REGISTRADO": "sem envio",
    "RETIRADO/PREJUDICADO/REJEITADO": "retirada",
}
DESFECHO_PADRAO = "sem envio"


@dataclass(frozen=True)
class RespostaPorAno:
    ano: int
    indicacoes: int
    respondidas: int
    canal: str | None
    pct_respondidas: float


@dataclass(frozen=True)
class CelulaDeDestino:
    categoria: str
    orgao: str
    n: int
    pct: float


@dataclass(frozen=True)
class DispersaoDaCategoria:
    categoria: str
    orgao_principal: str
    pct_principal: float
    orgaos: int


@dataclass(frozen=True)
class FluxoDeOrgao:
    orgao: str
    desfecho: str
    n: int


@dataclass(frozen=True)
class CaminhoDaCategoria:
    categoria: str
    fluxos: list[FluxoDeOrgao]


@dataclass(frozen=True)
class RetornoDasIndicacoes:
    resumo: ResumoDasIndicacoes
    por_ano: list[RespostaPorAno]
    celulas: list[CelulaDeDestino]
    orgaos: list[str]
    dispersoes: list[DispersaoDaCategoria]
    caminhos: list[CaminhoDaCategoria]


@dataclass(frozen=True)
class CanalPorAno:
    ano: int
    canal: str
    n: int
    pct: float


@dataclass(frozen=True)
class CanaisDaOuvidoria:
    canais: list[CanalPorAno]
    ano_do_app: int | None
    pct_do_app: float | None
    pct_no_prazo: float | None
    total: int
