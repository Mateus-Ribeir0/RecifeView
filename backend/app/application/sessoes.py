import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID, uuid4

from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import EmissorDeTokenDeAcesso, TokenDeAcesso
from app.application.portas.sessoes import SessaoRepository
from app.domain.erros import SessaoInvalida
from app.domain.sessao import Sessao
from app.domain.usuario import Usuario

DURACAO_PADRAO_DA_SESSAO = timedelta(hours=12)
BYTES_DO_TOKEN_DE_SESSAO = 32


@dataclass(frozen=True)
class AcessoConcedido:
    usuario: Usuario
    token_de_acesso: TokenDeAcesso


@dataclass(frozen=True)
class SessaoAberta:
    acesso: AcessoConcedido
    token_de_sessao: str
    validade: timedelta


def calcular_hash_do_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass(frozen=True)
class GestaoDeSessoes:
    sessoes: SessaoRepository
    emissor: EmissorDeTokenDeAcesso
    relogio: Relogio
    duracao_da_sessao: timedelta = DURACAO_PADRAO_DA_SESSAO

    def abrir(self, usuario: Usuario) -> SessaoAberta:
        agora = self.relogio.agora()
        token_de_sessao = secrets.token_urlsafe(BYTES_DO_TOKEN_DE_SESSAO)
        sessao = Sessao(
            id=uuid4(),
            usuario_id=usuario.id,
            hash_do_token=calcular_hash_do_token(token_de_sessao),
            criada_em=agora,
            expira_em=agora + self.duracao_da_sessao,
        )
        self.sessoes.adicionar(sessao)
        return SessaoAberta(self.conceder_acesso(usuario), token_de_sessao, self.duracao_da_sessao)

    def conceder_acesso(self, usuario: Usuario) -> AcessoConcedido:
        return AcessoConcedido(usuario, self.emissor.emitir(usuario, self.relogio.agora()))

    def buscar_ativa(self, token_de_sessao: str | None) -> Sessao:
        if not token_de_sessao:
            raise SessaoInvalida
        sessao = self.sessoes.buscar_por_hash_do_token(calcular_hash_do_token(token_de_sessao))
        if sessao is None or not sessao.esta_ativa(self.relogio.agora()):
            raise SessaoInvalida
        return sessao

    def encerrar(self, sessao: Sessao) -> None:
        self.sessoes.atualizar(sessao.revogada(self.relogio.agora()))

    def encerrar_todas(self, usuario_id: UUID) -> None:
        self.sessoes.revogar_todas_do_usuario(usuario_id, self.relogio.agora())
