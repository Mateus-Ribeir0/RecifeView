from datetime import timedelta

import pytest

from app.application.casos_de_uso.identificar_usuario import IdentificarUsuario
from app.application.casos_de_uso.renovar_acesso import RenovarAcesso
from app.application.casos_de_uso.sair import Sair
from app.application.sessoes import DURACAO_PADRAO_DA_SESSAO, GestaoDeSessoes
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.erros import SessaoInvalida
from app.domain.usuario import Usuario
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from tests.fakes import AcessosEmMemoria, RelogioFixo, SessoesEmMemoria, UsuariosEmMemoria


def test_renovar_com_sessao_ativa_emite_novo_token(
    usuarios: UsuariosEmMemoria, usuario: Usuario, gestao_de_sessoes: GestaoDeSessoes
) -> None:
    aberta = gestao_de_sessoes.abrir(usuario)
    acesso = RenovarAcesso(usuarios, gestao_de_sessoes).executar(aberta.token_de_sessao)
    assert acesso.usuario.id == usuario.id


@pytest.mark.parametrize("token", [None, "", "token-que-nunca-existiu"])
def test_renovar_sem_sessao_valida_e_recusado(
    usuarios: UsuariosEmMemoria, gestao_de_sessoes: GestaoDeSessoes, token: str | None
) -> None:
    with pytest.raises(SessaoInvalida):
        RenovarAcesso(usuarios, gestao_de_sessoes).executar(token)


def test_sessao_expira_depois_da_duracao(
    usuarios: UsuariosEmMemoria,
    usuario: Usuario,
    gestao_de_sessoes: GestaoDeSessoes,
    relogio: RelogioFixo,
) -> None:
    aberta = gestao_de_sessoes.abrir(usuario)
    relogio.avancar(DURACAO_PADRAO_DA_SESSAO)
    with pytest.raises(SessaoInvalida):
        RenovarAcesso(usuarios, gestao_de_sessoes).executar(aberta.token_de_sessao)


def test_sair_revoga_a_sessao_e_registra_a_saida(
    usuarios: UsuariosEmMemoria,
    usuario: Usuario,
    gestao_de_sessoes: GestaoDeSessoes,
    acessos: AcessosEmMemoria,
    relogio: RelogioFixo,
) -> None:
    aberta = gestao_de_sessoes.abrir(usuario)

    Sair(gestao_de_sessoes, acessos, relogio).executar(aberta.token_de_sessao)

    assert acessos.tipos() == [TipoDeEventoDeAcesso.SAIDA]
    with pytest.raises(SessaoInvalida):
        RenovarAcesso(usuarios, gestao_de_sessoes).executar(aberta.token_de_sessao)


def test_sair_sem_sessao_nao_faz_nada(
    gestao_de_sessoes: GestaoDeSessoes, acessos: AcessosEmMemoria, relogio: RelogioFixo
) -> None:
    Sair(gestao_de_sessoes, acessos, relogio).executar(None)
    assert acessos.eventos == []


def test_identificar_usuario_pelo_token_de_acesso(
    usuarios: UsuariosEmMemoria,
    usuario: Usuario,
    emissor: EmissorDeTokenJwt,
    relogio: RelogioFixo,
) -> None:
    token = emissor.emitir(usuario, relogio.agora())
    identificado = IdentificarUsuario(usuarios, emissor, relogio).executar(token.valor)
    assert identificado.id == usuario.id


def test_token_de_acesso_vencido_e_recusado(
    usuarios: UsuariosEmMemoria,
    usuario: Usuario,
    emissor: EmissorDeTokenJwt,
    relogio: RelogioFixo,
) -> None:
    token = emissor.emitir(usuario, relogio.agora())
    relogio.avancar(timedelta(minutes=15))
    with pytest.raises(SessaoInvalida):
        IdentificarUsuario(usuarios, emissor, relogio).executar(token.valor)


def test_token_assinado_com_outro_segredo_e_recusado(
    usuarios: UsuariosEmMemoria, usuario: Usuario, relogio: RelogioFixo
) -> None:
    falsificado = EmissorDeTokenJwt("outro-segredo-com-mais-de-trinta-e-dois-chars", timedelta(1))
    token = falsificado.emitir(usuario, relogio.agora())
    verdadeiro = EmissorDeTokenJwt("segredo-verdadeiro-com-mais-de-trinta-e-dois", timedelta(1))
    with pytest.raises(SessaoInvalida):
        IdentificarUsuario(usuarios, verdadeiro, relogio).executar(token.valor)


def test_encerrar_todas_revoga_cada_sessao_do_usuario(
    usuario: Usuario, gestao_de_sessoes: GestaoDeSessoes, sessoes_em_memoria: SessoesEmMemoria
) -> None:
    gestao_de_sessoes.abrir(usuario)
    gestao_de_sessoes.abrir(usuario)
    gestao_de_sessoes.encerrar_todas(usuario.id)
    assert sessoes_em_memoria.ativas() == []
