from dataclasses import dataclass
from datetime import datetime
from typing import NoReturn
from uuid import UUID

from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import GestaoDeSessoes, SessaoAberta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.email import Email
from app.domain.erros import ContaBloqueada, ContaInativa, CredenciaisInvalidas, EmailInvalido
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class Entrar:
    usuarios: UsuarioRepository
    senhas: HashDeSenha
    sessoes: GestaoDeSessoes
    acessos: RegistroDeAcessos
    relogio: Relogio

    def executar(self, email: str, senha: str) -> SessaoAberta:
        agora = self.relogio.agora()
        usuario = self._buscar_usuario(email)
        if usuario is None:
            self.senhas.simular_conferencia(senha)
            self._registrar(TipoDeEventoDeAcesso.ENTRADA_RECUSADA, agora)
            raise CredenciaisInvalidas
        if (fim_do_bloqueio := usuario.fim_do_bloqueio(agora)) is not None:
            raise ContaBloqueada(fim_do_bloqueio)
        if not self.senhas.confere(senha, usuario.hash_da_senha):
            self._recusar(usuario, agora)
        if not usuario.ativo:
            raise ContaInativa
        return self._aceitar(usuario, agora)

    def _buscar_usuario(self, email: str) -> Usuario | None:
        try:
            return self.usuarios.buscar_por_email(Email(email))
        except EmailInvalido:
            return None

    def _recusar(self, usuario: Usuario, agora: datetime) -> NoReturn:
        com_falha = usuario.com_falha_de_entrada(agora)
        self.usuarios.atualizar(com_falha)
        if (fim_do_bloqueio := com_falha.fim_do_bloqueio(agora)) is not None:
            self._registrar(TipoDeEventoDeAcesso.CONTA_BLOQUEADA, agora, usuario.id)
            raise ContaBloqueada(fim_do_bloqueio)
        self._registrar(TipoDeEventoDeAcesso.ENTRADA_RECUSADA, agora, usuario.id)
        raise CredenciaisInvalidas

    def _aceitar(self, usuario: Usuario, agora: datetime) -> SessaoAberta:
        aceito = usuario.com_entrada_aceita()
        self.usuarios.atualizar(aceito)
        self._registrar(TipoDeEventoDeAcesso.ENTRADA, agora, usuario.id)
        return self.sessoes.abrir(aceito)

    def _registrar(
        self, tipo: TipoDeEventoDeAcesso, agora: datetime, usuario_id: UUID | None = None
    ) -> None:
        self.acessos.registrar(EventoDeAcesso(tipo, agora, usuario_id))
