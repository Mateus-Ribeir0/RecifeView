from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.orm import Session

from app.domain.acesso_corporativo import AcessoCorporativo, ConviteDeAcesso
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.usuario import DOMINIO_DAS_CONTAS_EXCLUIDAS

INSERIR_CONVITE = """
INSERT INTO app.convite_de_acesso (id, usuario_id, hash_do_token, criado_em, expira_em, criado_por)
VALUES (:id, :usuario_id, :hash_do_token, :criado_em, :expira_em, :criado_por)
"""
CONVITE_PELO_HASH = """
SELECT id, usuario_id, hash_do_token, criado_em, expira_em, usado_em
FROM app.convite_de_acesso
WHERE hash_do_token = :hash
"""
MARCAR_USADO = "UPDATE app.convite_de_acesso SET usado_em = :agora WHERE id = :id"
ENCERRAR_ABERTOS = """
UPDATE app.convite_de_acesso SET expira_em = :agora
WHERE usuario_id = :usuario_id AND usado_em IS NULL AND expira_em > :agora
"""
ACESSOS = """
SELECT
    u.id, u.nome, u.email, u.orgao, u.ativo, u.criado_em,
    EXISTS (
        SELECT 1 FROM app.convite_de_acesso c WHERE c.usuario_id = u.id AND c.usado_em IS NOT NULL
    ) OR NOT EXISTS (
        SELECT 1 FROM app.convite_de_acesso c WHERE c.usuario_id = u.id
    ) AS convite_aceito,
    (
        SELECT max(c.expira_em) FROM app.convite_de_acesso c
        WHERE c.usuario_id = u.id AND c.usado_em IS NULL
    ) AS convite_expira_em,
    (
        SELECT max(a.ocorrido_em) FROM app.evento_de_acesso a
        WHERE a.usuario_id = u.id AND a.tipo IN ('ENTRADA', 'CONVITE_ACEITO')
    ) AS ultimo_acesso_em
FROM app.usuario u
WHERE u.perfil = 'CORPORATIVO' AND u.orgao IS NOT NULL AND u.email NOT LIKE :excluidas
"""
ORDEM_DA_LISTA = " ORDER BY u.orgao, u.nome"
CONTAS_EXCLUIDAS = f"%@{DOMINIO_DAS_CONTAS_EXCLUIDAS}"


def _acesso(linha: Row[Any]) -> AcessoCorporativo:
    dados = linha._mapping
    return AcessoCorporativo(
        usuario_id=dados["id"],
        nome=dados["nome"],
        email=dados["email"],
        orgao=Orgao(dados["orgao"]),
        ativo=dados["ativo"],
        criado_em=dados["criado_em"],
        convite_aceito=dados["convite_aceito"],
        convite_expira_em=dados["convite_expira_em"],
        ultimo_acesso_em=dados["ultimo_acesso_em"],
    )


class ConviteRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, convite: ConviteDeAcesso, criado_por: UUID | None) -> None:
        parametros = {
            "id": convite.id,
            "usuario_id": convite.usuario_id,
            "hash_do_token": convite.hash_do_token,
            "criado_em": convite.criado_em,
            "expira_em": convite.expira_em,
            "criado_por": criado_por,
        }
        self._sessao.execute(text(INSERIR_CONVITE), parametros)

    def buscar_pelo_hash(self, hash_do_token: str) -> ConviteDeAcesso | None:
        linha = self._sessao.execute(text(CONVITE_PELO_HASH), {"hash": hash_do_token}).first()
        return ConviteDeAcesso(*linha) if linha else None

    def marcar_usado(self, convite_id: UUID, agora: datetime) -> None:
        self._sessao.execute(text(MARCAR_USADO), {"id": convite_id, "agora": agora})

    def encerrar_os_abertos(self, usuario_id: UUID, agora: datetime) -> None:
        self._sessao.execute(text(ENCERRAR_ABERTOS), {"usuario_id": usuario_id, "agora": agora})


class AcessosCorporativosSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def listar(self) -> list[AcessoCorporativo]:
        linhas = self._sessao.execute(
            text(ACESSOS + ORDEM_DA_LISTA), {"excluidas": CONTAS_EXCLUIDAS}
        )
        return [_acesso(linha) for linha in linhas]

    def buscar(self, usuario_id: UUID) -> AcessoCorporativo | None:
        consulta = text(ACESSOS + " AND u.id = :id")
        linha = self._sessao.execute(
            consulta, {"excluidas": CONTAS_EXCLUIDAS, "id": usuario_id}
        ).first()
        return _acesso(linha) if linha else None
