from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.orm import Session

from app.application.portas.encaminhamentos import Destinatario
from app.domain.encaminhamento.encaminhamento import Encaminhamento
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.usuario import DOMINIO_DAS_CONTAS_EXCLUIDAS

QUEM_ENCAMINHOU = """
SELECT u.id, u.email, u.recebe_avisos
FROM app.encaminhamento e
JOIN app.usuario u ON u.id = e.criado_por
WHERE e.id = :id AND u.ativo
"""
QUEM_ACOMPANHA = """
SELECT u.id, u.email, u.recebe_avisos
FROM app.pedido_acompanhado p
JOIN app.usuario u ON u.id = p.usuario_id
WHERE CAST(:protocolo AS text) IS NOT NULL AND p.protocolo = :protocolo
    AND u.ativo AND u.perfil = 'CIDADAO'
UNION
SELECT u.id, u.email, u.recebe_avisos
FROM app.contribuicao c
JOIN app.usuario u ON u.id = c.usuario_id
WHERE CAST(:relato AS uuid) IN (c.id, c.principal_id)
    AND u.ativo AND u.perfil = 'CIDADAO'
"""
PESSOAS_DO_ORGAO = """
SELECT u.id, u.email, u.recebe_avisos
FROM app.usuario u
WHERE u.perfil = 'CORPORATIVO' AND u.orgao = :orgao AND u.ativo AND u.email NOT LIKE :excluidas
    AND (
        EXISTS (
            SELECT 1 FROM app.convite_de_acesso c
            WHERE c.usuario_id = u.id AND c.usado_em IS NOT NULL
        )
        OR NOT EXISTS (SELECT 1 FROM app.convite_de_acesso c WHERE c.usuario_id = u.id)
    )
"""
QUANTOS_ACOMPANHAM = """
WITH alvos AS (
    SELECT * FROM unnest(CAST(:ids AS int[]), CAST(:protocolos AS text[]), CAST(:relatos AS uuid[]))
        AS a(encaminhamento_id, protocolo, relato)
)
SELECT alvos.encaminhamento_id, count(DISTINCT pessoas.usuario_id)::int
FROM alvos
JOIN LATERAL (
    SELECT p.usuario_id FROM app.pedido_acompanhado p
    WHERE alvos.protocolo IS NOT NULL AND p.protocolo = alvos.protocolo
    UNION
    SELECT c.usuario_id FROM app.contribuicao c
    WHERE alvos.relato IS NOT NULL AND alvos.relato IN (c.id, c.principal_id)
        AND c.usuario_id IS NOT NULL
) pessoas ON true
GROUP BY alvos.encaminhamento_id
"""
CONTAS_EXCLUIDAS = f"%@{DOMINIO_DAS_CONTAS_EXCLUIDAS}"


def _destinatario(linha: Row[Any]) -> Destinatario:
    dados = linha._mapping
    return Destinatario(dados["id"], dados["email"], dados["recebe_avisos"])


class DestinatariosDosAvisosSql:
    """Quem fica sabendo de cada mudança, e quantas pessoas acompanham cada pedido."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def gestor_que_encaminhou(self, encaminhamento_id: int) -> Destinatario | None:
        linha = self._sessao.execute(text(QUEM_ENCAMINHOU), {"id": encaminhamento_id}).first()
        return _destinatario(linha) if linha else None

    def cidadaos_que_acompanham(self, encaminhamento: Encaminhamento) -> list[Destinatario]:
        parametros = {
            "protocolo": encaminhamento.ocorrencia.protocolo,
            "relato": encaminhamento.contribuicao_id,
        }
        return [
            _destinatario(linha) for linha in self._sessao.execute(text(QUEM_ACOMPANHA), parametros)
        ]

    def pessoas_do_orgao(self, orgao: Orgao) -> list[Destinatario]:
        parametros = {"orgao": orgao.value, "excluidas": CONTAS_EXCLUIDAS}
        return [
            _destinatario(linha)
            for linha in self._sessao.execute(text(PESSOAS_DO_ORGAO), parametros)
        ]

    def contar(self, encaminhamentos: Sequence[Encaminhamento]) -> dict[int, int]:
        if not encaminhamentos:
            return {}
        relatos: list[UUID | None] = [item.contribuicao_id for item in encaminhamentos]
        parametros = {
            "ids": [item.id for item in encaminhamentos],
            "protocolos": [item.ocorrencia.protocolo for item in encaminhamentos],
            "relatos": relatos,
        }
        linhas = self._sessao.execute(text(QUANTOS_ACOMPANHAM), parametros)
        return {encaminhamento_id: pessoas for encaminhamento_id, pessoas in linhas}
