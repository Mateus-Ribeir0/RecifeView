import pytest

from app.domain.contribuicao.enderecos import (
    canonizar_logradouro,
    reconhecer_logradouro,
    semelhanca_de_via,
    separar_via,
)
from app.domain.contribuicao.semelhanca import semelhanca_de_texto


@pytest.mark.parametrize(
    ("digitado", "esperado"),
    [
        ("R. da Esperança", "RUA DA ESPERANCA"),
        ("rua da esperanca", "RUA DA ESPERANCA"),
        ("Av. Boa Esperança", "AV BOA ESPERANCA"),
        ("Avenida Boa Esperança", "AV BOA ESPERANCA"),
        ("Travessa das Flores", "TRV DAS FLORES"),
        ("Tv das Flores", "TRV DAS FLORES"),
        ("Praça da Vitória", "PRC DA VITORIA"),
        ("Estrada do Arraial", "EST DO ARRAIAL"),
        ("1ª Travessa das Flores", "1TR DAS FLORES"),
        ("2a. Travessa das Flores", "2TR DAS FLORES"),
        ("3ª Subida da Vitória", "3SB DA VITORIA"),
        ("Flores", "FLORES"),
    ],
)
def test_escreve_a_via_como_a_central_156(digitado: str, esperado: str) -> None:
    assert canonizar_logradouro(digitado) == esperado


def test_separa_tipo_e_tira_titulos_do_nome() -> None:
    via = separar_via("AV GOVERNADOR JOAO DAS FLORES")

    assert via.tipo == "AV"
    assert via.nucleo == "JOAO FLORES"


def test_trigramas_toleram_erro_de_digitacao_mas_separam_nomes_diferentes() -> None:
    assert semelhanca_de_texto("ESPERANCA", "ESPERNCA") > 0.6
    assert semelhanca_de_texto("ESPERANCA", "CONSOLACAO") < 0.2
    assert semelhanca_de_texto("", "ESPERANCA") == 0.0


def test_primeira_e_segunda_travessa_sao_vias_diferentes() -> None:
    assert semelhanca_de_via("1TR DAS FLORES", "2TR DAS FLORES") <= 0.6
    assert semelhanca_de_via("RUA DAS FLORES", "RUA DAS FLORES") == 1.0


def test_titulo_omitido_nao_impede_de_reconhecer_a_via() -> None:
    conhecidas = ["AV GOVERNADOR JOAO DAS FLORES", "RUA DA CONSOLACAO"]

    assert reconhecer_logradouro("Avenida João das Flores", conhecidas) == conhecidas[0]


def test_erro_de_digitacao_cai_na_via_conhecida() -> None:
    conhecidas = ["RUA DA ESPERANCA", "RUA DA CONSOLACAO"]

    assert reconhecer_logradouro("Rua da Esperamca", conhecidas) == "RUA DA ESPERANCA"


def test_via_desconhecida_fica_como_foi_digitada() -> None:
    assert reconhecer_logradouro("Rua Inventada", ["RUA DA CONSOLACAO"]) == "RUA INVENTADA"


def test_empate_entre_vias_nao_escolhe_nenhuma() -> None:
    conhecidas = ["RUA DAS FLORES", "TRV DAS FLORES"]

    assert reconhecer_logradouro("Flores", conhecidas) == "FLORES"
