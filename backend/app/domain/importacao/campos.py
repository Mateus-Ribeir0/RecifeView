from dataclasses import dataclass
from enum import StrEnum


class TipoDeCampo(StrEnum):
    TEXTO = "texto"
    DATA = "data"
    INTEIRO = "inteiro"
    BOOLEANO = "booleano"


@dataclass(frozen=True)
class Campo:
    nome: str
    rotulo: str
    tipo: TipoDeCampo
    descricao: str
    sinonimos: tuple[str, ...] = ()


CAMPOS: tuple[Campo, ...] = (
    Campo("fonte", "Fonte", TipoDeCampo.TEXTO, "Porta de entrada da demanda."),
    Campo(
        "data_abertura",
        "Data de abertura",
        TipoDeCampo.DATA,
        "Dia em que a demanda foi registrada.",
        ("DATA", "DATA_DEMANDA", "DATA_REGISTRO", "DATA_DE_ABERTURA", "ABERTURA", "DATA_ENTRADA"),
    ),
    Campo(
        "data_ult_movimento",
        "Data do último movimento",
        TipoDeCampo.DATA,
        "Última movimentação, conclusão ou resposta.",
        ("DATA_ULT_SITUACAO", "DATA_RESPOSTA", "DATA_CONCLUSAO", "DATA_DA_ACAO", "DATA_FIM"),
    ),
    Campo(
        "dias_ate_movimento",
        "Dias até o movimento",
        TipoDeCampo.INTEIRO,
        "Dias entre a abertura e o último movimento. Sem esta coluna, é calculado.",
    ),
    Campo("ano", "Ano", TipoDeCampo.INTEIRO, "Ano do registro na fonte.", ("ANO_REGISTRO",)),
    Campo(
        "categoria",
        "Categoria",
        TipoDeCampo.TEXTO,
        "Grupo de serviço ou assunto.",
        ("GRUPOSERVICO_DESCRICAO", "GRUPO", "GRUPO_DE_SERVICO", "GRUPO_SERVICO", "ASSUNTO", "TEMA"),
    ),
    Campo(
        "servico_codigo",
        "Código do serviço",
        TipoDeCampo.TEXTO,
        "Código do serviço no 156.",
        ("SERVICO_CODIGO", "COD_SERVICO", "CODIGO_SERVICO"),
    ),
    Campo(
        "servico",
        "Serviço",
        TipoDeCampo.TEXTO,
        "Nome do serviço pedido.",
        ("SERVICO_DESCRICAO", "SERVICO_NOME", "DESCRICAO_SERVICO", "NOME_DO_SERVICO"),
    ),
    Campo(
        "tipo_registro",
        "Tipo de registro",
        TipoDeCampo.TEXTO,
        "Natureza do registro (solicitação, ação, indicação...).",
        ("NATUREZA", "NATUREZA_DA_MANIFESTACAO", "TIPO", "TIPO_DE_REGISTRO"),
    ),
    Campo(
        "orgao",
        "Órgão",
        TipoDeCampo.TEXTO,
        "Órgão responsável ou destinatário.",
        ("ORGAO_ENTIDADE", "ORGAO_RESPONSAVEL", "ORGAO_DESTINATARIO", "SECRETARIA", "ENTIDADE"),
    ),
    Campo(
        "canal_entrada",
        "Canal de entrada",
        TipoDeCampo.TEXTO,
        "Por onde a demanda entrou.",
        ("CANAL", "CANAL_DE_ATENDIMENTO", "CANAL_DE_ENTRADA"),
    ),
    Campo(
        "bairro",
        "Bairro informado",
        TipoDeCampo.TEXTO,
        "Bairro como veio no arquivo. Vira um dos 94 bairros oficiais.",
        ("NOME_BAIRRO", "BAIRRO_CITADO", "BAIRRO_NOME"),
    ),
    Campo(
        "bairro_oficial",
        "Bairro oficial",
        TipoDeCampo.TEXTO,
        "Bairro já na forma dos 94 bairros oficiais.",
    ),
    Campo("rpa", "RPA", TipoDeCampo.TEXTO, "Região Político-Administrativa, de 1 a 6."),
    Campo(
        "situacao",
        "Situação",
        TipoDeCampo.TEXTO,
        "Etapa do pedido na fonte.",
        ("STATUS", "SITUACAO_ATUAL", "ETAPA", "PROCESSO_STATUS"),
    ),
    Campo("iniciativa", "Iniciativa", TipoDeCampo.TEXTO, "Quem provocou o registro."),
    Campo(
        "id_local",
        "Pseudônimo do endereço",
        TipoDeCampo.TEXTO,
        "Hash do endereço. Nunca é exibido.",
    ),
    Campo(
        "numero_informado",
        "Tem número no endereço",
        TipoDeCampo.BOOLEANO,
        "Falso quando o endereço veio sem número.",
    ),
    Campo(
        "id_registro",
        "Identificador da fonte",
        TipoDeCampo.TEXTO,
        "Usado só para reconhecer o registro. Não fica guardado.",
        ("REQUERIMENTO", "PROCESSO_NUMERO", "NUMERO_DO_PROCESSO", "NO_PROTOCOLO"),
    ),
    Campo(
        "ouv_data_prazo",
        "Prazo da Ouvidoria",
        TipoDeCampo.DATA,
        "Data-limite de resposta.",
        ("DATA_PRAZO_RESPOSTA", "DATA_PRAZO", "PRAZO_RESPOSTA"),
    ),
    Campo("ouv_no_prazo", "Respondida no prazo", TipoDeCampo.BOOLEANO, "Resposta até o prazo."),
    Campo(
        "camara_data_envio_prefeitura",
        "Envio à Prefeitura",
        TipoDeCampo.DATA,
        "Data em que a Câmara enviou a indicação.",
        ("DATA_ENVIO_PREFEITURA", "DATA_ENVIO"),
    ),
    Campo(
        "camara_canal_envio",
        "Canal de envio",
        TipoDeCampo.TEXTO,
        "Como a indicação foi enviada.",
        ("CANAL_ENVIO",),
    ),
    Campo(
        "camara_dias_ate_envio",
        "Dias até o envio",
        TipoDeCampo.INTEIRO,
        "Dias entre a apresentação e o envio.",
        ("DIAS_ATE_ENVIO_PREFEITURA",),
    ),
    Campo(
        "camara_data_resposta",
        "Resposta registrada",
        TipoDeCampo.DATA,
        "Data da resposta registrada na tramitação.",
        ("DATA_RESPOSTA_REGISTRADA",),
    ),
    Campo(
        "camara_dias_ate_resposta",
        "Dias até a resposta",
        TipoDeCampo.INTEIRO,
        "Dias entre a apresentação e a resposta.",
        ("DIAS_ATE_RESPOSTA_REGISTRADA",),
    ),
    Campo(
        "camara_desfecho",
        "Desfecho na Câmara",
        TipoDeCampo.TEXTO,
        "Situação final da indicação.",
        ("DESFECHO_NA_CAMARA",),
    ),
    Campo(
        "arquivo_origem", "Arquivo de origem", TipoDeCampo.TEXTO, "Arquivo publicado pela fonte."
    ),
)

CAMPOS_POR_NOME = {campo.nome: campo for campo in CAMPOS}

CAMPOS_OBRIGATORIOS = ("data_abertura", "categoria")
CAMPOS_DE_DATA = tuple(campo.nome for campo in CAMPOS if campo.tipo is TipoDeCampo.DATA)
CAMPOS_VERIFICADOS_NO_VOCABULARIO = ("categoria", "situacao", "orgao")
