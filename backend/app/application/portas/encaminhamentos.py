from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

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


@dataclass(frozen=True)
class MudancaDeSituacao:
    situacao: SituacaoDoEncaminhamento
    autor: AutorDoEvento
    ocorrido_em: datetime
    usuario_id: UUID | None = None
    observacao: str | None = None
    protocolo_do_orgao: str | None = None


@dataclass(frozen=True)
class FiltroDeEncaminhamentos:
    situacao: SituacaoDoEncaminhamento | None = None
    orgao: Orgao | None = None
    so_atrasados: bool = False
    limite: int = 50
    deslocamento: int = 0


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


class EncaminhamentosDasOcorrencias(Protocol):
    def ultimos_por_chave(self, chaves: Sequence[int]) -> dict[int, Encaminhamento]: ...


class EnvioAoOrgaoFalhou(Exception):
    """O canal do órgão recusou ou não respondeu. O encaminhamento fica gravado como falha."""


class DespachoAosOrgaos(Protocol):
    def canal_de(self, orgao: Orgao) -> CanalDeEnvio: ...

    def enviar(self, mensagem: MensagemAoOrgao) -> None: ...
