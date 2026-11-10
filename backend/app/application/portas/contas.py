from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.conta import CodigoDeConta, FinalidadeDoCodigo


@dataclass(frozen=True)
class MensagemDeEmail:
    para: str
    assunto: str
    corpo: str


class CodigoDeContaRepository(Protocol):
    def adicionar(self, codigo: CodigoDeConta) -> None: ...

    def ultimo(self, usuario_id: UUID, finalidade: FinalidadeDoCodigo) -> CodigoDeConta | None: ...

    def atualizar(self, codigo: CodigoDeConta) -> None: ...

    def invalidar_abertos(
        self, usuario_id: UUID, finalidade: FinalidadeDoCodigo, agora: datetime
    ) -> None: ...


class EnvioDeEmail(Protocol):
    def enviar(self, mensagem: MensagemDeEmail) -> None: ...
