from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.erros import NotificacaoNaoEncontrada
from app.domain.notificacao import CaixaDeNotificacoes, Notificacao, NovaNotificacao

INSERIR = """
INSERT INTO app.notificacao (usuario_id, titulo, texto, caminho)
VALUES (:usuario_id, :titulo, :texto, :caminho)
"""
ULTIMAS = """
SELECT id, titulo, texto, caminho, criada_em, lida_em
FROM app.notificacao
WHERE usuario_id = :usuario_id
ORDER BY criada_em DESC, id DESC
LIMIT :limite
"""
NAO_LIDAS = (
    "SELECT count(*)::int FROM app.notificacao WHERE usuario_id = :usuario_id AND lida_em IS NULL"
)
MARCAR_LIDA = """
UPDATE app.notificacao SET lida_em = coalesce(lida_em, :agora)
WHERE id = :id AND usuario_id = :usuario_id
"""
MARCAR_TODAS = """
UPDATE app.notificacao SET lida_em = :agora WHERE usuario_id = :usuario_id AND lida_em IS NULL
"""


class NotificacaoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def criar(self, nova: NovaNotificacao) -> None:
        parametros = {
            "usuario_id": nova.usuario_id,
            "titulo": nova.titulo,
            "texto": nova.texto,
            "caminho": nova.caminho,
        }
        self._sessao.execute(text(INSERIR), parametros)

    def caixa_do_usuario(self, usuario_id: UUID, limite: int) -> CaixaDeNotificacoes:
        parametros = {"usuario_id": usuario_id, "limite": limite}
        itens = [Notificacao(*linha) for linha in self._sessao.execute(text(ULTIMAS), parametros)]
        nao_lidas = self._sessao.execute(text(NAO_LIDAS), parametros).scalar_one()
        return CaixaDeNotificacoes(nao_lidas, itens)

    def marcar_lida(self, usuario_id: UUID, notificacao_id: int, agora: datetime) -> None:
        parametros = {"id": notificacao_id, "usuario_id": usuario_id, "agora": agora}
        resultado = self._sessao.execute(text(MARCAR_LIDA), parametros)
        if resultado.rowcount == 0:  # type: ignore[attr-defined]
            raise NotificacaoNaoEncontrada

    def marcar_todas_lidas(self, usuario_id: UUID, agora: datetime) -> None:
        self._sessao.execute(text(MARCAR_TODAS), {"usuario_id": usuario_id, "agora": agora})
