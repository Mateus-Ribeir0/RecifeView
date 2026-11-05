from datetime import date

import pytest

from app.domain.fontes import Fonte
from app.domain.importacao.chaves import OrdemPorConteudo, chave_base
from app.domain.importacao.datas import FormatoDeData
from app.domain.importacao.decisoes import (
    ACEITAR_COMO_NOVO,
    DEIXAR_VAZIO,
    DESCARTAR_LINHA,
    Decisoes,
    PoliticaDeDatasInvalidas,
    PoliticaDeDuplicados,
    PoliticaDeRepetidos,
)
from app.domain.importacao.layouts import CodigoDoLayout
from app.domain.importacao.normalizador import (
    NormalizadorDeLinhas,
    PlanoDeNormalizacao,
    Referencias,
)
from app.domain.importacao.registro import RegistroDeDemanda
from app.domain.importacao.relatorio import Correcao, MotivoDeDescarte

BAIRROS = {"AFOGADOS": "5", "VARZEA": "4", "COHAB": "6"}
COLUNAS_156 = ("GRUPO", "SERVICO", "COD", "BAIRRO", "DATA", "SITUACAO", "ULT", "LOGRADOURO", "NUM")
MAPEAMENTO_156 = {
    "GRUPO": "categoria",
    "SERVICO": "servico",
    "COD": "servico_codigo",
    "BAIRRO": "bairro",
    "DATA": "data_abertura",
    "SITUACAO": "situacao",
    "ULT": "data_ult_movimento",
    "LOGRADOURO": "logradouro",
    "NUM": "numero",
}
LINHA_156 = [
    "Iluminação Pública",
    "Lâmpada apagada",
    "77",
    "Afogados",
    "2026-02-10",
    "ATENDIDA",
    "2026-02-14",
    "RUA DO TESTE",
    "10",
]


def criar_normalizador(
    decisoes: Decisoes | None = None,
    layout: CodigoDoLayout = CodigoDoLayout.PORTAL_156,
    vocabularios: dict[tuple[str, str], frozenset[str]] | None = None,
    sal: str | None = None,
    ordem: OrdemPorConteudo | None = None,
) -> NormalizadorDeLinhas:
    plano = PlanoDeNormalizacao(
        colunas=COLUNAS_156,
        layout=layout,
        decisoes=decisoes or Decisoes(fonte=Fonte.CENTRAL_156, mapeamento=MAPEAMENTO_156),
        arquivo_origem="156_2026",
        data_do_retrato=date(2026, 11, 5),
        importacao_id=7,
        sal=sal,
    )
    return NormalizadorDeLinhas(
        plano, Referencias(BAIRROS, vocabularios or {}), ordem or OrdemPorConteudo()
    )


def normalizar_arquivo(
    linhas: list[list[str]], decisoes: Decisoes | None = None
) -> tuple[list[RegistroDeDemanda | None], NormalizadorDeLinhas]:
    ordem = OrdemPorConteudo()
    primeira_passada = criar_normalizador(decisoes, ordem=ordem)
    for linha in linhas:
        primeira_passada.anotar(linha)
    ordem.fechar()
    normalizador = criar_normalizador(decisoes, ordem=ordem)
    return [normalizador.normalizar(linha) for linha in linhas], normalizador


def decisoes_156(**extras: object) -> Decisoes:
    return Decisoes(fonte=Fonte.CENTRAL_156, mapeamento=MAPEAMENTO_156, **extras)  # type: ignore[arg-type]


def test_linha_do_156_vira_registro_normalizado() -> None:
    normalizador = criar_normalizador()

    registro = normalizador.normalizar(LINHA_156)

    assert registro is not None
    assert registro.fonte == "156_EMLURB"
    assert registro.categoria == "ILUMINACAO PUBLICA"
    assert registro.bairro_oficial == "AFOGADOS"
    assert registro.rpa == "5"
    assert registro.dias_ate_movimento == 4
    assert registro.ano == 2026
    assert registro.ano_do_arquivo == 2026
    assert registro.numero_informado is True


def test_sem_sal_o_registro_fica_sem_id_local_e_a_conta_aparece_no_relatorio() -> None:
    normalizador = criar_normalizador()

    registro = normalizador.normalizar(LINHA_156)

    assert registro is not None
    assert registro.id_local is None
    assert normalizador.relatorio.sem_id_local == 1


def test_com_sal_o_endereco_vira_pseudonimo_e_nao_sai_no_registro() -> None:
    registro = criar_normalizador(sal="sal-de-teste").normalizar(LINHA_156)

    assert registro is not None
    assert registro.id_local is not None
    assert len(registro.id_local) == 12
    assert "RUA DO TESTE" not in str(registro)


def test_prazo_negativo_e_anulado_e_marcado() -> None:
    linha = [*LINHA_156]
    linha[6] = "2026-02-01"
    normalizador = criar_normalizador()

    registro = normalizador.normalizar(linha)

    assert registro is not None
    assert registro.dias_ate_movimento is None
    assert registro.prazo_negativo is True
    assert normalizador.relatorio.correcoes[Correcao.PRAZO_NEGATIVO] == 1


def test_categoria_do_156_com_grafia_antiga_e_unificada() -> None:
    linha = [*LINHA_156]
    linha[0] = "TERRAPLANAGEN"
    normalizador = criar_normalizador()

    registro = normalizador.normalizar(linha)

    assert registro is not None
    assert registro.categoria == "TERRAPLENAGEM"
    assert normalizador.relatorio.correcoes[Correcao.CATEGORIA_UNIFICADA] == 1


def test_bairro_desconhecido_sem_decisao_entra_no_relatorio() -> None:
    linha = [*LINHA_156]
    linha[3] = "Afogadoss"
    normalizador = criar_normalizador()

    registro = normalizador.normalizar(linha)

    assert registro is not None
    assert registro.bairro_oficial is None
    assert normalizador.relatorio.bairros_desconhecidos["AFOGADOSS"] == 1


def test_bairro_associado_pela_pessoa_vale_na_carga() -> None:
    linha = [*LINHA_156]
    linha[3] = "Afogadoss"
    decisoes = decisoes_156(substituicoes={"bairro": {"AFOGADOSS": "AFOGADOS"}})

    registro = criar_normalizador(decisoes).normalizar(linha)

    assert registro is not None
    assert registro.bairro_oficial == "AFOGADOS"


def test_bairro_recusado_pela_pessoa_descarta_a_linha() -> None:
    linha = [*LINHA_156]
    linha[3] = "Outra cidade"
    decisoes = decisoes_156(padrao_para_valores={"bairro": DESCARTAR_LINHA})
    normalizador = criar_normalizador(decisoes)

    assert normalizador.normalizar(linha) is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.VALOR_RECUSADO] == 1


def test_bairro_deixado_vazio_nao_pede_nova_decisao() -> None:
    linha = [*LINHA_156]
    linha[3] = "Outra cidade"
    decisoes = decisoes_156(padrao_para_valores={"bairro": DEIXAR_VAZIO})
    normalizador = criar_normalizador(decisoes)

    registro = normalizador.normalizar(linha)

    assert registro is not None
    assert registro.bairro_oficial is None
    assert not normalizador.relatorio.bairros_desconhecidos


def test_apelido_de_bairro_vira_bairro_oficial() -> None:
    linha = [*LINHA_156]
    linha[3] = "Cohab Ibura de Cima"

    registro = criar_normalizador().normalizar(linha)

    assert registro is not None
    assert registro.bairro_oficial == "COHAB"


def test_valor_fora_do_vocabulario_vira_valor_novo() -> None:
    vocabulario = {("156_EMLURB", "categoria"): frozenset({"DRENAGEM"})}
    normalizador = criar_normalizador(vocabularios=vocabulario)

    normalizador.normalizar(LINHA_156)

    assert normalizador.relatorio.valores_novos["categoria"]["ILUMINACAO PUBLICA"] == 1


def test_valor_novo_aceito_nao_pede_decisao() -> None:
    vocabulario = {("156_EMLURB", "categoria"): frozenset({"DRENAGEM"})}
    decisoes = decisoes_156(substituicoes={"categoria": {"ILUMINACAO PUBLICA": ACEITAR_COMO_NOVO}})
    normalizador = criar_normalizador(decisoes, vocabularios=vocabulario)

    registro = normalizador.normalizar(LINHA_156)

    assert registro is not None
    assert registro.categoria == "ILUMINACAO PUBLICA"
    assert not normalizador.relatorio.valores_novos


def test_valor_novo_pode_ser_associado_a_um_conhecido() -> None:
    vocabulario = {("156_EMLURB", "categoria"): frozenset({"DRENAGEM"})}
    decisoes = decisoes_156(substituicoes={"categoria": {"ILUMINACAO PUBLICA": "DRENAGEM"}})

    registro = criar_normalizador(decisoes, vocabularios=vocabulario).normalizar(LINHA_156)

    assert registro is not None
    assert registro.categoria == "DRENAGEM"


def test_linha_sem_data_de_abertura_e_descartada() -> None:
    linha = [*LINHA_156]
    linha[4] = ""
    normalizador = criar_normalizador()

    assert normalizador.normalizar(linha) is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.SEM_DATA_DE_ABERTURA] == 1


def test_data_invalida_fica_vazia_quando_a_pessoa_escolhe() -> None:
    linha = [*LINHA_156]
    linha[6] = "ontem"
    decisoes = decisoes_156(datas_invalidas=PoliticaDeDatasInvalidas.DEIXAR_VAZIA)
    normalizador = criar_normalizador(decisoes)

    registro = normalizador.normalizar(linha)

    assert registro is not None
    assert registro.data_ult_movimento is None
    assert normalizador.relatorio.datas_invalidas["data_ult_movimento"] == 1


def test_data_invalida_descarta_a_linha_quando_a_pessoa_escolhe() -> None:
    linha = [*LINHA_156]
    linha[6] = "ontem"
    decisoes = decisoes_156(datas_invalidas=PoliticaDeDatasInvalidas.DESCARTAR_LINHA)
    normalizador = criar_normalizador(decisoes)

    assert normalizador.normalizar(linha) is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.DATA_INVALIDA] == 1


def test_data_com_barra_segue_a_ordem_escolhida() -> None:
    linha = [*LINHA_156]
    linha[4] = "03/04/2026"
    linha[6] = ""
    decisoes = decisoes_156(formato_de_data=FormatoDeData.MES_DIA_ANO)

    registro = criar_normalizador(decisoes).normalizar(linha)

    assert registro is not None
    assert registro.data_abertura == date(2026, 3, 4)


def test_valor_com_cpf_descarta_a_linha_e_nao_guarda_o_valor() -> None:
    linha = [*LINHA_156]
    linha[1] = "Pedido de 123.456.789-09"
    normalizador = criar_normalizador()

    assert normalizador.normalizar(linha) is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.DADO_PESSOAL] == 1
    assert "123.456" not in str(normalizador.relatorio)


def test_linha_curta_e_descartada_como_quebrada() -> None:
    normalizador = criar_normalizador()

    assert normalizador.normalizar(["so uma celula"]) is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.LINHA_QUEBRADA] == 1


def test_o_mesmo_arquivo_gera_as_mesmas_chaves() -> None:
    primeiro = criar_normalizador().normalizar(LINHA_156)
    segundo = criar_normalizador().normalizar(LINHA_156)

    assert primeiro is not None
    assert segundo is not None
    assert primeiro.chave_registro == segundo.chave_registro
    assert primeiro.assinatura == segundo.assinatura


def test_mudanca_de_situacao_mantem_a_chave_e_muda_a_assinatura() -> None:
    linha = [*LINHA_156]
    linha[5] = "EXECUCAO"
    original = criar_normalizador().normalizar(LINHA_156)
    alterado = criar_normalizador().normalizar(linha)

    assert original is not None
    assert alterado is not None
    assert original.chave_registro == alterado.chave_registro
    assert original.assinatura != alterado.assinatura


def test_linhas_iguais_no_arquivo_ganham_chaves_diferentes() -> None:
    (primeira, segunda), normalizador = normalizar_arquivo([LINHA_156, LINHA_156])

    assert primeira is not None
    assert segunda is not None
    assert primeira.chave_registro != segunda.chave_registro
    assert normalizador.relatorio.repetidas_no_arquivo == 1


def test_manter_um_descarta_a_linha_repetida_no_arquivo() -> None:
    decisoes = decisoes_156(repetidos_no_arquivo=PoliticaDeDuplicados.MANTER_UM)

    (primeira, segunda), normalizador = normalizar_arquivo([LINHA_156, LINHA_156], decisoes)

    assert primeira is not None
    assert segunda is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.REPETIDA_NO_ARQUIVO] == 1


def test_mesma_chave_com_conteudo_diferente_nao_e_repetida() -> None:
    decisoes = decisoes_156(repetidos_no_arquivo=PoliticaDeDuplicados.MANTER_UM)
    em_execucao = [*LINHA_156]
    em_execucao[5] = "EXECUCAO"

    (primeira, segunda), normalizador = normalizar_arquivo([LINHA_156, em_execucao], decisoes)

    assert primeira is not None
    assert segunda is not None
    assert primeira.chave_registro != segunda.chave_registro
    assert normalizador.relatorio.repetidas_no_arquivo == 0


def test_o_arquivo_anual_faz_parte_da_identidade_do_registro() -> None:
    partes = {
        "servico_codigo": "77",
        "data_abertura": date(2025, 12, 30),
        "bairro_oficial": "IPSEP",
    }
    fonte = Fonte.CENTRAL_156.value

    no_arquivo_de_2025 = chave_base(fonte, {**partes, "ano_do_arquivo": 2025})
    no_arquivo_de_2026 = chave_base(fonte, {**partes, "ano_do_arquivo": 2026})

    assert no_arquivo_de_2025 != no_arquivo_de_2026


def test_a_ordem_das_linhas_no_arquivo_nao_muda_quem_e_quem() -> None:
    em_execucao = [*LINHA_156]
    em_execucao[5] = "EXECUCAO"

    registros, _ = normalizar_arquivo([LINHA_156, em_execucao])
    invertidos, _ = normalizar_arquivo([em_execucao, LINHA_156])

    pares = {(r.chave_registro, r.assinatura) for r in registros if r}
    pares_invertidos = {(r.chave_registro, r.assinatura) for r in invertidos if r}
    assert pares == pares_invertidos


def test_inserir_como_novos_muda_a_chave_de_quem_ja_existe() -> None:
    decisoes = decisoes_156(repetidos_na_base=PoliticaDeRepetidos.INSERIR_COMO_NOVOS)
    original = criar_normalizador().normalizar(LINHA_156)
    novo = criar_normalizador(decisoes).normalizar(LINHA_156)

    assert original is not None
    assert novo is not None
    assert original.chave_registro != novo.chave_registro


@pytest.mark.parametrize(
    ("nome_do_arquivo", "ano"),
    [("156_2026", 2026), ("ouvidoria_2024", 2024), ("exportacao", 2026)],
)
def test_ano_do_arquivo_vem_do_nome_ou_do_retrato(nome_do_arquivo: str, ano: int) -> None:
    plano = PlanoDeNormalizacao(
        colunas=COLUNAS_156,
        layout=CodigoDoLayout.PORTAL_156,
        decisoes=decisoes_156(),
        arquivo_origem=nome_do_arquivo,
        data_do_retrato=date(2026, 11, 5),
        importacao_id=1,
    )

    registro = NormalizadorDeLinhas(plano, Referencias(BAIRROS, {}), OrdemPorConteudo()).normalizar(
        LINHA_156
    )

    assert registro is not None
    assert registro.ano_do_arquivo == ano
