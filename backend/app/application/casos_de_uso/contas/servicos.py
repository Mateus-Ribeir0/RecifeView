from dataclasses import dataclass

from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.contas import CodigoDeContaRepository, EnvioDeEmail
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import GestaoDeSessoes


@dataclass(frozen=True)
class ServicosDeConta:
    usuarios: UsuarioRepository
    codigos: CodigoDeContaRepository
    senhas: HashDeSenha
    emails: EnvioDeEmail
    acessos: RegistroDeAcessos
    sessoes: GestaoDeSessoes
    relogio: Relogio
