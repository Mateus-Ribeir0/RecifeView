from dataclasses import dataclass

from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import GestaoDeSessoes, SessaoAberta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.erros import SenhaAtualIncorreta, SenhaFraca
from app.domain.senha import validar_nova_senha
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class TrocarSenha:
    usuarios: UsuarioRepository
    senhas: HashDeSenha
    sessoes: GestaoDeSessoes
    acessos: RegistroDeAcessos
    relogio: Relogio

    def executar(self, usuario: Usuario, senha_atual: str, nova_senha: str) -> SessaoAberta:
        if not self.senhas.confere(senha_atual, usuario.hash_da_senha):
            raise SenhaAtualIncorreta
        if nova_senha == senha_atual:
            raise SenhaFraca("A nova senha precisa ser diferente da atual.")
        validar_nova_senha(nova_senha, usuario.email)
        atualizado = usuario.com_nova_senha(self.senhas.gerar(nova_senha))
        self.usuarios.atualizar(atualizado)
        self.sessoes.encerrar_todas(usuario.id)
        evento = EventoDeAcesso(
            TipoDeEventoDeAcesso.SENHA_ALTERADA, self.relogio.agora(), usuario.id
        )
        self.acessos.registrar(evento)
        return self.sessoes.abrir(atualizado)
