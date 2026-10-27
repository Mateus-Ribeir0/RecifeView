from typing import Protocol

from app.domain.acesso import EventoDeAcesso


class RegistroDeAcessos(Protocol):
    def registrar(self, evento: EventoDeAcesso) -> None: ...
