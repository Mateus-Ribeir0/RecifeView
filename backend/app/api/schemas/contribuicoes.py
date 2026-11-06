from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.contribuicao.contribuicao import (
    TAMANHO_MAXIMO_DA_VIA,
    TAMANHO_MAXIMO_DO_DETALHE,
    TAMANHO_MAXIMO_DO_NUMERO,
    DecisaoDoPar,
    FormularioPreenchido,
    ResultadoDoEnvio,
    RetornoAnterior,
)

TAMANHO_MINIMO_DA_CHAVE_DE_ENVIO = 16
TAMANHO_MAXIMO_DA_CHAVE_DE_ENVIO = 64


class ServicoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    rotulo: str


class TemaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chave: str
    rotulo: str
    servicos: list[ServicoResposta]


class BairroResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chave: str
    nome: str
    rpa: str


class CatalogoDoFormularioResposta(BaseModel):
    temas: list[TemaResposta]
    bairros: list[BairroResposta]


class ContribuicaoEntrada(BaseModel):
    chave_de_envio: str = Field(
        min_length=TAMANHO_MINIMO_DA_CHAVE_DE_ENVIO, max_length=TAMANHO_MAXIMO_DA_CHAVE_DE_ENVIO
    )
    servico_codigo: str = Field(max_length=10)
    bairro_oficial: str = Field(max_length=60)
    logradouro: str = Field(max_length=TAMANHO_MAXIMO_DA_VIA)
    numero: str = Field(default="", max_length=TAMANHO_MAXIMO_DO_NUMERO)
    detalhe: str = Field(default="", max_length=TAMANHO_MAXIMO_DO_DETALHE)
    retorno: RetornoAnterior
    site: str = Field(default="", max_length=200)

    def para_formulario(self) -> FormularioPreenchido:
        return FormularioPreenchido(
            chave_de_envio=self.chave_de_envio,
            servico_codigo=self.servico_codigo,
            bairro_oficial=self.bairro_oficial,
            logradouro=self.logradouro,
            numero=self.numero,
            detalhe=self.detalhe,
            retorno=self.retorno,
        )


class ResultadoDoEnvioResposta(BaseModel):
    resultado: ResultadoDoEnvio


class ResumoDasContribuicoesResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    relatos: int
    ocorrencias: int
    somados: int
    aguardando_revisao: int
    prontas_para_pacote: int
    em_pacote: int
    na_base: int
    retiradas: int
    sem_retorno: int


class OcorrenciaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recebida_em: datetime
    servico: str
    bairro: str
    logradouro: str | None
    numero: str | None
    relatos: int
    sem_retorno: int
    situacao: str


class PaginaDeOcorrenciasResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    itens: list[OcorrenciaResposta]
    total: int


class LadoDoParResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recebida_em: datetime
    servico: str
    bairro: str
    logradouro: str | None
    numero: str | None
    detalhe: str | None
    relatos: int


class ParResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pontuacao: float
    motivos: list[str]
    primeiro: LadoDoParResposta
    segundo: LadoDoParResposta


class DecisaoDoParEntrada(BaseModel):
    decisao: DecisaoDoPar
