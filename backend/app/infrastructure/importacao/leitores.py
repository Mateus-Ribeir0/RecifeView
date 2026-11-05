import bz2
import codecs
import csv
import gzip
import io
import json
import lzma
import zipfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import IO, Any, cast

from openpyxl import load_workbook

from app.domain.erros import ArquivoIlegivel

SEPARADORES = (";", ",", "\t", "|")
TAMANHO_DA_AMOSTRA = 16 * 1024 * 1024
TAMANHO_DO_CABECALHO = 512 * 1024
TAMANHO_MAXIMO_DE_CAMPO = 10**8
ASSINATURA_ZIP = b"PK\x03\x04"
ASSINATURA_GZIP = b"\x1f\x8b"
ASSINATURA_XZ = b"\xfd7zXZ\x00"
ASSINATURA_BZIP2 = b"BZh"
TAMANHO_DA_ASSINATURA = 8
ABRIDORES: tuple[tuple[bytes, Callable[..., Any]], ...] = (
    (ASSINATURA_GZIP, gzip.open),
    (ASSINATURA_XZ, lzma.open),
    (ASSINATURA_BZIP2, bz2.open),
)
EXTENSOES_DE_TABELA = (".csv", ".tsv", ".txt", ".json")
CARACTERES_DE_LINHA_VAZIA = " ;,\t|﻿\r\n"
CHAVES_COM_REGISTROS = ("records", "dados", "data", "registros")

csv.field_size_limit(TAMANHO_MAXIMO_DE_CAMPO)


@dataclass(frozen=True)
class TabelaLida:
    formato: str
    codificacao: str | None
    separador: str | None
    colunas: list[str]
    produtor_de_linhas: Callable[[], Iterator[list[str]]]

    def linhas(self) -> Iterator[list[str]]:
        return self.produtor_de_linhas()


def _nomear_colunas(cabecalho: list[str]) -> list[str]:
    limpo = [celula.strip().lstrip("﻿") for celula in cabecalho]
    while limpo and not limpo[-1]:
        limpo.pop()
    nomes: list[str] = []
    for posicao, nome in enumerate(limpo, start=1):
        base = nome or f"coluna_{posicao}"
        repeticoes = sum(1 for existente in nomes if existente == base)
        nomes.append(base if repeticoes == 0 else f"{base}_{repeticoes + 1}")
    return nomes


def _maior_tabela_do_zip(arquivo: zipfile.ZipFile) -> str:
    candidatos = [
        info
        for info in arquivo.infolist()
        if not info.is_dir() and info.filename.lower().endswith(EXTENSOES_DE_TABELA)
    ]
    if not candidatos:
        raise ArquivoIlegivel
    return max(candidatos, key=lambda info: info.file_size).filename


@contextmanager
def _abrir_conteudo(caminho: Path) -> Iterator[IO[bytes]]:
    """Abre o arquivo já descompactado, qualquer que seja o formato de compactação."""
    with caminho.open("rb") as bruto:
        assinatura = bruto.read(TAMANHO_DA_ASSINATURA)
    if assinatura.startswith(ASSINATURA_ZIP):
        with zipfile.ZipFile(caminho) as pacote, pacote.open(_maior_tabela_do_zip(pacote)) as dados:
            yield dados
        return
    abrir = next((abridor for marca, abridor in ABRIDORES if assinatura.startswith(marca)), open)
    with abrir(caminho, "rb") as dados:
        yield cast(IO[bytes], dados)


def _e_planilha(caminho: Path) -> bool:
    if not zipfile.is_zipfile(caminho):
        return False
    with zipfile.ZipFile(caminho) as pacote:
        return "xl/workbook.xml" in pacote.namelist()


def _detectar_codificacao(amostra: bytes) -> str:
    decodificador = codecs.getincrementaldecoder("utf-8")()
    try:
        decodificador.decode(amostra)
    except UnicodeDecodeError:
        return "cp1252"
    return "utf-8-sig"


def _detectar_separador(linha: str) -> str:
    return max(SEPARADORES, key=linha.count)


def _primeira_linha_com_conteudo(texto: IO[str]) -> str:
    for linha in texto:
        if linha.strip(CARACTERES_DE_LINHA_VAZIA):
            return linha
    return ""


def _ler_delimitado(caminho: Path, codificacao: str, formato: str) -> TabelaLida:
    with _abrir_conteudo(caminho) as conteudo:
        texto = io.TextIOWrapper(conteudo, encoding=codificacao, errors="replace", newline="")
        primeira = _primeira_linha_com_conteudo(texto)
    if not primeira:
        return TabelaLida(formato, codificacao, None, [], lambda: iter(()))
    separador = _detectar_separador(primeira)
    colunas = _nomear_colunas(next(csv.reader([primeira], delimiter=separador)))

    def linhas() -> Iterator[list[str]]:
        with _abrir_conteudo(caminho) as conteudo:
            texto = io.TextIOWrapper(conteudo, encoding=codificacao, errors="replace", newline="")
            _primeira_linha_com_conteudo(texto)
            yield from csv.reader(texto, delimiter=separador)

    return TabelaLida(formato, codificacao, separador, colunas, linhas)


def _registros_do_json(dados: Any) -> list[dict[str, Any]]:
    if isinstance(dados, list):
        return [item for item in dados if isinstance(item, dict)]
    if not isinstance(dados, dict):
        raise ArquivoIlegivel
    for chave in CHAVES_COM_REGISTROS:
        if isinstance(dados.get(chave), list):
            return _registros_do_json(dados[chave])
    if isinstance(dados.get("result"), dict):
        return _registros_do_json(dados["result"])
    raise ArquivoIlegivel


def _celula_em_texto(valor: object) -> str:
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def _ler_json(caminho: Path, codificacao: str) -> TabelaLida:
    with _abrir_conteudo(caminho) as conteudo:
        try:
            registros = _registros_do_json(json.loads(conteudo.read().decode(codificacao)))
        except ValueError as erro:
            raise ArquivoIlegivel from erro
    colunas = list(dict.fromkeys(chave for registro in registros[:1000] for chave in registro))

    def linhas() -> Iterator[list[str]]:
        for registro in registros:
            yield [_celula_em_texto(registro.get(coluna)) for coluna in colunas]

    return TabelaLida("json", codificacao, None, colunas, linhas)


def _linhas_da_planilha(caminho: Path) -> Iterator[list[str]]:
    planilha = load_workbook(caminho, read_only=True, data_only=True)
    try:
        for linha in planilha.worksheets[0].iter_rows(values_only=True):
            celulas = [_celula_em_texto(valor) for valor in linha]
            if any(celulas):
                yield celulas
    finally:
        planilha.close()


def _ler_planilha(caminho: Path) -> TabelaLida:
    try:
        cabecalho = next(_linhas_da_planilha(caminho), [])
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as erro:
        raise ArquivoIlegivel from erro

    def linhas() -> Iterator[list[str]]:
        produtor = _linhas_da_planilha(caminho)
        next(produtor, None)
        yield from produtor

    return TabelaLida("xlsx", None, None, _nomear_colunas(cabecalho), linhas)


def _ler_formato_de_texto(caminho: Path) -> TabelaLida:
    with _abrir_conteudo(caminho) as conteudo:
        amostra = conteudo.read(TAMANHO_DA_AMOSTRA)
    codificacao = _detectar_codificacao(amostra)
    inicio = amostra[:TAMANHO_DO_CABECALHO].decode(codificacao, errors="replace").lstrip()
    if inicio[:1] in ("[", "{"):
        return _ler_json(caminho, codificacao)
    return _ler_delimitado(caminho, codificacao, "csv")


class LeitorDeArquivos:
    """Abre CSV, TSV, JSON e XLSX, soltos ou dentro de ZIP, GZ, XZ e BZ2."""

    def abrir(self, caminho: Path) -> TabelaLida:
        try:
            if _e_planilha(caminho):
                return _ler_planilha(caminho)
            return _ler_formato_de_texto(caminho)
        except (OSError, EOFError, lzma.LZMAError, zipfile.BadZipFile) as erro:
            raise ArquivoIlegivel from erro
