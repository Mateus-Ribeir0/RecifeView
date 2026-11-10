from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.domain.conta import CodigoDeConta, FinalidadeDoCodigo
from app.infrastructure.db.modelos import CodigoDeContaModelo


def _para_dominio(modelo: CodigoDeContaModelo) -> CodigoDeConta:
    return CodigoDeConta(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        finalidade=FinalidadeDoCodigo(modelo.finalidade),
        hash_do_codigo=modelo.hash_do_codigo,
        criado_em=modelo.criado_em,
        expira_em=modelo.expira_em,
        tentativas=modelo.tentativas,
        usado_em=modelo.usado_em,
    )


class CodigoDeContaRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, codigo: CodigoDeConta) -> None:
        self._sessao.add(
            CodigoDeContaModelo(
                id=codigo.id,
                usuario_id=codigo.usuario_id,
                finalidade=codigo.finalidade.value,
                hash_do_codigo=codigo.hash_do_codigo,
                criado_em=codigo.criado_em,
                expira_em=codigo.expira_em,
                tentativas=codigo.tentativas,
                usado_em=codigo.usado_em,
            )
        )
        self._sessao.flush()

    def ultimo(self, usuario_id: UUID, finalidade: FinalidadeDoCodigo) -> CodigoDeConta | None:
        consulta = (
            select(CodigoDeContaModelo)
            .where(
                CodigoDeContaModelo.usuario_id == usuario_id,
                CodigoDeContaModelo.finalidade == finalidade.value,
            )
            .order_by(CodigoDeContaModelo.criado_em.desc())
            .limit(1)
        )
        modelo = self._sessao.scalar(consulta)
        return _para_dominio(modelo) if modelo else None

    def atualizar(self, codigo: CodigoDeConta) -> None:
        modelo = self._sessao.get(CodigoDeContaModelo, codigo.id)
        if modelo is None:
            return
        modelo.tentativas = codigo.tentativas
        modelo.usado_em = codigo.usado_em
        self._sessao.flush()

    def invalidar_abertos(
        self, usuario_id: UUID, finalidade: FinalidadeDoCodigo, agora: datetime
    ) -> None:
        self._sessao.execute(
            update(CodigoDeContaModelo)
            .where(
                CodigoDeContaModelo.usuario_id == usuario_id,
                CodigoDeContaModelo.finalidade == finalidade.value,
                CodigoDeContaModelo.usado_em.is_(None),
            )
            .values(usado_em=agora)
        )
