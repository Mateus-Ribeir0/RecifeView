from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.cidade import SituacaoPublica


class OcorrenciaPublicaResposta(BaseModel):
    """Lista explícita: o número exato e o texto do relato não têm campo aqui."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data_relato: date
    servico: str
    tema: str
    bairro_oficial: str
    bairro: str
    rpa: str
    via: str | None
    faixa_de_numeracao: str | None
    relatos: int
    sem_retorno: int
    situacao: SituacaoPublica


class MeuRelatoResposta(BaseModel):
    """Vai só para quem enviou: por isso o endereço e o texto podem voltar."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recebido_em: datetime
    servico: str
    tema: str
    bairro: str
    endereco: str | None
    detalhe: str | None
    endereco_apagado: bool
    somado: bool
    relatos: int
    situacao: SituacaoPublica


class ComparacaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bairro: float | None
    recife: float | None


class IndicadoresDoBairroResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bairro_oficial: str
    nome: str
    rpa: str
    populacao: int
    ano_inicio: int
    ano_fim: int
    pedidos_ao_156: int
    pedidos_por_mil_habitantes: ComparacaoResposta
    prazo_mediano: ComparacaoResposta
    prazo_p90: ComparacaoResposta
    pct_local_repetido: ComparacaoResposta
