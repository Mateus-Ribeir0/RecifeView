import pytest

from app.application.casos_de_uso.cadastrar_usuario import CadastrarUsuario
from app.application.casos_de_uso.redefinir_senha import RedefinirSenha
from app.application.casos_de_uso.trocar_senha import TrocarSenha
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.email import Email
from app.domain.erros import EmailJaCadastrado, SenhaAtualIncorreta, SenhaFraca
from app.domain.senha import TAMANHO_MINIMO_DA_SENHA
from app.domain.usuario import Perfil, Usuario
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from tests.fakes import (
    SENHA_DE_TESTE,
    AcessosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
)


@pytest.fixture
def trocar_senha(
    usuarios: UsuariosEmMemoria,
    senhas: HashDeSenhaDeTeste,
    gestao_de_sessoes: GestaoDeSessoes,
    acessos: AcessosEmMemoria,
    relogio: RelogioFixo,
) -> TrocarSenha:
    return TrocarSenha(usuarios, senhas, gestao_de_sessoes, acessos, relogio)


def test_trocar_senha_grava_o_novo_hash_e_abre_sessao_nova(
    trocar_senha: TrocarSenha,
    usuario: Usuario,
    usuarios: UsuariosEmMemoria,
    gestao_de_sessoes: GestaoDeSessoes,
    sessoes_em_memoria: SessoesEmMemoria,
) -> None:
    antiga = gestao_de_sessoes.abrir(usuario)

    nova = trocar_senha.executar(usuario, SENHA_DE_TESTE, "ponte-boa-vista-1840")

    assert usuarios.por_id[usuario.id].hash_da_senha == "hash:ponte-boa-vista-1840"
    ativas = sessoes_em_memoria.ativas()
    assert len(ativas) == 1
    assert ativas[0].hash_do_token != antiga.token_de_sessao
    assert nova.acesso.usuario.deve_trocar_senha is False


def test_trocar_senha_exige_a_senha_atual(trocar_senha: TrocarSenha, usuario: Usuario) -> None:
    with pytest.raises(SenhaAtualIncorreta):
        trocar_senha.executar(usuario, "nao-e-a-atual", "ponte-boa-vista-1840")


def test_nova_senha_igual_a_atual_e_recusada(trocar_senha: TrocarSenha, usuario: Usuario) -> None:
    with pytest.raises(SenhaFraca, match="diferente da atual"):
        trocar_senha.executar(usuario, SENHA_DE_TESTE, SENHA_DE_TESTE)


def test_troca_registra_evento(
    trocar_senha: TrocarSenha, usuario: Usuario, acessos: AcessosEmMemoria
) -> None:
    trocar_senha.executar(usuario, SENHA_DE_TESTE, "ponte-boa-vista-1840")
    assert acessos.tipos() == [TipoDeEventoDeAcesso.SENHA_ALTERADA]


def test_cadastro_cria_conta_com_senha_temporaria_obrigatoria(senhas: HashDeSenhaDeTeste) -> None:
    usuarios = UsuariosEmMemoria()
    resultado = CadastrarUsuario(usuarios, senhas).executar(
        "Nova.Gestora@Recife.pe.gov.br", " Nova Gestora ", Perfil.GESTOR
    )
    criado = usuarios.buscar_por_email(Email("nova.gestora@recife.pe.gov.br"))
    assert criado is not None
    assert criado.deve_trocar_senha
    assert criado.nome == "Nova Gestora"
    assert len(resultado.senha_temporaria) >= TAMANHO_MINIMO_DA_SENHA
    assert senhas.confere(resultado.senha_temporaria, criado.hash_da_senha)


def test_cadastro_recusa_email_repetido(
    usuarios: UsuariosEmMemoria, senhas: HashDeSenhaDeTeste
) -> None:
    with pytest.raises(EmailJaCadastrado):
        CadastrarUsuario(usuarios, senhas).executar(
            "gestora@recife.pe.gov.br", "Outra", Perfil.GESTOR
        )


def test_redefinir_senha_exige_troca_e_derruba_as_sessoes(
    usuarios: UsuariosEmMemoria,
    usuario: Usuario,
    senhas: HashDeSenhaDeTeste,
    gestao_de_sessoes: GestaoDeSessoes,
    sessoes_em_memoria: SessoesEmMemoria,
    acessos: AcessosEmMemoria,
    relogio: RelogioFixo,
) -> None:
    gestao_de_sessoes.abrir(usuario)
    redefinicao = RedefinirSenha(usuarios, senhas, gestao_de_sessoes, acessos, relogio)

    temporaria = redefinicao.executar("gestora@recife.pe.gov.br")

    atualizado = usuarios.por_id[usuario.id]
    assert atualizado.deve_trocar_senha
    assert senhas.confere(temporaria, atualizado.hash_da_senha)
    assert sessoes_em_memoria.ativas() == []


def test_argon2_confere_a_senha_certa_e_recusa_as_outras() -> None:
    argon2 = HashDeSenhaArgon2()
    hash_da_senha = argon2.gerar("ponte-boa-vista-1840")
    assert hash_da_senha.startswith("$argon2id$")
    assert argon2.confere("ponte-boa-vista-1840", hash_da_senha)
    assert not argon2.confere("outra-senha-qualquer", hash_da_senha)
    assert not argon2.confere("ponte-boa-vista-1840", "hash-corrompido")
