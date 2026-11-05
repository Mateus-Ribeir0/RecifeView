from pydantic import BaseModel, ConfigDict


class Esquema(BaseModel):
    """Só os campos declarados saem: coluna nova no banco não vaza por acidente."""

    model_config = ConfigDict(from_attributes=True)


class BairroDoCatalogoResposta(Esquema):
    bairro_oficial: str
    nome: str
    rpa: str
    populacao: int
    pct_favela: float
    taxa_confiavel: bool


class FonteDoCatalogoResposta(Esquema):
    codigo: str
    rotulo: str
    registros: int


class CatalogoDeFiltrosResposta(Esquema):
    ano_minimo: int
    ano_maximo: int
    rpas: list[str]
    bairros: list[BairroDoCatalogoResposta]
    categorias: list[str]
    fontes: list[FonteDoCatalogoResposta]


class DemandaPorAnoResposta(Esquema):
    ano: int
    fonte: str
    n: int


class ResumoDasIndicacoesResposta(Esquema):
    total: int
    enviadas: int
    respondidas: int
    pct_enviadas: float | None
    pct_respondidas: float | None
    mediana_dias_ate_envio: float | None
    mediana_dias_ate_resposta: float | None


class PercentisDePrazoResposta(Esquema):
    mediana: int | None
    p90: int | None


class VisaoGeralResposta(Esquema):
    demandas: int
    indicacoes: ResumoDasIndicacoesResposta
    pct_local_repetido: float | None
    prazo: PercentisDePrazoResposta
    serie: list[DemandaPorAnoResposta]


class RespostaPorAnoResposta(Esquema):
    ano: int
    indicacoes: int
    respondidas: int
    canal: str | None
    pct_respondidas: float


class CelulaDeDestinoResposta(Esquema):
    categoria: str
    orgao: str
    n: int
    pct: float


class DispersaoDaCategoriaResposta(Esquema):
    categoria: str
    orgao_principal: str
    pct_principal: float
    orgaos: int


class FluxoDeOrgaoResposta(Esquema):
    orgao: str
    desfecho: str
    n: int


class CaminhoDaCategoriaResposta(Esquema):
    categoria: str
    fluxos: list[FluxoDeOrgaoResposta]


class RetornoResposta(Esquema):
    resumo: ResumoDasIndicacoesResposta
    por_ano: list[RespostaPorAnoResposta]
    celulas: list[CelulaDeDestinoResposta]
    orgaos: list[str]
    dispersoes: list[DispersaoDaCategoriaResposta]
    caminhos: list[CaminhoDaCategoriaResposta]


class CanalPorAnoResposta(Esquema):
    ano: int
    canal: str
    n: int
    pct: float


class CanaisDaOuvidoriaResposta(Esquema):
    canais: list[CanalPorAnoResposta]
    ano_do_app: int | None
    pct_do_app: float | None
    pct_no_prazo: float | None
    total: int


class IntervalosDeRepeticaoResposta(Esquema):
    duplicidade: int
    intermediario: int
    reincidencia: int
    total: int


class RecorrenciaPorCategoriaResposta(Esquema):
    categoria: str
    pedidos: int
    repetidos: int
    pct_repetidos: float
    intervalos: IntervalosDeRepeticaoResposta


class PontoCronicoResposta(Esquema):
    bairro_oficial: str | None
    categoria: str | None
    servico: str | None
    pedidos: int
    dias_distintos: int
    primeiro_ano: int
    ultimo_ano: int


class RecorrenciasResposta(Esquema):
    pedidos: int
    repetidos: int
    pct_repetidos: float | None
    intervalos: IntervalosDeRepeticaoResposta
    pontos_cronicos: int
    minimo_por_categoria: int
    por_categoria: list[RecorrenciaPorCategoriaResposta]
    lista_de_pontos: list[PontoCronicoResposta]


class ResumoDosPrazosResposta(Esquema):
    pedidos: int
    mediana: int | None
    p90: int | None
    pct_mesmo_dia: float | None
    pct_acima_de_90_dias: float | None


class PrazoPorAnoResposta(Esquema):
    ano: int
    mediana: int
    p90: int


class FaixaDePrazoResposta(Esquema):
    faixa: str
    n: int
    pct: float


class PrazoPorCategoriaResposta(Esquema):
    categoria: str
    pedidos: int
    mediana: int
    p90: int
    pct_mesmo_dia: float


class EstoquePorCategoriaResposta(Esquema):
    categoria: str
    abertos: int
    acima_do_prazo: int


class EstoqueAbertoResposta(Esquema):
    abertos: int
    acima_do_prazo: int
    pct_acima_do_prazo: float | None
    por_categoria: list[EstoquePorCategoriaResposta]


class PrazosResposta(Esquema):
    resumo: ResumoDosPrazosResposta
    por_ano: list[PrazoPorAnoResposta]
    faixas: list[FaixaDePrazoResposta]
    minimo_por_categoria: int
    por_categoria: list[PrazoPorCategoriaResposta]
    estoque: EstoqueAbertoResposta


class FaixaDeTaxaResposta(Esquema):
    inicio: float
    fim: float


class IndicadorDeTerritorioResposta(Esquema):
    volume: int
    taxa: float | None
    classe: int | None


class BairroDoTerritorioResposta(Esquema):
    bairro_oficial: str
    nome: str
    rpa: str
    populacao: int
    pct_favela: float
    taxa_confiavel: bool
    em_destaque: bool
    central_156: IndicadorDeTerritorioResposta
    defesa_civil: IndicadorDeTerritorioResposta
    pct_reincidencia_156: float | None
    pct_atraso_156: float | None
    abertos_156: int | None


class PontoResposta(Esquema):
    x: float
    y: float


class TerritorioResposta(Esquema):
    bairros: list[BairroDoTerritorioResposta]
    faixas_156: list[FaixaDeTaxaResposta]
    faixas_defesa_civil: list[FaixaDeTaxaResposta]
    tendencia_156: list[PontoResposta]
    tendencia_defesa_civil: list[PontoResposta]
    anos_156: int
    anos_defesa_civil: int
