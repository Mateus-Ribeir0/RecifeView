from datetime import timedelta

import pytest

from app.domain.email import Email
from app.domain.erros import EmailInvalido, SenhaFraca
from app.domain.senha import validar_nova_senha
from app.domain.usuario import DURACAO_DO_BLOQUEIO, TENTATIVAS_ANTES_DO_BLOQUEIO
from tests.fakes import INICIO_DOS_TESTES, criar_usuario


def test_email_e_normalizado_para_minusculas_sem_espacos() -> None:
    assert str(Email("  Gestora@Recife.PE.gov.br ")) == "gestora@recife.pe.gov.br"


@pytest.mark.parametrize(
    "texto", ["", "sem-arroba", "a@b", "duas@@arrobas.com", "x" * 250 + "@a.com"]
)
def test_email_recusa_formato_invalido(texto: str) -> None:
    with pytest.raises(EmailInvalido):
        Email(texto)


@pytest.mark.parametrize(
    ("senha", "trecho_do_motivo"),
    [
        ("curtinha", "pelo menos 12"),
        ("a" * 129, "no máximo 128"),
        ("aaaaaaaaaaaaaa", "único caractere"),
        ("minha-gestora-2026", "antes do @"),
    ],
)
def test_nova_senha_fora_das_regras_e_recusada(senha: str, trecho_do_motivo: str) -> None:
    with pytest.raises(SenhaFraca, match=trecho_do_motivo):
        validar_nova_senha(senha, Email("gestora@recife.pe.gov.br"))


def test_nova_senha_dentro_das_regras_e_aceita() -> None:
    validar_nova_senha("ponte-boa-vista-1840", Email("gestora@recife.pe.gov.br"))


def test_nome_curto_do_email_nao_impede_a_senha() -> None:
    validar_nova_senha("uma senha com ana dentro", Email("ana@recife.pe.gov.br"))


def test_conta_bloqueia_na_quinta_falha_seguida() -> None:
    usuario = criar_usuario()
    for _ in range(TENTATIVAS_ANTES_DO_BLOQUEIO - 1):
        usuario = usuario.com_falha_de_entrada(INICIO_DOS_TESTES)
        assert usuario.fim_do_bloqueio(INICIO_DOS_TESTES) is None

    bloqueado = usuario.com_falha_de_entrada(INICIO_DOS_TESTES)

    assert bloqueado.fim_do_bloqueio(INICIO_DOS_TESTES) == INICIO_DOS_TESTES + DURACAO_DO_BLOQUEIO
    assert bloqueado.tentativas_falhas == 0


def test_bloqueio_termina_depois_da_duracao() -> None:
    bloqueado = criar_usuario(bloqueado_ate=INICIO_DOS_TESTES + DURACAO_DO_BLOQUEIO)
    depois = INICIO_DOS_TESTES + DURACAO_DO_BLOQUEIO + timedelta(seconds=1)
    assert bloqueado.fim_do_bloqueio(depois) is None


def test_nova_senha_libera_a_conta_e_dispensa_a_troca() -> None:
    usuario = criar_usuario(deve_trocar_senha=True, tentativas_falhas=3)
    atualizado = usuario.com_nova_senha("hash:nova")
    assert not atualizado.deve_trocar_senha
    assert atualizado.tentativas_falhas == 0
