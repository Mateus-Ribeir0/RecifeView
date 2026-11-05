from sqlalchemy.orm import Session

from app.domain.auditoria import ConsultaAuditada
from app.infrastructure.db.modelos import ConsultaAuditadaModelo


class RegistroDeConsultasSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def registrar(self, consulta: ConsultaAuditada) -> None:
        self._sessao.add(
            ConsultaAuditadaModelo(
                usuario_id=consulta.usuario_id,
                rota=consulta.rota,
                filtros=consulta.filtros,
                ocorrida_em=consulta.ocorrida_em,
            )
        )
