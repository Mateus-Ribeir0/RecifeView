from collections import Counter
from datetime import date

import pytest

from app.domain.importacao.datas import (
    FormatoDeData,
    formato_de_data_ambiguo,
    interpretar_data,
    usa_barra_com_ano_no_fim,
)
from app.domain.importacao.decisoes import Decisoes, PoliticaDeRepetidos
from app.domain.importacao.layouts import (
    DATASET,
    ENDERECO,
    NUMERO,
    PORTAL_156,
    TEXTO_LIVRE,
    CodigoDoLayout,
    Layout,
)
from app.domain.importacao.mapeamento import (
    OrigemDaSugestao,
    campos_obrigatorios_faltando,
    sugerir_mapeamento,
)
from app.domain.importacao.pendencias import (
    TipoDePendencia,
    montar_pendencia_de_valores,
    valores_ainda_sem_resposta,
)
from app.domain.importacao.privacidade import (
    MotivoDeBloqueio,
    localizar_colunas_bloqueadas,
    motivo_pelo_conteudo,
    motivo_pelo_nome,
)
from app.domain.importacao.pseudonimizacao import gerar_id_local, numero_foi_informado
from app.domain.importacao.texto import normalizar_nome_de_coluna, normalizar_texto

MANUAL = Layout(CodigoDoLayout.MANUAL, "manual", frozenset())


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("Várzea", "VARZEA"),
        ("  Boa   Viagem ", "BOA VIAGEM"),
        ("ILUMINAÃ‡ÃƒO", "ILUMINACAO"),
    ],
)
def test_texto_fica_sem_acento_e_em_maiusculas(valor: str, esperado: str) -> None:
    assert normalizar_texto(valor) == esperado


def test_nome_de_coluna_ignora_acento_pontuacao_e_espaco() -> None:
    assert normalizar_nome_de_coluna("Órgão/Entidade ") == "ORGAO_ENTIDADE"


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("2026-03-04", date(2026, 3, 4)),
        ("2026-03-04 10:30:00", date(2026, 3, 4)),
        ("2026/03/04", date(2026, 3, 4)),
        ("04/03/2026", date(2026, 3, 4)),
        ("31/02/2026", None),
        ("sem data", None),
    ],
)
def test_data_e_interpretada_nos_formatos_das_fontes(valor: str, esperado: date | None) -> None:
    assert interpretar_data(valor, FormatoDeData.DIA_MES_ANO) == esperado


def test_dia_acima_de_doze_prova_a_ordem_das_datas() -> None:
    assert formato_de_data_ambiguo(["01/02/2026", "25/02/2026"]) is FormatoDeData.DIA_MES_ANO
    assert formato_de_data_ambiguo(["02/25/2026"]) is FormatoDeData.MES_DIA_ANO


def test_valores_ate_doze_nao_provam_a_ordem_das_datas() -> None:
    assert formato_de_data_ambiguo(["01/02/2026", "03/04/2026"]) is None


def test_data_iso_nao_usa_barra() -> None:
    assert usa_barra_com_ano_no_fim(["2026-03-04"]) is False
    assert usa_barra_com_ano_no_fim(["04/03/2026"]) is True


@pytest.mark.parametrize(
    ("coluna", "motivo"),
    [
        ("CPF do Solicitante", MotivoDeBloqueio.DOCUMENTO),
        ("Nome", MotivoDeBloqueio.NOME_DE_PESSOA),
        ("E-mail", MotivoDeBloqueio.CONTATO),
        ("Telefone", MotivoDeBloqueio.CONTATO),
        ("LOGRADOURO", MotivoDeBloqueio.ENDERECO),
        ("Descrição", MotivoDeBloqueio.TEXTO_LIVRE),
        ("descricao_mascarada", MotivoDeBloqueio.TEXTO_LIVRE),
        ("latitude", MotivoDeBloqueio.COORDENADA),
    ],
)
def test_coluna_sensivel_e_reconhecida_pelo_nome(coluna: str, motivo: MotivoDeBloqueio) -> None:
    assert motivo_pelo_nome(coluna) is motivo


@pytest.mark.parametrize(
    "coluna", ["SERVICO_DESCRICAO", "NOME_BAIRRO", "numero_informado", "Bairro", "Assunto"]
)
def test_coluna_comum_nao_e_bloqueada(coluna: str) -> None:
    assert motivo_pelo_nome(coluna) is None


@pytest.mark.parametrize("valor", ["123.456.789-09", "fulano@exemplo.com.br", "(81) 99999-0000"])
def test_conteudo_pessoal_e_reconhecido(valor: str) -> None:
    assert motivo_pelo_conteudo(valor) is not None


def test_coluna_de_nome_inocente_com_cpf_no_conteudo_e_bloqueada() -> None:
    amostra = [["123.456.789-09", "ok"], ["987.654.321-00", "ok"]]

    bloqueadas = localizar_colunas_bloqueadas(["campo_a", "campo_b"], amostra)

    assert [bloqueada.coluna for bloqueada in bloqueadas] == ["campo_a"]
    assert bloqueadas[0].motivo is MotivoDeBloqueio.DOCUMENTO


def test_um_unico_valor_suspeito_nao_bloqueia_a_coluna() -> None:
    amostra = [["fulano@exemplo.com.br"], ["sem contato"], ["outro valor"]]

    assert localizar_colunas_bloqueadas(["campo_a"], amostra) == []


def test_sugestao_vem_do_layout_do_portal() -> None:
    sugestoes = sugerir_mapeamento(["GRUPOSERVICO_DESCRICAO", "BAIRRO"], PORTAL_156, [])

    assert sugestoes[0].campo == "categoria"
    assert sugestoes[0].origem is OrigemDaSugestao.LAYOUT
    assert sugestoes[1].campo == "bairro"


def test_sugestao_usa_sinonimo_e_nome_parecido() -> None:
    sugestoes = sugerir_mapeamento(["Data Registro", "Data Abertura ", "Situaçao"], MANUAL, [])

    assert sugestoes[0].campo == "data_abertura"
    assert sugestoes[0].origem is OrigemDaSugestao.SINONIMO
    assert sugestoes[1].campo is None
    assert sugestoes[2].campo == "situacao"


def test_coluna_sem_correspondencia_fica_sem_sugestao() -> None:
    sugestao = sugerir_mapeamento(["xpto"], MANUAL, [])[0]

    assert sugestao.campo is None
    assert sugestao.origem is OrigemDaSugestao.SEM_CORRESPONDENCIA


def test_endereco_bloqueado_so_serve_para_o_pseudonimo() -> None:
    colunas = ["LOGRADOURO", "NUMERO", "CPF"]
    bloqueadas = localizar_colunas_bloqueadas(colunas, [])

    sugestoes = sugerir_mapeamento(colunas, PORTAL_156, bloqueadas)

    assert [sugestao.campo for sugestao in sugestoes] == [ENDERECO, NUMERO, None]
    assert all(sugestao.origem is OrigemDaSugestao.BLOQUEADA for sugestao in sugestoes)


def test_ementa_so_e_lida_no_dataset_do_grupo() -> None:
    bloqueadas = localizar_colunas_bloqueadas(["texto"], [])

    assert sugerir_mapeamento(["texto"], DATASET, bloqueadas)[0].campo == TEXTO_LIVRE
    assert sugerir_mapeamento(["texto"], MANUAL, bloqueadas)[0].campo is None


def test_campo_obrigatorio_faltando_e_apontado() -> None:
    assert campos_obrigatorios_faltando({"data_abertura"}) == ["categoria"]


def test_valor_respondido_sai_das_pendencias() -> None:
    decisoes = Decisoes(substituicoes={"bairro": {"A": "AFOGADOS"}})

    restantes = valores_ainda_sem_resposta("bairro", Counter({"A": 2, "B": 1}), decisoes)

    assert restantes == Counter({"B": 1})


def test_regra_para_os_demais_valores_resolve_a_pendencia() -> None:
    decisoes = Decisoes(padrao_para_valores={"bairro": "__deixar_vazio__"})

    assert not valores_ainda_sem_resposta("bairro", Counter({"A": 2}), decisoes)


def test_pendencia_sugere_o_valor_mais_parecido() -> None:
    pendencia = montar_pendencia_de_valores(
        TipoDePendencia.BAIRRO_DESCONHECIDO,
        "bairro",
        Counter({"AFOGADOSS": 3}),
        ["AFOGADOS", "VARZEA"],
    )

    assert pendencia.quantidade == 3
    assert pendencia.valores[0].sugestao == "AFOGADOS"


def test_decisoes_voltam_iguais_depois_de_guardadas() -> None:
    decisoes = Decisoes(
        data_do_retrato=date(2026, 11, 5),
        mapeamento={"A": "categoria"},
        repetidos_na_base=PoliticaDeRepetidos.ATUALIZAR,
    )

    assert Decisoes.de_dicionario(decisoes.para_dicionario()) == decisoes


def test_id_local_e_estavel_e_ignora_acento_e_caixa() -> None:
    primeiro = gerar_id_local(("Rua da Aurora", "10"), "sal")
    segundo = gerar_id_local(("RUA DA AURORA ", "10"), "sal")

    assert primeiro == segundo
    assert gerar_id_local(("Rua da Aurora", "10"), "outro sal") != primeiro


def test_endereco_vazio_nao_gera_id_local() -> None:
    assert gerar_id_local(("", ""), "sal") is None


@pytest.mark.parametrize(("numero", "esperado"), [("10", True), ("S/N", False), ("0", False)])
def test_numero_informado_segue_a_regra_do_pipeline(numero: str, esperado: bool) -> None:
    assert numero_foi_informado(numero) is esperado
