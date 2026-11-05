import hashlib

from app.domain.importacao.texto import normalizar_texto

TAMANHO_DO_ID_LOCAL = 12
NUMEROS_SEM_INFORMACAO = frozenset({"", "0", "S/N", "SN"})


def gerar_id_local(partes_do_endereco: tuple[str, ...], sal: str) -> str | None:
    """Mesmo hash do pipeline do grupo, para o pseudônimo continuar valendo entre arquivos."""
    chave = "|".join(normalizar_texto(parte) for parte in partes_do_endereco)
    if not chave.strip("| "):
        return None
    return hashlib.sha256((sal + chave).encode()).hexdigest()[:TAMANHO_DO_ID_LOCAL]


def numero_foi_informado(numero: str) -> bool:
    return numero.strip().upper() not in NUMEROS_SEM_INFORMACAO
