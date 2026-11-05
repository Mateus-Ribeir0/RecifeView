from datetime import date

from pydantic import BaseModel, Field

from app.api.schemas.painel import Esquema
from app.domain.ahp import BairroPriorizado
from app.domain.prioridade import FonteDaFila, OcorrenciaClassificada, Prioridade

ESCALA_MINIMA_DE_SAATY = 1 / 9
ESCALA_MAXIMA_DE_SAATY = 9.0


class JulgamentoEntrada(BaseModel):
    primeiro: str
    segundo: str
    valor: float = Field(ge=ESCALA_MINIMA_DE_SAATY, le=ESCALA_MAXIMA_DE_SAATY)


class JulgamentosEntrada(BaseModel):
    julgamentos: list[JulgamentoEntrada] = Field(default_factory=list)


class PedidoDeFilaEntrada(JulgamentosEntrada):
    fonte: FonteDaFila
    semente: int = 2026


class CriterioResposta(Esquema):
    chave: str
    nome: str
    unidade: str
    descricao: str


class JulgamentoPadraoResposta(BaseModel):
    primeiro: str
    segundo: str
    valor: float


class CriteriosResposta(BaseModel):
    criterios: list[CriterioResposta]
    julgamentos_padrao: list[JulgamentoPadraoResposta]
    razao_aceitavel: float


class BairroPriorizadoResposta(BaseModel):
    bairro_oficial: str
    nome: str
    rpa: str
    indice: float
    posicao: int
    contribuicoes: dict[str, float]
    risco: float | None
    vulnerabilidade: float | None
    atraso: float | None
    reincidencia: float | None

    @classmethod
    def de_bairro(cls, bairro: BairroPriorizado) -> "BairroPriorizadoResposta":
        item = bairro.indicadores
        return cls(
            bairro_oficial=item.bairro_oficial,
            nome=item.nome,
            rpa=item.rpa,
            indice=bairro.indice,
            posicao=bairro.posicao,
            contribuicoes=bairro.contribuicoes,
            risco=item.risco,
            vulnerabilidade=item.vulnerabilidade,
            atraso=item.atraso,
            reincidencia=item.reincidencia,
        )


class TesteDeSensibilidadeResposta(Esquema):
    criterio: str
    fator: float
    peso_testado: float
    mantidos_no_top: int


class PrioridadeResposta(BaseModel):
    pesos: dict[str, float]
    razao_de_consistencia: float
    coerente: bool
    bairros: list[BairroPriorizadoResposta]
    sensibilidade: list[TesteDeSensibilidadeResposta]

    @classmethod
    def de_prioridade(cls, prioridade: Prioridade) -> "PrioridadeResposta":
        return cls(
            pesos=prioridade.pesos,
            razao_de_consistencia=prioridade.razao_de_consistencia,
            coerente=prioridade.coerente,
            bairros=[BairroPriorizadoResposta.de_bairro(item) for item in prioridade.bairros],
            sensibilidade=[
                TesteDeSensibilidadeResposta.model_validate(item)
                for item in prioridade.sensibilidade
            ],
        )


class OcorrenciaClassificadaResposta(BaseModel):
    fila: int
    indice: float
    notas: dict[str, float | None]
    contribuicoes: dict[str, float]
    data_abertura: date | None
    idade_dias: int
    prazo_tipico_dias: float | None
    pedidos_anteriores: int | None
    bairro_oficial: str | None
    rpa: str | None
    categoria: str | None
    servico: str | None
    situacao: str | None
    orgao: str | None
    canal: str | None
    data_envio: date | None
    data_prazo: date | None
    natureza: str | None
    dias_alem_do_prazo: int | None

    @classmethod
    def de_classificada(cls, item: OcorrenciaClassificada) -> "OcorrenciaClassificadaResposta":
        ocorrencia = item.ocorrencia
        return cls(
            fila=item.fila,
            indice=item.indice,
            notas=item.notas,
            contribuicoes=item.contribuicoes,
            data_abertura=ocorrencia.data_abertura,
            idade_dias=ocorrencia.idade_dias,
            prazo_tipico_dias=ocorrencia.prazo_tipico_dias,
            pedidos_anteriores=ocorrencia.pedidos_anteriores,
            bairro_oficial=ocorrencia.bairro_oficial,
            rpa=ocorrencia.rpa,
            categoria=ocorrencia.categoria,
            servico=ocorrencia.servico,
            situacao=ocorrencia.situacao,
            orgao=ocorrencia.orgao,
            canal=ocorrencia.canal,
            data_envio=ocorrencia.data_envio,
            data_prazo=ocorrencia.data_prazo,
            natureza=ocorrencia.natureza,
            dias_alem_do_prazo=ocorrencia.dias_alem_do_prazo,
        )


class FaixaDeNotaResposta(Esquema):
    inicio: float
    fim: float
    registros: int


class FilaClassificadaResposta(BaseModel):
    fonte: FonteDaFila
    registros_na_base: int
    em_aberto: int
    classificados: int
    com_nota_alta: int
    pct_nota_alta: float | None
    amostra: list[OcorrenciaClassificadaResposta]
    topo: list[OcorrenciaClassificadaResposta]
    distribuicao: list[FaixaDeNotaResposta]
