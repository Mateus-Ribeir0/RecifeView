from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.encaminhamento.encaminhamento import Encaminhamento

QUEM_ENCAMINHOU = """
SELECT u.email
FROM app.encaminhamento e
JOIN app.usuario u ON u.id = e.criado_por
WHERE e.id = :id AND u.ativo AND u.recebe_avisos
"""
QUEM_ACOMPANHA = """
SELECT u.email
FROM app.pedido_acompanhado p
JOIN app.usuario u ON u.id = p.usuario_id
WHERE CAST(:protocolo AS text) IS NOT NULL AND p.protocolo = :protocolo
    AND u.ativo AND u.recebe_avisos AND u.perfil = 'CIDADAO'
UNION
SELECT u.email
FROM app.contribuicao c
JOIN app.usuario u ON u.id = c.usuario_id
WHERE CAST(:relato AS uuid) IN (c.id, c.principal_id)
    AND u.ativo AND u.recebe_avisos AND u.perfil = 'CIDADAO'
"""


class DestinatariosDosAvisosSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def email_de_quem_encaminhou(self, encaminhamento_id: int) -> str | None:
        return self._sessao.execute(text(QUEM_ENCAMINHOU), {"id": encaminhamento_id}).scalar()

    def emails_de_quem_acompanha(self, encaminhamento: Encaminhamento) -> list[str]:
        parametros = {
            "protocolo": encaminhamento.ocorrencia.protocolo,
            "relato": encaminhamento.contribuicao_id,
        }
        return list(self._sessao.execute(text(QUEM_ACOMPANHA), parametros).scalars())
