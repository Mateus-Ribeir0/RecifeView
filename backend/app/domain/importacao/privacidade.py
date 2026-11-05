import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache

from app.domain.importacao.texto import normalizar_nome_de_coluna

AMOSTRAS_SUFICIENTES = 2


class MotivoDeBloqueio(StrEnum):
    NOME_DE_PESSOA = "nome_de_pessoa"
    DOCUMENTO = "documento"
    CONTATO = "contato"
    ENDERECO = "endereco"
    TEXTO_LIVRE = "texto_livre"
    COORDENADA = "coordenada"


ROTULOS_DOS_MOTIVOS = {
    MotivoDeBloqueio.NOME_DE_PESSOA: "Nome de pessoa",
    MotivoDeBloqueio.DOCUMENTO: "Documento pessoal",
    MotivoDeBloqueio.CONTATO: "Contato pessoal",
    MotivoDeBloqueio.ENDERECO: "Endereço",
    MotivoDeBloqueio.TEXTO_LIVRE: "Texto livre",
    MotivoDeBloqueio.COORDENADA: "Coordenada",
}

PADROES_DE_NOME_DE_COLUNA: tuple[tuple[re.Pattern[str], MotivoDeBloqueio], ...] = (
    (re.compile(r"(^|_)(CPF|CNPJ|RG|CNH|NIS|PIS|TITULO_ELEITOR)(_|$)"), MotivoDeBloqueio.DOCUMENTO),
    (
        re.compile(
            r"(^|_)(NOME|NOME_COMPLETO|SOLICITANTE|REQUERENTE|CIDADAO|DENUNCIANTE|MANIFESTANTE"
            r"|RECLAMANTE|MORADOR|AUTORIA|AUTOR|AVALIADOR|ATENDENTE)(_|$)"
        ),
        MotivoDeBloqueio.NOME_DE_PESSOA,
    ),
    (
        re.compile(r"(^|_)(EMAIL|E_MAIL|TELEFONE|FONE|CELULAR|WHATSAPP|CONTATO)(_|$)"),
        MotivoDeBloqueio.CONTATO,
    ),
    (
        re.compile(
            r"(^|_)(ENDERECO|LOGRADOURO|NUMERO|COMPLEMENTO|CEP|ROTEIRO|SOLICITACAO_ENDERECO)(_|$)"
        ),
        MotivoDeBloqueio.ENDERECO,
    ),
    (
        re.compile(
            r"(^|_)(TEXTO|DESCRICAO|DESCRICAO_MASCARADA|RELATO|OBSERVACAO|OBSERVACOES|EMENTA"
            r"|HISTORICO|DETALHE|DETALHES|COMENTARIO|COMENTARIOS|MENSAGEM)(_|$)"
        ),
        MotivoDeBloqueio.TEXTO_LIVRE,
    ),
    (re.compile(r"(^|_)(LAT|LON|LNG|LATITUDE|LONGITUDE)(_|$)"), MotivoDeBloqueio.COORDENADA),
)

# Nomes de coluna que contêm uma palavra da lista acima, mas não são dado pessoal.
COLUNAS_PERMITIDAS = frozenset(
    {
        "SERVICO_DESCRICAO",
        "GRUPOSERVICO_DESCRICAO",
        "DESCRICAO_SERVICO",
        "NOME_DO_SERVICO",
        "SERVICO_NOME",
        "SERVICO_NOME_CANONICO",
        "NOME_BAIRRO",
        "BAIRRO_NOME",
        "NUMERO_INFORMADO",
        "NUMERO_DO_PROCESSO",
        "PROCESSO_NUMERO",
        "NO_PROTOCOLO",
        "ROTULOS_OCORRENCIA",
    }
)

PADRAO_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
PADRAO_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PADRAO_TELEFONE = re.compile(r"\(\d{2}\)\s?9?\d{4}-?\d{4}\b")

CACHE_DE_VERIFICACOES = 300_000


@dataclass(frozen=True)
class ColunaBloqueada:
    coluna: str
    motivo: MotivoDeBloqueio


def motivo_pelo_nome(coluna: str) -> MotivoDeBloqueio | None:
    nome = normalizar_nome_de_coluna(coluna)
    if nome in COLUNAS_PERMITIDAS:
        return None
    for padrao, motivo in PADROES_DE_NOME_DE_COLUNA:
        if padrao.search(nome):
            return motivo
    return None


@lru_cache(maxsize=CACHE_DE_VERIFICACOES)
def motivo_pelo_conteudo(valor: str) -> MotivoDeBloqueio | None:
    if PADRAO_CPF.search(valor):
        return MotivoDeBloqueio.DOCUMENTO
    if PADRAO_EMAIL.search(valor) or PADRAO_TELEFONE.search(valor):
        return MotivoDeBloqueio.CONTATO
    return None


def _motivo_pela_amostra(valores: Iterable[str]) -> MotivoDeBloqueio | None:
    achados = [motivo for valor in valores if (motivo := motivo_pelo_conteudo(valor)) is not None]
    return achados[0] if len(achados) >= AMOSTRAS_SUFICIENTES else None


def localizar_colunas_bloqueadas(
    colunas: list[str], amostra: list[list[str]]
) -> list[ColunaBloqueada]:
    bloqueadas = []
    for indice, coluna in enumerate(colunas):
        valores = (linha[indice] for linha in amostra if indice < len(linha))
        motivo = motivo_pelo_nome(coluna) or _motivo_pela_amostra(valores)
        if motivo is not None:
            bloqueadas.append(ColunaBloqueada(coluna, motivo))
    return bloqueadas
