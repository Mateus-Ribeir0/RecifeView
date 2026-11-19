from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from app.domain.encaminhamento.avisos import Aviso
from app.domain.encaminhamento.encaminhamento import (
    AutorDoEvento,
    CanalDeEnvio,
    Encaminhamento,
    OcorrenciaEncaminhavel,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.mensagem import MensagemAoOrgao
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.encaminhamento.sugestao import CitacoesDoTema


@dataclass(frozen=True)
class TokenDeRetorno:
    hash: str
    expira_em: datetime


@dataclass(frozen=True)
class NovoEncaminhamento:
    ocorrencia: OcorrenciaEncaminhavel
    orgao: Orgao
    orgao_sugerido: Orgao | None
    canal: CanalDeEnvio
    criado_em: datetime
    prazo_de_resposta: date
    token: TokenDeRetorno
    criado_por: UUID | None = None
    nota: float | None = None
    justificativa: str | None = None
    automatico: bool = False
    contribuicao_id: UUID | None = None


@dataclass(frozen=True)
class MudancaDeSituacao:
    situacao: SituacaoDoEncaminhamento
    autor: AutorDoEvento
    ocorrido_em: datetime
    usuario_id: UUID | None = None
    observacao: str | None = None
    protocolo_do_orgao: str | None = None
    resposta_ao_cidadao: str | None = None
    previsao: date | None = None


class OrdemDaLista(StrEnum):
    MAIS_RECENTES = "mais_recentes"
    PRAZO_MAIS_PROXIMO = "prazo_mais_proximo"
    ATUALIZADOS_POR_ULTIMO = "atualizados_por_ultimo"


@dataclass(frozen=True)
class FiltroDeEncaminhamentos:
    situacao: SituacaoDoEncaminhamento | None = None
    orgao: Orgao | None = None
    so_atrasados: bool = False
    so_os_que_pedem_acao: bool = False
    limite: int = 50
    deslocamento: int = 0
    situacoes: frozenset[SituacaoDoEncaminhamento] = frozenset()
    bairro: str | None = None
    categoria: str | None = None
    ordem: OrdemDaLista = OrdemDaLista.MAIS_RECENTES


@dataclass(frozen=True)
class PaginaDeEncaminhamentos:
    itens: list[Encaminhamento] = field(default_factory=list)
    total: int = 0


@dataclass(frozen=True)
class ResumoDosEncaminhamentos:
    total: int = 0
    abertos: int = 0
    atrasados: int = 0
    por_situacao: dict[SituacaoDoEncaminhamento, int] = field(default_factory=dict)
    mediana_de_dias_ate_resolver: float | None = None


@dataclass(frozen=True)
class PendenciasDosEncaminhamentos:
    """Conta só o último encaminhamento de cada ocorrência: o que já seguiu adiante não pesa."""

    devolvidos: int = 0
    falhas: int = 0
    prazo_vencido: int = 0

    @property
    def pedem_acao(self) -> int:
        return self.devolvidos + self.falhas + self.prazo_vencido


class EncaminhamentoRepository(Protocol):
    def ocorrencia(self, chave_registro: int) -> OcorrenciaEncaminhavel | None: ...

    def citacoes_do_tema(self, tema: str) -> CitacoesDoTema: ...

    def da_ocorrencia(self, chave_registro: int) -> list[Encaminhamento]: ...

    def criar(self, novo: NovoEncaminhamento) -> Encaminhamento: ...

    def buscar(self, encaminhamento_id: int) -> Encaminhamento | None: ...

    def buscar_pelo_token(self, hash_do_token: str, agora: datetime) -> Encaminhamento | None: ...

    def mudar_situacao(self, encaminhamento_id: int, mudanca: MudancaDeSituacao) -> None: ...

    def preparar_reenvio(
        self, encaminhamento_id: int, token: TokenDeRetorno, canal: CanalDeEnvio
    ) -> None: ...

    def listar(self, filtro: FiltroDeEncaminhamentos, hoje: date) -> PaginaDeEncaminhamentos: ...

    def resumir(self, hoje: date) -> ResumoDosEncaminhamentos: ...

    def contar_pendencias(self, hoje: date) -> PendenciasDosEncaminhamentos: ...

    def local_aproximado_do_relato(self, contribuicao_id: UUID) -> str | None: ...

    def vencidos_sem_lembrete(self, hoje: date) -> list[Encaminhamento]: ...

    def registrar_lembrete(
        self, encaminhamento_id: int, token: TokenDeRetorno, agora: datetime
    ) -> None: ...

    def comparaveis(
        self, ocorrencias: Sequence[OcorrenciaEncaminhavel]
    ) -> list[Encaminhamento]: ...

    def registros_do_mesmo_local(self, ocorrencia: OcorrenciaEncaminhavel) -> int: ...


class EncaminhamentosDasOcorrencias(Protocol):
    def ultimos_por_chave(self, chaves: Sequence[int]) -> dict[int, Encaminhamento]: ...


class EncaminhamentosDosRelatos(Protocol):
    def ultimos_por_relato(self, ids: Sequence[UUID]) -> dict[UUID, Encaminhamento]: ...


@dataclass(frozen=True)
class Destinatario:
    usuario_id: UUID
    email: str
    recebe_email: bool = True


class DestinatariosDosAvisos(Protocol):
    def gestor_que_encaminhou(self, encaminhamento_id: int) -> Destinatario | None: ...

    def cidadaos_que_acompanham(self, encaminhamento: Encaminhamento) -> list[Destinatario]: ...

    def pessoas_do_orgao(self, orgao: Orgao) -> list[Destinatario]: ...


class PessoasQueAcompanham(Protocol):
    def contar(self, encaminhamentos: Sequence[Encaminhamento]) -> dict[int, int]: ...


class EntregaDeAvisos(Protocol):
    def entregar(self, para: str, aviso: Aviso) -> None: ...


class EnvioAoOrgaoFalhou(Exception):
    """O canal do órgão recusou ou não respondeu. O encaminhamento fica gravado como falha."""


class DespachoAosOrgaos(Protocol):
    def canal_de(self, orgao: Orgao) -> CanalDeEnvio: ...

    def enviar(self, mensagem: MensagemAoOrgao) -> None: ...
