import re
import unicodedata
from functools import lru_cache

MARCAS_DE_CODIFICACAO_QUEBRADA = ("Ã", "Â")
ESPACOS = re.compile(r"\s+")
CACHE_DE_TEXTOS = 300_000


def _consertar_codificacao(valor: str) -> str:
    if not any(marca in valor for marca in MARCAS_DE_CODIFICACAO_QUEBRADA):
        return valor
    try:
        return valor.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return valor


@lru_cache(maxsize=CACHE_DE_TEXTOS)
def normalizar_texto(valor: str) -> str:
    """Maiúsculas, sem acento e com espaço simples: a forma em que as fontes são comparadas."""
    consertado = _consertar_codificacao(valor)
    sem_acento = unicodedata.normalize("NFKD", consertado).encode("ascii", "ignore").decode()
    return ESPACOS.sub(" ", sem_acento).strip().upper()


def normalizar_nome_de_coluna(nome: str) -> str:
    """Compara nomes de coluna sem depender de caixa, acento, espaço ou pontuação."""
    return re.sub(r"[^A-Z0-9]+", "_", normalizar_texto(nome)).strip("_")
