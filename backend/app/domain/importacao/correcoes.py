import re
from collections.abc import Iterable

from app.domain.importacao.bairros import APELIDOS_DE_BAIRRO
from app.domain.importacao.texto import normalizar_texto

# Nomes populares que a N3 aceitou na ementa: mais apelidos mudariam a contagem conferida.
APELIDOS_NA_EMENTA = (
    "SITIO DOS PINTOS",
    "SAO BRAS",
    "COHAB IBURA DE CIMA",
    "IBURA DE BAIXO",
    "BAIRRO DO RECIFE",
    "RECIFE ANTIGO",
    "POCO DA PANELA",
    "ZUMBI DO PACHECO",
)

# As correções reproduzem o que a N3 fez no notebook (docs/dados.md, "Correções da N3").
CATEGORIAS_DO_156 = {"TERRAPLANAGEN": "TERRAPLENAGEM", "TERRAPLANAGEM": "TERRAPLENAGEM"}

ORGAOS_DA_OUVIDORIA = {
    "AUTARQUIA DE MANUTENCAO E LIMPEZA URBANA DO RECIFE-EMLURB": "EMLURB",
    "AUTARQUIA DE TRANSITO E TRANSPORTE URBANO DO RECIFE-CTTU": "CTTU",
    "AUTARQUIA DE URBANIZACAO DO RECIFE-URB": "URB",
    "EMPRESA MUNICIPAL DE INFORMATICA-EMPREL": "EMPREL",
    "MERCADOS E FEIRAS - AUTARQUIA MUNICIPAL-CONVIVA": "CONVIVA",
    "SAUDE RECIFE-RECIPREV": "RECIPREV",
    "CONSELHO MUNICIPAL DE DEFESA E PROMOCAO DOS DIREITOS DA CRIANCA E DO ADOLESCENTE-COMDICA": (
        "COMDICA"
    ),
    "SECRETARIA-EXECUTIVA DE DEFESA CIVIL": "SECRETARIA EXECUTIVA DE DEFESA CIVIL",
    "CONTROLADORIA-GERAL DO MUNICIPIO": "CONTROLADORIA GERAL DO MUNICIPIO",
    "PROCURADORIA-GERAL DO MUNICIPIO": "PROCURADORIA GERAL DO MUNICIPIO",
    "SECRETARIA PLANEJAMENTO, GESTAO E TRANSFORMACAO DIGITAL": (
        "SECRETARIA DE PLANEJAMENTO, GESTAO E TRANSFORMACAO DIGITAL"
    ),
}

SITUACOES_EQUIVALENTES_DO_156 = {"PENDENTE": "PENDENCIA"}
RPAS_VALIDAS = frozenset({"1", "2", "3", "4", "5", "6"})
TAMANHO_MAXIMO_DA_SITUACAO_DA_OUVIDORIA = 30


def padrao_de_bairro_na_ementa(bairros_oficiais: Iterable[str]) -> re.Pattern[str]:
    # Só vale depois de "bairro", "comunidade" ou "localidade": na N3, o nome solto era nome de rua
    # em cerca de 1 a cada 4 casos ("Rua Zumbi dos Palmares").
    chaves = sorted(set(bairros_oficiais) | set(APELIDOS_NA_EMENTA), key=len, reverse=True)
    alternativas = "|".join(map(re.escape, chaves))
    return re.compile(
        rf"\b(?:BAIRRO|COMUNIDADE|LOCALIDADE)\s+(?:D[OAE]S?\s+|EM\s+)?({alternativas})\b"
    )


def bairro_na_ementa(ementa: str, padrao: re.Pattern[str]) -> str | None:
    achado = padrao.search(normalizar_texto(ementa))
    if achado is None:
        return None
    return APELIDOS_DE_BAIRRO.get(achado.group(1), achado.group(1))


def situacao_da_ouvidoria_esta_quebrada(situacao: str) -> bool:
    """Em 2025 a Ouvidoria publicou linhas com texto ou data vazando para a coluna Situação."""
    tamanho_valido = 1 <= len(situacao) <= TAMANHO_MAXIMO_DA_SITUACAO_DA_OUVIDORIA
    return not tamanho_valido or any(caractere.isdigit() for caractere in situacao)
