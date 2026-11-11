from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.fontes import Fonte, Iniciativa
from app.domain.importacao.texto import normalizar_nome_de_coluna

ENDERECO = "logradouro"
NUMERO = "numero"
TEXTO_LIVRE = "texto"
AUXILIAR_REGIONAL = "_regional"
AUXILIAR_MES = "_mes"
AUXILIAR_OCORRENCIA = "_ocorrencia"
AUXILIAR_LOCALIDADE = "_localidade"
AUXILIAR_SOLICITACAO = "_solicitacao"
AUXILIAR_TIPO_DA_ACAO = "_tipo_da_acao"
AUXILIAR_GRAU_DE_RISCO = "_grau_de_risco"
AUXILIAR_DATA_DA_ACAO = "_data_da_acao"
AUXILIAR_RESPOSTA = "_data_resposta"
SEM_USO = "_sem_uso"


class CodigoDoLayout(StrEnum):
    DATASET = "dataset"
    PORTAL_156 = "portal_156"
    PORTAL_OUVIDORIA = "portal_ouvidoria"
    PORTAL_DEFESA_CIVIL = "portal_defesa_civil"
    FORMULARIO = "formulario"
    MANUAL = "manual"


@dataclass(frozen=True)
class Layout:
    codigo: CodigoDoLayout
    nome: str
    assinatura: frozenset[str]
    fonte: Fonte | None = None
    colunas: dict[str, str] = field(default_factory=dict)
    valores_fixos: dict[str, str] = field(default_factory=dict)


PORTAL_156 = Layout(
    CodigoDoLayout.PORTAL_156,
    "156 / Emlurb, Portal de Dados Abertos",
    frozenset({"GRUPOSERVICO_DESCRICAO", "SERVICO_CODIGO", "DATA_DEMANDA", "DATA_ULT_SITUACAO"}),
    Fonte.CENTRAL_156,
    {
        "GRUPOSERVICO_CODIGO": SEM_USO,
        "GRUPOSERVICO_DESCRICAO": "categoria",
        "SERVICO_CODIGO": "servico_codigo",
        "SERVICO_DESCRICAO": "servico",
        "LOGRADOURO": ENDERECO,
        "NUMERO": NUMERO,
        "BAIRRO": "bairro",
        "RPA": "rpa",
        "DATA_DEMANDA": "data_abertura",
        "SITUACAO": "situacao",
        "DATA_ULT_SITUACAO": "data_ult_movimento",
        "LATITUDE": SEM_USO,
        "LONGITUDE": SEM_USO,
    },
    {
        "tipo_registro": "SOLICITACAO DE SERVICO",
        "orgao": "EMLURB",
        "iniciativa": Iniciativa.CIDADAO.value,
    },
)

PORTAL_OUVIDORIA = Layout(
    CodigoDoLayout.PORTAL_OUVIDORIA,
    "Ouvidoria, Portal de Dados Abertos",
    frozenset({"DATA_REGISTRO", "DATA_PRAZO_RESPOSTA", "ORGAO_ENTIDADE", "ASSUNTO"}),
    Fonte.OUVIDORIA,
    {
        "ANO": "ano",
        "NO_PROTOCOLO": "protocolo",
        "DATA_REGISTRO": "data_abertura",
        "DATA_PRAZO_RESPOSTA": "ouv_data_prazo",
        "DATA_RESPOSTA": "data_ult_movimento",
        "CANAL_DE_ATENDIMENTO": "canal_entrada",
        "ORGAO_ENTIDADE": "orgao",
        "NATUREZA_DA_MANIFESTACAO": "tipo_registro",
        "ASSUNTO": "categoria",
        "SITUACAO": "situacao",
    },
    {"iniciativa": Iniciativa.CIDADAO.value},
)

PORTAL_DEFESA_CIVIL = Layout(
    CodigoDoLayout.PORTAL_DEFESA_CIVIL,
    "Defesa Civil, Portal de Dados Abertos",
    frozenset({"GRAU_DE_RISCO", "DATA_DA_ACAO", "TIPO_DA_ACAO", "SOLICITACAO"}),
    Fonte.DEFESA_CIVIL,
    {
        "REGIONAL": AUXILIAR_REGIONAL,
        "ANO": "ano",
        "MES": AUXILIAR_MES,
        "DATA": "data_abertura",
        "OCORRENCIA": AUXILIAR_OCORRENCIA,
        "SOLICITACAO": AUXILIAR_SOLICITACAO,
        "ENDERECO": ENDERECO,
        "BAIRRO": "bairro",
        "LOCALIDADE": AUXILIAR_LOCALIDADE,
        "GRAU_DE_RISCO": AUXILIAR_GRAU_DE_RISCO,
        "DATA_DA_ACAO": AUXILIAR_DATA_DA_ACAO,
        "TIPO_DA_ACAO": AUXILIAR_TIPO_DA_ACAO,
        "QUANTIDADE": SEM_USO,
        "ALTURA": SEM_USO,
        "LARGURA": SEM_USO,
        "AREA_M": SEM_USO,
    },
    {"orgao": "SEDEC", "servico_codigo": "448"},
)

DATASET = Layout(
    CodigoDoLayout.DATASET,
    "Dataset do RecifeView",
    frozenset({"FONTE", "DATA_ABERTURA", "CATEGORIA", "BAIRRO_OFICIAL"}),
)

PACOTE_DO_FORMULARIO = Layout(
    CodigoDoLayout.FORMULARIO,
    "Pacote do formulário público",
    frozenset({"CONTRIBUICAO_ID", "RELATOS_SOMADOS"}),
    Fonte.FORMULARIO,
    {
        "CONTRIBUICAO_ID": "id_registro",
        "DATA_ABERTURA": "data_abertura",
        "CATEGORIA": "categoria",
        "SERVICO_CODIGO": "servico_codigo",
        "SERVICO": "servico",
        "BAIRRO_OFICIAL": "bairro_oficial",
        "ID_LOCAL": "id_local",
        "NUMERO_INFORMADO": "numero_informado",
        "RELATOS_SOMADOS": SEM_USO,
    },
    {
        "tipo_registro": "CONTRIBUICAO",
        "canal_entrada": "FORMULARIO PUBLICO",
        "situacao": "RECEBIDA",
        "iniciativa": Iniciativa.CIDADAO.value,
    },
)

MANUAL = Layout(CodigoDoLayout.MANUAL, "Mapeamento manual", frozenset())

LAYOUTS_RECONHECIDOS = (
    DATASET,
    PACOTE_DO_FORMULARIO,
    PORTAL_156,
    PORTAL_OUVIDORIA,
    PORTAL_DEFESA_CIVIL,
)
LAYOUTS_POR_CODIGO = {layout.codigo: layout for layout in (*LAYOUTS_RECONHECIDOS, MANUAL)}


def reconhecer_layout(colunas: list[str]) -> Layout:
    presentes = {normalizar_nome_de_coluna(coluna) for coluna in colunas}
    for layout in LAYOUTS_RECONHECIDOS:
        if layout.assinatura <= presentes:
            return layout
    return MANUAL
