from sqlalchemy.orm import Session

from app.domain.acesso import EventoDeAcesso
from app.infrastructure.db.modelos import EventoDeAcessoModelo


class RegistroDeAcessosSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def registrar(self, evento: EventoDeAcesso) -> None:
        self._sessao.add(
            EventoDeAcessoModelo(
                usuario_id=evento.usuario_id,
                tipo=evento.tipo.value,
                ocorrido_em=evento.ocorrido_em,
            )
        )
