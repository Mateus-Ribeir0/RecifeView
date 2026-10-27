from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.domain.erros import SessaoInvalida
from app.domain.sessao import Sessao
from app.infrastructure.db.modelos import SessaoModelo


class SessaoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, sessao: Sessao) -> None:
        self._sessao.add(
            SessaoModelo(
                id=sessao.id,
                usuario_id=sessao.usuario_id,
                hash_do_token=sessao.hash_do_token,
                criada_em=sessao.criada_em,
                expira_em=sessao.expira_em,
                revogada_em=sessao.revogada_em,
            )
        )
        self._sessao.flush()

    def buscar_por_hash_do_token(self, hash_do_token: str) -> Sessao | None:
        consulta = select(SessaoModelo).where(SessaoModelo.hash_do_token == hash_do_token)
        modelo = self._sessao.scalar(consulta)
        return _para_dominio(modelo) if modelo else None

    def atualizar(self, sessao: Sessao) -> None:
        modelo = self._sessao.get(SessaoModelo, sessao.id)
        if modelo is None:
            raise SessaoInvalida
        modelo.expira_em = sessao.expira_em
        modelo.revogada_em = sessao.revogada_em
        self._sessao.flush()

    def revogar_todas_do_usuario(self, usuario_id: UUID, agora: datetime) -> None:
        self._sessao.execute(
            update(SessaoModelo)
            .where(SessaoModelo.usuario_id == usuario_id, SessaoModelo.revogada_em.is_(None))
            .values(revogada_em=agora)
        )


def _para_dominio(modelo: SessaoModelo) -> Sessao:
    return Sessao(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        hash_do_token=modelo.hash_do_token,
        criada_em=modelo.criada_em,
        expira_em=modelo.expira_em,
        revogada_em=modelo.revogada_em,
    )
