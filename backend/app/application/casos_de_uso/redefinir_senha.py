from dataclasses import dataclass

from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.senhas_temporarias import gerar_senha_temporaria
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.email import Email
from app.domain.erros import UsuarioNaoEncontrado


@dataclass(frozen=True)
class RedefinirSenha:
    usuarios: UsuarioRepository
    senhas: HashDeSenha
    sessoes: GestaoDeSessoes
    acessos: RegistroDeAcessos
    relogio: Relogio

    def executar(self, email: str) -> str:
        usuario = self.usuarios.buscar_por_email(Email(email))
        if usuario is None:
            raise UsuarioNaoEncontrado
        senha_temporaria = gerar_senha_temporaria()
        self.usuarios.atualizar(usuario.com_senha_temporaria(self.senhas.gerar(senha_temporaria)))
        self.sessoes.encerrar_todas(usuario.id)
        evento = EventoDeAcesso(
            TipoDeEventoDeAcesso.SENHA_REDEFINIDA, self.relogio.agora(), usuario.id
        )
        self.acessos.registrar(evento)
        return senha_temporaria
