from collections.abc import Iterator
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.entrar import Entrar
from app.application.casos_de_uso.identificar_usuario import IdentificarUsuario
from app.application.casos_de_uso.renovar_acesso import RenovarAcesso
from app.application.casos_de_uso.sair import Sair
from app.application.casos_de_uso.trocar_senha import TrocarSenha
from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import EmissorDeTokenDeAcesso, HashDeSenha
from app.application.portas.sessoes import SessaoRepository
from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import GestaoDeSessoes
from app.domain.erros import ErroDeDominio, SessaoInvalida
from app.domain.usuario import Usuario
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from app.infrastructure.settings import Configuracao


@dataclass(frozen=True)
class Seguranca:
    senhas: HashDeSenha
    emissor: EmissorDeTokenDeAcesso
    relogio: Relogio
    duracao_da_sessao: timedelta


@dataclass(frozen=True)
class Repositorios:
    usuarios: UsuarioRepository
    sessoes: SessaoRepository
    acessos: RegistroDeAcessos


def obter_configuracao(request: Request) -> Configuracao:
    configuracao: Configuracao = request.app.state.configuracao
    return configuracao


def obter_seguranca(request: Request) -> Seguranca:
    seguranca: Seguranca = request.app.state.seguranca
    return seguranca


def abrir_transacao(request: Request) -> Iterator[Session]:
    fabrica: sessionmaker[Session] = request.app.state.fabrica_de_sessoes
    with fabrica() as sessao:
        try:
            yield sessao
        except ErroDeDominio:
            # Uma entrada recusada também precisa gravar a tentativa e o evento de auditoria.
            sessao.commit()
            raise
        except Exception:
            sessao.rollback()
            raise
        else:
            sessao.commit()


def obter_repositorios(sessao: Annotated[Session, Depends(abrir_transacao)]) -> Repositorios:
    return Repositorios(
        usuarios=UsuarioRepositorySql(sessao),
        sessoes=SessaoRepositorySql(sessao),
        acessos=RegistroDeAcessosSql(sessao),
    )


ConfiguracaoDep = Annotated[Configuracao, Depends(obter_configuracao)]
SegurancaDep = Annotated[Seguranca, Depends(obter_seguranca)]
RepositoriosDep = Annotated[Repositorios, Depends(obter_repositorios)]


def obter_gestao_de_sessoes(
    repositorios: RepositoriosDep, seguranca: SegurancaDep
) -> GestaoDeSessoes:
    return GestaoDeSessoes(
        repositorios.sessoes, seguranca.emissor, seguranca.relogio, seguranca.duracao_da_sessao
    )


GestaoDeSessoesDep = Annotated[GestaoDeSessoes, Depends(obter_gestao_de_sessoes)]


def obter_entrar(
    repositorios: RepositoriosDep, seguranca: SegurancaDep, sessoes: GestaoDeSessoesDep
) -> Entrar:
    return Entrar(
        repositorios.usuarios, seguranca.senhas, sessoes, repositorios.acessos, seguranca.relogio
    )


def obter_renovar_acesso(
    repositorios: RepositoriosDep, sessoes: GestaoDeSessoesDep
) -> RenovarAcesso:
    return RenovarAcesso(repositorios.usuarios, sessoes)


def obter_sair(
    repositorios: RepositoriosDep, seguranca: SegurancaDep, sessoes: GestaoDeSessoesDep
) -> Sair:
    return Sair(sessoes, repositorios.acessos, seguranca.relogio)


def obter_trocar_senha(
    repositorios: RepositoriosDep, seguranca: SegurancaDep, sessoes: GestaoDeSessoesDep
) -> TrocarSenha:
    return TrocarSenha(
        repositorios.usuarios, seguranca.senhas, sessoes, repositorios.acessos, seguranca.relogio
    )


def obter_identificar_usuario(
    repositorios: RepositoriosDep, seguranca: SegurancaDep
) -> IdentificarUsuario:
    return IdentificarUsuario(repositorios.usuarios, seguranca.emissor, seguranca.relogio)


esquema_bearer = HTTPBearer(auto_error=False)


def obter_usuario_atual(
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
    identificar: Annotated[IdentificarUsuario, Depends(obter_identificar_usuario)],
) -> Usuario:
    if credenciais is None:
        raise SessaoInvalida
    return identificar.executar(credenciais.credentials)


EntrarDep = Annotated[Entrar, Depends(obter_entrar)]
RenovarAcessoDep = Annotated[RenovarAcesso, Depends(obter_renovar_acesso)]
SairDep = Annotated[Sair, Depends(obter_sair)]
TrocarSenhaDep = Annotated[TrocarSenha, Depends(obter_trocar_senha)]
UsuarioAtualDep = Annotated[Usuario, Depends(obter_usuario_atual)]
