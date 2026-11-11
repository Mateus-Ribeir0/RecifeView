from collections.abc import Collection
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

from app.domain.erros import OrigemRecusada

ESQUEMA_ACEITO = "https"
NOME_PADRAO_DO_DOWNLOAD = "download.csv"
TAMANHO_MAXIMO_DA_CONSULTA = 5000
INICIOS_DE_CONSULTA_DE_LEITURA = ("SELECT", "WITH")


def exigir_endereco_permitido(endereco: str, hosts_permitidos: Collection[str]) -> str:
    """Só https e só os hosts da configuração: a API não vira ponte para a rede interna."""
    partes = urlsplit(endereco.strip())
    if partes.scheme != ESQUEMA_ACEITO:
        raise OrigemRecusada("Use um endereço que comece com https://.")
    if partes.username or partes.password:
        raise OrigemRecusada("O endereço não pode levar usuário nem senha.")
    host = (partes.hostname or "").lower()
    if host not in {permitido.lower() for permitido in hosts_permitidos}:
        raise OrigemRecusada(f"O endereço {host or 'informado'} não está na lista de permitidos.")
    return partes.geturl()


def nome_do_arquivo_do_endereco(endereco: str) -> str:
    nome = PurePosixPath(unquote(urlsplit(endereco).path)).name
    return nome or NOME_PADRAO_DO_DOWNLOAD


def exigir_consulta_de_leitura(consulta: str) -> str:
    """A transação só de leitura é a proteção de verdade; esta regra dá a mensagem clara antes."""
    limpa = consulta.strip().rstrip(";").strip()
    if not limpa or len(limpa) > TAMANHO_MAXIMO_DA_CONSULTA:
        raise OrigemRecusada(
            f"Escreva uma consulta de até {TAMANHO_MAXIMO_DA_CONSULTA} caracteres."
        )
    if ";" in limpa:
        raise OrigemRecusada("Mande um comando por vez.")
    primeira_palavra = limpa.split(maxsplit=1)[0].upper()
    if primeira_palavra not in INICIOS_DE_CONSULTA_DE_LEITURA:
        raise OrigemRecusada("A consulta precisa começar com SELECT ou WITH.")
    return limpa
