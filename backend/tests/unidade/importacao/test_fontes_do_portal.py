from datetime import date

from app.domain.fontes import Fonte
from app.domain.importacao.chaves import OrdemPorConteudo
from app.domain.importacao.decisoes import Decisoes
from app.domain.importacao.layouts import (
    AUXILIAR_DATA_DA_ACAO,
    AUXILIAR_GRAU_DE_RISCO,
    AUXILIAR_MES,
    AUXILIAR_OCORRENCIA,
    AUXILIAR_REGIONAL,
    AUXILIAR_SOLICITACAO,
    AUXILIAR_TIPO_DA_ACAO,
    ENDERECO,
    PORTAL_156,
    PORTAL_DEFESA_CIVIL,
    PORTAL_OUVIDORIA,
    CodigoDoLayout,
    reconhecer_layout,
)
from app.domain.importacao.normalizador import (
    NormalizadorDeLinhas,
    PlanoDeNormalizacao,
    Referencias,
)
from app.domain.importacao.relatorio import Correcao, MotivoDeDescarte

COLUNAS_OUVIDORIA = (
    "Ano",
    "Data Registro",
    "Data Prazo Resposta",
    "Data Resposta",
    "Órgão/Entidade",
    "Natureza",
    "Assunto",
    "Situação",
)
MAPEAMENTO_OUVIDORIA = {
    "Ano": "ano",
    "Data Registro": "data_abertura",
    "Data Prazo Resposta": "ouv_data_prazo",
    "Data Resposta": "data_ult_movimento",
    "Órgão/Entidade": "orgao",
    "Natureza": "tipo_registro",
    "Assunto": "categoria",
    "Situação": "situacao",
}
COLUNAS_DEFESA_CIVIL = (
    "Regional",
    "Ano",
    "Mes",
    "Data",
    "Ocorrencia",
    "Solicitacao",
    "Endereco",
    "Bairro",
    "Grau",
    "Acao",
    "Tipo",
)
MAPEAMENTO_DEFESA_CIVIL = {
    "Regional": AUXILIAR_REGIONAL,
    "Ano": "ano",
    "Mes": AUXILIAR_MES,
    "Data": "data_abertura",
    "Ocorrencia": AUXILIAR_OCORRENCIA,
    "Solicitacao": AUXILIAR_SOLICITACAO,
    "Endereco": ENDERECO,
    "Bairro": "bairro",
    "Grau": AUXILIAR_GRAU_DE_RISCO,
    "Acao": AUXILIAR_DATA_DA_ACAO,
    "Tipo": AUXILIAR_TIPO_DA_ACAO,
}


def normalizador_de(
    layout: CodigoDoLayout,
    colunas: tuple[str, ...],
    decisoes: Decisoes,
) -> NormalizadorDeLinhas:
    plano = PlanoDeNormalizacao(colunas, layout, decisoes, "arquivo_2024", date(2026, 11, 5), 1)
    return NormalizadorDeLinhas(plano, Referencias({"AFOGADOS": "5"}, {}), OrdemPorConteudo())


def ouvidoria() -> NormalizadorDeLinhas:
    decisoes = Decisoes(
        fonte=Fonte.OUVIDORIA,
        mapeamento=MAPEAMENTO_OUVIDORIA,
        valores_fixos={"iniciativa": "CIDADAO"},
    )
    return normalizador_de(CodigoDoLayout.PORTAL_OUVIDORIA, COLUNAS_OUVIDORIA, decisoes)


def defesa_civil() -> NormalizadorDeLinhas:
    decisoes = Decisoes(
        fonte=Fonte.DEFESA_CIVIL,
        mapeamento=MAPEAMENTO_DEFESA_CIVIL,
        valores_fixos={"orgao": "SEDEC", "servico_codigo": "448"},
    )
    return normalizador_de(CodigoDoLayout.PORTAL_DEFESA_CIVIL, COLUNAS_DEFESA_CIVIL, decisoes)


def test_cabecalhos_do_portal_sao_reconhecidos() -> None:
    do_156 = ["GRUPOSERVICO_DESCRICAO", "SERVICO_CODIGO", "DATA_DEMANDA", "DATA_ULT_SITUACAO"]
    da_ouvidoria = ["Data Registro", "Data Prazo Resposta", "Órgão/Entidade", "Assunto"]
    da_defesa_civil = ["Grau_de_Risco", "Data_da_Acao", "Tipo_da_Acao", "Solicitacao"]

    assert reconhecer_layout(do_156) is PORTAL_156
    assert reconhecer_layout(da_ouvidoria) is PORTAL_OUVIDORIA
    assert reconhecer_layout(da_defesa_civil) is PORTAL_DEFESA_CIVIL


def test_cabecalho_desconhecido_pede_mapeamento_manual() -> None:
    assert reconhecer_layout(["coluna a", "coluna b"]).codigo is CodigoDoLayout.MANUAL


def test_ouvidoria_calcula_se_respondeu_no_prazo() -> None:
    linha = [
        "2024",
        "02/01/2024",
        "16/01/2024",
        "10/01/2024",
        "Secretaria de Saúde",
        "Reclamação",
        "Atendimento",
        "Concluído",
    ]

    registro = ouvidoria().normalizar(linha)

    assert registro is not None
    assert registro.ouv_no_prazo is True
    assert registro.servico == "ATENDIMENTO"
    assert registro.situacao == "CONCLUIDO"


def ouvidoria_com_protocolo() -> NormalizadorDeLinhas:
    decisoes = Decisoes(
        fonte=Fonte.OUVIDORIA,
        mapeamento={"Protocolo": "protocolo", **MAPEAMENTO_OUVIDORIA},
        valores_fixos={"iniciativa": "CIDADAO"},
    )
    colunas = ("Protocolo", *COLUNAS_OUVIDORIA)
    return normalizador_de(CodigoDoLayout.PORTAL_OUVIDORIA, colunas, decisoes)


LINHA_DA_OUVIDORIA = [
    "2024",
    "02/01/2024",
    "16/01/2024",
    "10/01/2024",
    "Secretaria de Saúde",
    "Reclamação",
    "Atendimento",
    "Concluído",
]


def test_ouvidoria_guarda_o_protocolo_sem_espacos_e_em_maiusculas() -> None:
    registro = ouvidoria_com_protocolo().normalizar([" 2024/ab 0001 ", *LINHA_DA_OUVIDORIA])

    assert registro is not None
    assert registro.protocolo == "2024/AB0001"


def test_registro_sem_protocolo_mantem_a_assinatura_de_antes() -> None:
    sem_coluna = ouvidoria().normalizar(LINHA_DA_OUVIDORIA)
    com_coluna_vazia = ouvidoria_com_protocolo().normalizar(["", *LINHA_DA_OUVIDORIA])
    com_protocolo = ouvidoria_com_protocolo().normalizar(["2024/1", *LINHA_DA_OUVIDORIA])

    assert sem_coluna is not None
    assert com_coluna_vazia is not None
    assert com_protocolo is not None
    assert com_coluna_vazia.protocolo is None
    assert com_coluna_vazia.assinatura == sem_coluna.assinatura
    assert com_protocolo.assinatura != sem_coluna.assinatura
    assert com_protocolo.chave_registro == sem_coluna.chave_registro


def test_ouvidoria_harmoniza_o_nome_do_orgao() -> None:
    linha = [
        "2022",
        "2022-03-01",
        "2022-03-15",
        "",
        "Autarquia de Trânsito e Transporte Urbano do Recife-CTTU",
        "Denúncia",
        "Trânsito",
        "ABERTO",
    ]
    normalizador = ouvidoria()

    registro = normalizador.normalizar(linha)

    assert registro is not None
    assert registro.orgao == "CTTU"
    assert registro.ouv_no_prazo is False
    assert normalizador.relatorio.correcoes[Correcao.ORGAO_HARMONIZADO] == 1


def test_ouvidoria_descarta_linha_com_texto_vazando_na_situacao() -> None:
    linha = ["2025", "2025-07-01", "", "", "ORGAO", "NATUREZA", "ASSUNTO", "RESPONDIDO EM 12/07"]
    normalizador = ouvidoria()

    assert normalizador.normalizar(linha) is None
    assert normalizador.relatorio.descartes[MotivoDeDescarte.LINHA_QUEBRADA] == 1


def test_defesa_civil_classifica_a_demanda_do_cidadao() -> None:
    linha = [
        "RPA 5",
        "2024",
        "MARCO",
        "2024-03-05",
        "DESLIZAMENTO",
        "VISTORIA NO IMOVEL",
        "RUA DA ENCOSTA, 10",
        "AFOGADOS",
        "R3",
        "2024-03-06",
        "ANALISE VISUAL",
    ]

    registro = defesa_civil().normalizar(linha)

    assert registro is not None
    assert registro.categoria == "VISTORIA (demanda)"
    assert registro.iniciativa == "CIDADAO"
    assert registro.situacao == "R3"
    assert registro.tipo_registro == "ACAO: ANALISE VISUAL"
    assert registro.dias_ate_movimento == 1


def test_defesa_civil_reconhece_monitoramento_proativo() -> None:
    linha = [
        "RPA 5",
        "2024",
        "MARCO",
        "2024-03-05",
        "",
        "MONITORAMENTO DE AREA",
        "",
        "AFOGADOS",
        "",
        "2024-03-05",
        "ROCAGEM",
    ]

    registro = defesa_civil().normalizar(linha)

    assert registro is not None
    assert registro.iniciativa == "PROATIVA"


def test_defesa_civil_corrige_as_colunas_deslocadas_do_arquivo() -> None:
    deslocada = [
        "2019",
        "MARCO",
        "2019-03-05",
        "DESLIZAMENTO",
        "PEDIDO DE LONA",
        "RUA DA ENCOSTA",
        "10",
        "AFOGADOS",
        "R2",
        "2019-03-07",
        "COLOCACAO",
    ]

    registro = defesa_civil().normalizar(deslocada)

    assert registro is not None
    assert registro.ano == 2019
    assert registro.data_abertura == date(2019, 3, 5)
    assert registro.categoria == "LONA (demanda)"
