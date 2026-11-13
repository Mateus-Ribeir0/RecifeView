from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.application.portas.importacoes import ContribuicoesDaImportacao
from app.domain.contribuicao.comparacao import Comparacao
from app.domain.contribuicao.contribuicao import Contribuicao, DecisaoDoPar


@dataclass(frozen=True)
class ParNovo:
    contribuicao_id: UUID
    comparacao: Comparacao


@dataclass(frozen=True)
class BairroDoFormulario:
    chave: str
    nome: str
    rpa: str


@dataclass(frozen=True)
class ResumoDasContribuicoes:
    relatos: int = 0
    ocorrencias: int = 0
    somados: int = 0
    aguardando_revisao: int = 0
    prontas_para_pacote: int = 0
    em_pacote: int = 0
    na_base: int = 0
    retiradas: int = 0
    sem_retorno: int = 0


@dataclass(frozen=True)
class OcorrenciaDoPainel:
    id: UUID
    recebida_em: datetime
    servico: str
    bairro: str
    logradouro: str | None
    numero: str | None
    relatos: int
    sem_retorno: int
    situacao: str


@dataclass(frozen=True)
class PaginaDeOcorrencias:
    itens: list[OcorrenciaDoPainel]
    total: int


@dataclass(frozen=True)
class LadoDoPar:
    id: UUID
    recebida_em: datetime
    servico: str
    bairro: str
    logradouro: str | None
    numero: str | None
    detalhe: str | None
    relatos: int


@dataclass(frozen=True)
class ParParaRevisar:
    id: int
    pontuacao: float
    motivos: list[str]
    primeiro: LadoDoPar
    segundo: LadoDoPar


@dataclass(frozen=True)
class OcorrenciaDoPacote:
    contribuicao_id: UUID
    data_relato: date
    categoria: str
    servico_codigo: str
    servico: str
    bairro_oficial: str
    id_local: str | None
    numero_informado: bool
    relatos: int


@dataclass(frozen=True)
class FiltroDaCidade:
    desde: date
    bairro: str | None = None
    categorias: tuple[str, ...] = ()


@dataclass(frozen=True)
class RelatoDoCidadao:
    """Um relato visto por quem o enviou: o endereço é dele, então pode voltar inteiro."""

    id: UUID
    recebida_em: datetime
    servico_codigo: str
    servico: str
    bairro: str
    logradouro: str | None
    numero: str | None
    detalhe: str | None
    endereco_apagado: bool
    somado: bool
    relatos: int
    situacao: str
    tem_dupla_aberta: bool
    ocorrencia_id: UUID


@dataclass(frozen=True)
class OcorrenciaDaCidade:
    """Linha crua da quarentena: o número sai daqui só para virar faixa no caso de uso."""

    id: UUID
    data_relato: date
    servico_codigo: str
    servico: str
    bairro_oficial: str
    bairro: str
    rpa: str
    via_reconhecida: str | None
    numero: str | None
    relatos: int
    sem_retorno: int
    situacao: str
    tem_dupla_aberta: bool


@dataclass(frozen=True)
class DecisaoRegistrada:
    decisao: DecisaoDoPar
    usuario_id: UUID
    decidida_em: datetime


class ContribuicaoRepository(ContribuicoesDaImportacao, Protocol):
    def buscar_por_chave_de_envio(self, chave: str) -> Contribuicao | None: ...

    def candidatas(self, bairro: str, categoria: str, desde: date) -> list[Contribuicao]: ...

    def inserir(self, contribuicao: Contribuicao, pares: Sequence[ParNovo]) -> Contribuicao: ...

    def resumir(self) -> ResumoDasContribuicoes: ...

    def listar_ocorrencias(self, limite: int, deslocamento: int) -> PaginaDeOcorrencias: ...

    def listar_pares_abertos(self, limite: int) -> list[ParParaRevisar]: ...

    def decidir_par(self, par_id: int, decisao: DecisaoRegistrada) -> bool: ...

    def contar_pares_abertos(self) -> int: ...

    def prontas_para_pacote(self) -> list[OcorrenciaDoPacote]: ...

    def marcar_no_pacote(self, ids: Sequence[UUID], importacao_id: int) -> None: ...

    def expurgar_enderecos(self, recebidas_ate: datetime, agora: datetime) -> int: ...

    def ocorrencias_da_cidade(self, filtro: FiltroDaCidade) -> list[OcorrenciaDaCidade]: ...

    def relatos_do_cidadao(self, usuario_id: UUID) -> list[RelatoDoCidadao]: ...


class ReferenciaDoFormulario(Protocol):
    def bairros(self) -> list[BairroDoFormulario]: ...

    def logradouros(self, bairro: str) -> list[str]: ...

    def somar_logradouros(self, vias: Iterable[tuple[str, str, int]]) -> int: ...


class LimiteDeEnvios(Protocol):
    def permitir(self, origem: str) -> bool: ...
