from dataclasses import dataclass

from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.relogio import Relogio
from app.application.portas.usuarios import UsuarioRepository
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.email import Email
from app.domain.erros import AcessoNegado, UsuarioNaoEncontrado
from app.domain.usuario import PERFIS_DA_GESTAO, Perfil, Usuario


@dataclass(frozen=True)
class MudarPerfil:
    """Só troca entre os dois perfis da gestão: cidadão e órgão têm caminhos próprios."""

    usuarios: UsuarioRepository
    acessos: RegistroDeAcessos
    relogio: Relogio

    def executar(self, email: str, perfil: Perfil) -> Usuario:
        usuario = self.usuarios.buscar_por_email(Email(email))
        if usuario is None:
            raise UsuarioNaoEncontrado
        if not usuario.e_da_gestao or perfil not in PERFIS_DA_GESTAO:
            raise AcessoNegado
        alterado = usuario.com_perfil(perfil)
        self.usuarios.atualizar(alterado)
        evento = EventoDeAcesso(
            TipoDeEventoDeAcesso.CONTA_ALTERADA, self.relogio.agora(), usuario.id
        )
        self.acessos.registrar(evento)
        return alterado
