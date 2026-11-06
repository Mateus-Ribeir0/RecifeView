from datetime import date, timedelta

import pytest

from app.domain.contribuicao.comparacao import (
    DIAS_DE_DUPLICIDADE,
    DIAS_DE_REINCIDENCIA,
    ClasseDaComparacao,
    Relato,
    comparar_relatos,
)

DIA = date(2026, 3, 10)
BASE = Relato(
    data=DIA,
    bairro="AFOGADOS",
    categoria="PAVIMENTACAO",
    servico_codigo="131",
    logradouro="RUA DA ESPERANCA",
    numero="100",
    numero_informado=True,
)


def relato(**mudancas: object) -> Relato:
    dados = {**BASE.__dict__, **mudancas}
    return Relato(**dados)


def test_mesmo_endereco_e_servico_em_ate_7_dias_e_a_mesma_ocorrencia() -> None:
    outro = relato(data=DIA + timedelta(days=DIAS_DE_DUPLICIDADE))

    assert comparar_relatos(BASE, outro).classe is ClasseDaComparacao.MESMA


def test_entre_8_e_29_dias_nunca_e_automatico() -> None:
    outro = relato(data=DIA + timedelta(days=DIAS_DE_DUPLICIDADE + 1))

    assert comparar_relatos(BASE, outro).classe is ClasseDaComparacao.PROVAVEL


def test_reincidencia_nunca_vira_duplicidade() -> None:
    outro = relato(data=DIA + timedelta(days=DIAS_DE_REINCIDENCIA))

    assert comparar_relatos(BASE, outro).classe is ClasseDaComparacao.DISTINTA


def test_sem_numero_vai_para_revisao_humana() -> None:
    sem_numero = relato(numero=None, numero_informado=False)

    assert comparar_relatos(sem_numero, sem_numero).classe is ClasseDaComparacao.PROVAVEL


def test_via_de_nome_generico_nunca_prova_que_o_local_e_o_mesmo() -> None:
    projetada = relato(logradouro="RUA PROJETADA")

    assert comparar_relatos(projetada, projetada).classe is not ClasseDaComparacao.MESMA


@pytest.mark.parametrize(
    ("mudanca", "classe"),
    [
        ({"numero": "110"}, ClasseDaComparacao.PROVAVEL),
        ({"numero": "900"}, ClasseDaComparacao.DISTINTA),
        ({"logradouro": "RUA DA ESPERAMCA"}, ClasseDaComparacao.PROVAVEL),
        ({"logradouro": "RUA DA CONSOLACAO"}, ClasseDaComparacao.DISTINTA),
        ({"servico_codigo": "144"}, ClasseDaComparacao.PROVAVEL),
        ({"bairro": "BOA VIAGEM"}, ClasseDaComparacao.DISTINTA),
        ({"categoria": "DRENAGEM"}, ClasseDaComparacao.DISTINTA),
    ],
)
def test_classifica_cada_diferenca(mudanca: dict[str, str], classe: ClasseDaComparacao) -> None:
    assert comparar_relatos(BASE, relato(**mudanca)).classe is classe


def test_pseudonimo_igual_confirma_o_endereco_sem_precisar_do_texto() -> None:
    a = relato(logradouro=None, numero=None, id_local="abc")
    b = relato(logradouro=None, numero=None, id_local="abc")

    assert comparar_relatos(a, b).classe is ClasseDaComparacao.MESMA


def test_pseudonimo_de_rua_sem_numero_nao_prova_o_mesmo_imovel() -> None:
    a = relato(logradouro=None, numero=None, id_local="abc", numero_informado=False)

    assert comparar_relatos(a, a).classe is ClasseDaComparacao.PROVAVEL


def test_sem_endereco_dos_dois_lados_nao_ha_o_que_comparar() -> None:
    sem_endereco = relato(logradouro=None, numero=None)

    assert comparar_relatos(sem_endereco, sem_endereco).classe is ClasseDaComparacao.DISTINTA


def test_explica_por_que_apontou() -> None:
    motivos = comparar_relatos(BASE, relato(data=DIA + timedelta(days=2))).motivos

    assert motivos == ("Mesmo endereço", "Mesmo serviço", "2 dias de diferença")
