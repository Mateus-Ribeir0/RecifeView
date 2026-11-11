import re

from app.domain.erros import ProtocoloInvalido

TAMANHO_MINIMO_DO_PROTOCOLO = 4
TAMANHO_MAXIMO_DO_PROTOCOLO = 40
_FORMATO_DO_PROTOCOLO = re.compile(r"^[A-Z0-9./-]+$")
_ESPACOS = re.compile(r"\s+")


def normalizar_protocolo(valor: str) -> str | None:
    """Cada fonte escreve o protocolo de um jeito: sem espaços e em maiúsculas, a busca acha."""
    protocolo = _ESPACOS.sub("", valor).upper()
    return protocolo or None


def exigir_protocolo(valor: str) -> str:
    protocolo = normalizar_protocolo(valor) or ""
    tamanho_aceito = TAMANHO_MINIMO_DO_PROTOCOLO <= len(protocolo) <= TAMANHO_MAXIMO_DO_PROTOCOLO
    if not tamanho_aceito or not _FORMATO_DO_PROTOCOLO.match(protocolo):
        raise ProtocoloInvalido
    return protocolo
