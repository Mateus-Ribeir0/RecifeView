import pytest

from app.application.casos_de_uso.entrar import Entrar
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.erros import ContaBloqueada, ContaInativa, CredenciaisInvalidas
from app.domain.usuario import TENTATIVAS_ANTES_DO_BLOQUEIO, Usuario
from tests.fakes import (
    SENHA_DE_TESTE,
    AcessosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)


@pytest.fixture
def entrar(
    usuarios: UsuariosEmMemoria,
    senhas: HashDeSenhaDeTeste,
    gestao_de_sessoes: GestaoDeSessoes,
    acessos: AcessosEmMemoria,
    relogio: RelogioFixo,
) -> Entrar:
    return Entrar(usuarios, senhas, gestao_de_sessoes, acessos, relogio)


def test_entrada_aceita_abre_sessao_e_registra_o_acesso(
    entrar: Entrar,
    usuario: Usuario,
    sessoes_em_memoria: SessoesEmMemoria,
    acessos: AcessosEmMemoria,
) -> None:
    sessao = entrar.executar("Gestora@Recife.pe.gov.br", SENHA_DE_TESTE)

    assert sessao.acesso.usuario.id == usuario.id
    assert sessao.token_de_sessao
    assert len(sessoes_em_memoria.ativas()) == 1
    assert acessos.tipos() == [TipoDeEventoDeAcesso.ENTRADA]


def test_sessao_guarda_so_o_hash_do_token(
    entrar: Entrar, sessoes_em_memoria: SessoesEmMemoria
) -> None:
    sessao = entrar.executar("gestora@recife.pe.gov.br", SENHA_DE_TESTE)
    guardada = sessoes_em_memoria.ativas()[0]
    assert guardada.hash_do_token != sessao.token_de_sessao


def test_email_desconhecido_simula_conferencia_e_nao_revela_que_nao_existe(
    entrar: Entrar, senhas: HashDeSenhaDeTeste, acessos: AcessosEmMemoria
) -> None:
    with pytest.raises(CredenciaisInvalidas):
        entrar.executar("ninguem@recife.pe.gov.br", SENHA_DE_TESTE)
    assert senhas.conferencias_simuladas == 1
    assert acessos.eventos[0].usuario_id is None


def test_email_mal_formado_tem_a_mesma_resposta_de_email_desconhecido(entrar: Entrar) -> None:
    with pytest.raises(CredenciaisInvalidas):
        entrar.executar("nao-e-email", SENHA_DE_TESTE)


def test_senha_errada_conta_tentativa(
    entrar: Entrar, usuarios: UsuariosEmMemoria, usuario: Usuario
) -> None:
    with pytest.raises(CredenciaisInvalidas):
        entrar.executar("gestora@recife.pe.gov.br", "senha-errada")
    assert usuarios.por_id[usuario.id].tentativas_falhas == 1


def test_quinta_senha_errada_bloqueia_a_conta(entrar: Entrar, acessos: AcessosEmMemoria) -> None:
    for _ in range(TENTATIVAS_ANTES_DO_BLOQUEIO - 1):
        with pytest.raises(CredenciaisInvalidas):
            entrar.executar("gestora@recife.pe.gov.br", "senha-errada")

    with pytest.raises(ContaBloqueada):
        entrar.executar("gestora@recife.pe.gov.br", "senha-errada")

    assert acessos.tipos()[-1] == TipoDeEventoDeAcesso.CONTA_BLOQUEADA


def test_conta_bloqueada_recusa_ate_a_senha_certa(entrar: Entrar) -> None:
    for _ in range(TENTATIVAS_ANTES_DO_BLOQUEIO):
        with pytest.raises((CredenciaisInvalidas, ContaBloqueada)):
            entrar.executar("gestora@recife.pe.gov.br", "senha-errada")

    with pytest.raises(ContaBloqueada):
        entrar.executar("gestora@recife.pe.gov.br", SENHA_DE_TESTE)


def test_conta_inativa_com_senha_certa_e_recusada(
    senhas: HashDeSenhaDeTeste,
    gestao_de_sessoes: GestaoDeSessoes,
    acessos: AcessosEmMemoria,
    relogio: RelogioFixo,
) -> None:
    inativa = criar_usuario(ativo=False)
    entrar = Entrar(UsuariosEmMemoria(inativa), senhas, gestao_de_sessoes, acessos, relogio)
    with pytest.raises(ContaInativa):
        entrar.executar("gestora@recife.pe.gov.br", SENHA_DE_TESTE)
