from dataclasses import dataclass

from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import AcessoConcedido, GestaoDeSessoes
from app.domain.erros import SessaoInvalida


@dataclass(frozen=True)
class RenovarAcesso:
    usuarios: UsuarioRepository
    sessoes: GestaoDeSessoes

    def executar(self, token_de_sessao: str | None) -> AcessoConcedido:
        sessao = self.sessoes.buscar_ativa(token_de_sessao)
        usuario = self.usuarios.buscar_por_id(sessao.usuario_id)
        if usuario is None or not usuario.ativo:
            raise SessaoInvalida
        return self.sessoes.conceder_acesso(usuario)
