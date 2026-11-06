from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.application.casos_de_uso.importacoes.consultar_importacao import ImportacaoDetalhada
from app.domain.fontes import Fonte
from app.domain.importacao.datas import FormatoDeData
from app.domain.importacao.decisoes import (
    PoliticaDeDatasInvalidas,
    PoliticaDeDuplicados,
    PoliticaDeRepetidos,
    PoliticaEntreCanais,
)
from app.domain.importacao.importacao import Importacao


class ColunaResposta(BaseModel):
    nome: str
    campo: str | None
    origem: str
    bloqueada: bool
    motivo_de_bloqueio: str | None
    exemplos: list[str]


class MesmoArquivoResposta(BaseModel):
    id: int
    criada_em: datetime
    status: str


class EstruturaResposta(BaseModel):
    formato: str | None = None
    codificacao: str | None = None
    separador: str | None = None
    layout_nome: str | None = None
    guardar_arquivo: bool | None = None
    colunas: list[ColunaResposta] = Field(default_factory=list)
    mesmo_arquivo: list[MesmoArquivoResposta] = Field(default_factory=list)


class ValorEmDuvidaResposta(BaseModel):
    valor: str
    quantidade: int
    sugestao: str | None


class PendenciaResposta(BaseModel):
    tipo: str
    campo: str | None
    rotulo_do_campo: str | None
    quantidade: int
    valores: list[ValorEmDuvidaResposta]
    alternativas: list[str]
    total_de_valores: int
    detalhes: dict[str, int]


class ResumoDaValidacaoResposta(BaseModel):
    lidas: int = 0
    aceitas: int = 0
    novas: int = 0
    iguais: int = 0
    alteradas: int = 0
    repetidas_no_arquivo: int = 0
    sem_id_local: int = 0
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    descartes: dict[str, int] = Field(default_factory=dict)
    correcoes: dict[str, int] = Field(default_factory=dict)
    fontes: dict[str, int] = Field(default_factory=dict)
    pente_fino: dict[str, int] = Field(default_factory=dict)


class PreviaResposta(BaseModel):
    antes: dict[str, str]
    depois: dict[str, str]


class PendenciasResposta(BaseModel):
    itens: list[PendenciaResposta] = Field(default_factory=list)
    resumo: ResumoDaValidacaoResposta = Field(default_factory=ResumoDaValidacaoResposta)
    previa: list[PreviaResposta] = Field(default_factory=list)


class ResultadoResposta(BaseModel):
    lidas: int = 0
    aceitas: int = 0
    novas: int = 0
    atualizadas: int = 0
    iguais: int = 0
    ignoradas: int = 0
    retiradas: int = 0
    repetidas_no_arquivo: int = 0
    sem_id_local: int = 0
    descartes: dict[str, int] = Field(default_factory=dict)
    correcoes: dict[str, int] = Field(default_factory=dict)
    fontes: dict[str, int] = Field(default_factory=dict)
    pente_fino: dict[str, int] = Field(default_factory=dict)


class DecisoesResposta(BaseModel):
    fonte: str | None
    data_do_retrato: date | None
    mapeamento: dict[str, str]
    valores_fixos: dict[str, str]
    formato_de_data: str | None
    substituicoes: dict[str, dict[str, str]]
    padrao_para_valores: dict[str, str]
    datas_invalidas: str | None
    repetidos_na_base: str | None
    repetidos_no_arquivo: str | None
    coincidencias_certas: str | None
    coincidencias_provaveis: str | None


class ImportacaoResumoResposta(BaseModel):
    id: int
    nome_do_arquivo: str
    tamanho_em_bytes: int
    status: str
    progresso: int
    fonte: str | None
    layout: str | None
    data_do_retrato: date | None
    periodo_inicio: date | None
    periodo_fim: date | None
    criada_em: datetime
    concluida_em: datetime | None
    desfeita_em: datetime | None
    nome_de_quem_importou: str | None
    carga_inicial: bool
    arquivo_guardado: bool
    resultado: ResultadoResposta

    @classmethod
    def de_importacao(cls, importacao: Importacao) -> "ImportacaoResumoResposta":
        return cls(**_campos_do_resumo(importacao))


class ImportacaoDetalheResposta(ImportacaoResumoResposta):
    estrutura: EstruturaResposta
    decisoes: DecisoesResposta
    pendencias: PendenciasResposta
    mensagem_de_erro: str | None
    pode_desfazer: bool

    @classmethod
    def de_detalhe(cls, detalhe: ImportacaoDetalhada) -> "ImportacaoDetalheResposta":
        importacao = detalhe.importacao
        return cls(
            **_campos_do_resumo(importacao),
            estrutura=EstruturaResposta(**importacao.estrutura),
            decisoes=DecisoesResposta(**importacao.decisoes.para_dicionario()),
            pendencias=PendenciasResposta(**importacao.pendencias),
            mensagem_de_erro=importacao.mensagem_de_erro,
            pode_desfazer=detalhe.pode_desfazer,
        )


def _campos_do_resumo(importacao: Importacao) -> dict[str, Any]:
    return {
        "id": importacao.id,
        "nome_do_arquivo": importacao.nome_do_arquivo,
        "tamanho_em_bytes": importacao.tamanho_em_bytes,
        "status": importacao.status.value,
        "progresso": importacao.progresso,
        "fonte": importacao.fonte,
        "layout": importacao.layout,
        "data_do_retrato": importacao.data_do_retrato,
        "periodo_inicio": importacao.periodo_inicio,
        "periodo_fim": importacao.periodo_fim,
        "criada_em": importacao.criada_em,
        "concluida_em": importacao.concluida_em,
        "desfeita_em": importacao.desfeita_em,
        "nome_de_quem_importou": importacao.nome_de_quem_importou,
        "carga_inicial": importacao.carga_inicial,
        "arquivo_guardado": importacao.arquivo_guardado,
        "resultado": ResultadoResposta(**importacao.resultado),
    }


class PaginaDeImportacoesResposta(BaseModel):
    itens: list[ImportacaoResumoResposta]
    total: int


class CampoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str
    rotulo: str
    tipo: str
    descricao: str


class EscolhaDeColunasEntrada(BaseModel):
    fonte: Fonte | None = None
    data_do_retrato: date
    mapeamento: dict[str, str | None]
    valores_fixos: dict[str, str] = Field(default_factory=dict)


class RespostasDePendenciasEntrada(BaseModel):
    formato_de_data: FormatoDeData | None = None
    substituicoes: dict[str, dict[str, str]] = Field(default_factory=dict)
    padrao_para_valores: dict[str, str] = Field(default_factory=dict)
    datas_invalidas: PoliticaDeDatasInvalidas | None = None
    repetidos_na_base: PoliticaDeRepetidos | None = None
    repetidos_no_arquivo: PoliticaDeDuplicados | None = None
    coincidencias_certas: PoliticaEntreCanais | None = None
    coincidencias_provaveis: PoliticaEntreCanais | None = None


class RegistroImportadoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fonte: str
    ano: int | None
    data_abertura: date | None
    data_ult_movimento: date | None
    dias_ate_movimento: int | None
    categoria: str | None
    servico: str | None
    orgao: str | None
    bairro_oficial: str | None
    rpa: str | None
    situacao: str | None


class PaginaDeRegistrosResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    itens: list[RegistroImportadoResposta]
    total: int
