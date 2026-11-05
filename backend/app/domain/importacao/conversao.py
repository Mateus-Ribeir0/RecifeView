import re
from functools import lru_cache
from hashlib import blake2b

VERDADEIROS = frozenset({"TRUE", "SIM", "S", "1", "VERDADEIRO"})
FALSOS = frozenset({"FALSE", "NAO", "N", "0", "FALSO"})
PADRAO_ANO_NO_ARQUIVO = re.compile(r"(?<!\d)(20\d{2})(?!\d)")
BYTES_DO_HASH = 8
CACHE_DE_INTEIROS = 50_000


@lru_cache(maxsize=CACHE_DE_INTEIROS)
def ler_inteiro(valor: str) -> int | None:
    try:
        return int(float(valor.replace(",", ".")))
    except ValueError:
        return None


def ler_booleano(valor: str) -> bool | None:
    texto = valor.strip().upper()
    if texto in VERDADEIROS:
        return True
    return False if texto in FALSOS else None


def calcular_hash(texto: str) -> int:
    resumo = blake2b(texto.encode(), digest_size=BYTES_DO_HASH).digest()
    return int.from_bytes(resumo, "big", signed=True)


def ano_do_nome_do_arquivo(nome: str) -> int | None:
    anos = PADRAO_ANO_NO_ARQUIVO.findall(nome)
    return int(anos[-1]) if anos else None
