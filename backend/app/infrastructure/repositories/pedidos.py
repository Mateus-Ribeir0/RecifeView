from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.pedido import REGISTROS_POR_PROTOCOLO, PedidoAcompanhado, RegistroDoPedido

REGISTROS = """
SELECT
    chave_registro, fonte, protocolo, data_abertura, categoria, servico, tipo_registro, orgao,
    situacao, data_ult_movimento, ouv_data_prazo, bairro_oficial, rpa
FROM ouro.fato_demanda
WHERE protocolo = :protocolo
ORDER BY data_abertura DESC NULLS LAST
LIMIT :limite
"""
LISTAR = """
SELECT id, protocolo, criado_em FROM app.pedido_acompanhado
WHERE usuario_id = :usuario_id ORDER BY criado_em DESC, id DESC
"""
ADICIONAR = """
INSERT INTO app.pedido_acompanhado (usuario_id, protocolo, criado_em)
VALUES (:usuario_id, :protocolo, :agora)
RETURNING id, protocolo, criado_em
"""
REMOVER = "DELETE FROM app.pedido_acompanhado WHERE usuario_id = :usuario_id AND id = :id"
REMOVER_TODOS = "DELETE FROM app.pedido_acompanhado WHERE usuario_id = :usuario_id"


class ConsultaDePedidosSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def registros(self, protocolo: str) -> list[RegistroDoPedido]:
        parametros = {"protocolo": protocolo, "limite": REGISTROS_POR_PROTOCOLO}
        return [
            RegistroDoPedido(*linha) for linha in self._sessao.execute(text(REGISTROS), parametros)
        ]


class PedidoAcompanhadoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def listar(self, usuario_id: UUID) -> list[PedidoAcompanhado]:
        linhas = self._sessao.execute(text(LISTAR), {"usuario_id": usuario_id})
        return [PedidoAcompanhado(*linha) for linha in linhas]

    def adicionar(self, usuario_id: UUID, protocolo: str, agora: datetime) -> PedidoAcompanhado:
        parametros = {"usuario_id": usuario_id, "protocolo": protocolo, "agora": agora}
        return PedidoAcompanhado(*self._sessao.execute(text(ADICIONAR), parametros).one())

    def remover(self, usuario_id: UUID, pedido_id: int) -> None:
        self._sessao.execute(text(REMOVER), {"usuario_id": usuario_id, "id": pedido_id})

    def remover_todos(self, usuario_id: UUID) -> None:
        self._sessao.execute(text(REMOVER_TODOS), {"usuario_id": usuario_id})
