from dataclasses import dataclass

from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import EmissorDeTokenDeAcesso
from app.application.portas.usuarios import UsuarioRepository
from app.domain.erros import SessaoInvalida
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class IdentificarUsuario:
    usuarios: UsuarioRepository
    emissor: EmissorDeTokenDeAcesso
    relogio: Relogio

    def executar(self, token_de_acesso: str) -> Usuario:
        usuario_id = self.emissor.identificar(token_de_acesso, self.relogio.agora())
        usuario = self.usuarios.buscar_por_id(usuario_id)
        if usuario is None or not usuario.ativo:
            raise SessaoInvalida
        return usuario
