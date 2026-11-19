from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID

from app.domain.encaminhamento.orgaos import Orgao

VALIDADE_DO_CONVITE = timedelta(days=7)
CAMINHO_DO_CONVITE = "/convite/"


class SituacaoDoAcesso(StrEnum):
    CONVITE_ENVIADO = "convite_enviado"
    CONVITE_VENCIDO = "convite_vencido"
    ATIVO = "ativo"
    DESATIVADO = "desativado"


@dataclass(frozen=True)
class ConviteDeAcesso:
    id: UUID
    usuario_id: UUID
    hash_do_token: str
    criado_em: datetime
    expira_em: datetime
    usado_em: datetime | None = None

    def pode_ser_usado(self, agora: datetime) -> bool:
        return self.usado_em is None and agora < self.expira_em


@dataclass(frozen=True)
class AcessoCorporativo:
    """A conta como a administração vê: quem é, de qual órgão e se o convite já virou acesso."""

    usuario_id: UUID
    nome: str
    email: str
    orgao: Orgao
    ativo: bool
    criado_em: datetime
    convite_aceito: bool
    convite_expira_em: datetime | None = None
    ultimo_acesso_em: datetime | None = None

    def situacao(self, agora: datetime) -> SituacaoDoAcesso:
        if not self.ativo:
            return SituacaoDoAcesso.DESATIVADO
        if self.convite_aceito:
            return SituacaoDoAcesso.ATIVO
        if self.convite_expira_em is not None and agora < self.convite_expira_em:
            return SituacaoDoAcesso.CONVITE_ENVIADO
        return SituacaoDoAcesso.CONVITE_VENCIDO
