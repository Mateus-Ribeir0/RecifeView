from datetime import date
from uuid import uuid4

from app.domain.contribuicao.comparacao import ClasseDaComparacao, Relato
from app.domain.contribuicao.conferencia import (
    ConferenciaDoArquivo,
    RelatoGuardado,
    chave_da_contribuicao,
)
from app.domain.fontes import Fonte
from app.domain.importacao.chaves import GeradorDeChaves, OrdemPorConteudo
from app.domain.importacao.registro import EnderecoDaLinha, RegistroDeDemanda

DIA = date(2026, 3, 10)


def registro(bairro: str = "AFOGADOS", id_local: str | None = None) -> RegistroDeDemanda:
    valores = dict.fromkeys(RegistroDeDemanda._fields)
    valores.update(
        chave_registro=1,
        assinatura=1,
        fonte=Fonte.CENTRAL_156.value,
        data_abertura=DIA,
        categoria="PAVIMENTACAO",
        servico_codigo="131",
        bairro_oficial=bairro,
        id_local=id_local,
        numero_informado=True,
    )
    return RegistroDeDemanda(**valores)  # type: ignore[arg-type]


def guardado() -> RelatoGuardado:
    relato = Relato(
        data=DIA,
        bairro="AFOGADOS",
        categoria="PAVIMENTACAO",
        servico_codigo="131",
        logradouro="RUA DA ESPERANCA",
        numero="100",
        numero_informado=True,
    )
    return RelatoGuardado(uuid4(), relato, "Buraco na rua, Afogados")


def test_linha_do_arquivo_coincide_com_o_relato_do_formulario() -> None:
    conferencia = ConferenciaDoArquivo([guardado()])

    conferencia.conferir(registro(), EnderecoDaLinha("Rua da Esperança", "100"))

    resultado = conferencia.concluir()
    assert resultado.resumir()["certas"] == 1
    assert resultado.coincidencias[0].classe is ClasseDaComparacao.MESMA


def test_a_descricao_nao_leva_o_endereco() -> None:
    conferencia = ConferenciaDoArquivo([guardado()])

    conferencia.conferir(registro(), EnderecoDaLinha("Rua da Esperança", "100"))

    descricao = conferencia.concluir().coincidencias[0].descricao
    assert "ESPERANCA" not in descricao.upper()
    assert "100" not in descricao


def test_outro_bairro_nem_chega_a_ser_comparado() -> None:
    conferencia = ConferenciaDoArquivo([guardado()])

    conferencia.conferir(registro("BOA VIAGEM"), EnderecoDaLinha("Rua da Esperança", "100"))

    assert conferencia.concluir().resumir() == {
        "comparadas": 0,
        "sem_endereco": 0,
        "certas": 0,
        "provaveis": 0,
    }


def test_arquivo_sem_endereco_e_contado_e_nao_vira_coincidencia() -> None:
    conferencia = ConferenciaDoArquivo([guardado()])

    conferencia.conferir(registro(), None)

    resumo = conferencia.concluir().resumir()
    assert resumo["sem_endereco"] == 1
    assert resumo["certas"] == 0


def test_cada_relato_conta_uma_vez_mesmo_com_varias_linhas_iguais() -> None:
    conferencia = ConferenciaDoArquivo([guardado()])

    for _ in range(3):
        conferencia.conferir(registro(), EnderecoDaLinha("Rua da Esperança", "100"))

    assert len(conferencia.concluir().coincidencias) == 1


def test_chave_da_contribuicao_e_a_mesma_que_a_importacao_gera() -> None:
    contribuicao_id = uuid4()
    gerador = GeradorDeChaves(OrdemPorConteudo())

    gerada = gerador.gerar(Fonte.FORMULARIO.value, {"id_registro": str(contribuicao_id)}, 1)

    assert gerada.valor == chave_da_contribuicao(contribuicao_id)
