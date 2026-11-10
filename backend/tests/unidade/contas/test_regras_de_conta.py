from datetime import timedelta
from uuid import uuid4

import pytest

from app.domain.cidade import SituacaoPublica, faixa_de_numeracao, situacao_publica
from app.domain.conta import (
    TENTATIVAS_POR_CODIGO,
    VALIDADE_DO_CODIGO,
    CodigoDeConta,
    FinalidadeDoCodigo,
    calcular_hash_do_codigo,
    gerar_codigo,
    normalizar_nome,
)
from app.domain.email import Email
from app.domain.erros import CadastroInvalido
from app.domain.usuario import Perfil
from tests.fakes import INICIO_DOS_TESTES, criar_usuario


@pytest.mark.parametrize(
    ("digitado", "esperado"),
    [
        ("  Maria   da Silva ", "Maria da Silva"),
        ("João D'Ávila", "João D'Ávila"),
        ("Ana-Clara", "Ana-Clara"),
    ],
)
def test_nome_aceito_fica_com_espacos_simples(digitado: str, esperado: str) -> None:
    assert normalizar_nome(digitado) == esperado


@pytest.mark.parametrize("digitado", ["A", "Maria 123", "<script>", "Ana  --  Clara", "a" * 81])
def test_nome_com_numero_simbolo_ou_tamanho_errado_e_recusado(digitado: str) -> None:
    with pytest.raises(CadastroInvalido) as erro:
        normalizar_nome(digitado)
    assert erro.value.campo == "nome"


def novo_codigo(digitos: str = "123456") -> CodigoDeConta:
    identificador = uuid4()
    return CodigoDeConta(
        id=identificador,
        usuario_id=uuid4(),
        finalidade=FinalidadeDoCodigo.REDEFINIR_SENHA,
        hash_do_codigo=calcular_hash_do_codigo(identificador, digitos),
        criado_em=INICIO_DOS_TESTES,
        expira_em=INICIO_DOS_TESTES + VALIDADE_DO_CODIGO,
    )


def test_codigo_tem_seis_digitos_e_nao_e_guardado_em_claro() -> None:
    codigo = gerar_codigo()
    assert len(codigo) == 6
    assert codigo.isdigit()
    assert codigo not in novo_codigo(codigo).hash_do_codigo


def test_codigo_confere_so_com_os_digitos_certos() -> None:
    codigo = novo_codigo("123456")
    assert codigo.confere("123456")
    assert codigo.confere(" 123456 ")
    assert not codigo.confere("123457")


def test_codigo_vence_e_para_depois_de_cinco_tentativas() -> None:
    codigo = novo_codigo()
    assert codigo.pode_ser_usado(INICIO_DOS_TESTES)
    assert not codigo.pode_ser_usado(INICIO_DOS_TESTES + VALIDADE_DO_CODIGO)
    for _ in range(TENTATIVAS_POR_CODIGO):
        codigo = codigo.com_tentativa()
    assert not codigo.pode_ser_usado(INICIO_DOS_TESTES)


def test_codigo_usado_nao_vale_de_novo() -> None:
    assert not novo_codigo().usado(INICIO_DOS_TESTES).pode_ser_usado(INICIO_DOS_TESTES)


def test_reenvio_so_depois_de_um_minuto() -> None:
    codigo = novo_codigo()
    assert codigo.foi_emitido_ha_pouco(INICIO_DOS_TESTES + timedelta(seconds=30))
    assert not codigo.foi_emitido_ha_pouco(INICIO_DOS_TESTES + timedelta(seconds=61))


def test_conta_excluida_nao_guarda_nada_que_identifique() -> None:
    cidadao = criar_usuario(perfil=Perfil.CIDADAO, bairro_oficial="AFOGADOS")
    excluido = cidadao.excluido(Email("conta-x@contas-excluidas.invalid"), "hash")
    assert excluido.id == cidadao.id
    assert "gestora" not in str(excluido.email)
    assert excluido.nome == "Conta excluída"
    assert excluido.bairro_oficial is None
    assert not excluido.ativo


@pytest.mark.parametrize(
    ("numero", "faixa"),
    [
        ("120", "entre 100 e 199"),
        ("7", "entre 1 e 99"),
        ("1350-A", "entre 1300 e 1399"),
        ("S/N", None),
        ("", None),
        (None, None),
    ],
)
def test_cidadao_ve_so_a_centena_do_numero(numero: str | None, faixa: str | None) -> None:
    assert faixa_de_numeracao(numero) == faixa


@pytest.mark.parametrize(
    ("interna", "dupla_aberta", "publica"),
    [
        ("aberta", False, SituacaoPublica.RECEBIDO),
        ("aberta", True, SituacaoPublica.EM_ANALISE),
        ("em_pacote", False, SituacaoPublica.EM_ANALISE),
        ("na_base", False, SituacaoPublica.NO_PAINEL),
        ("retirada", False, SituacaoPublica.COBERTO_POR_PEDIDO_OFICIAL),
    ],
)
def test_situacao_publica(interna: str, dupla_aberta: bool, publica: SituacaoPublica) -> None:
    assert situacao_publica(interna, dupla_aberta) is publica
