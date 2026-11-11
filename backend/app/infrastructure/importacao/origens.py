import csv
import io
import logging
import urllib.error
import urllib.request
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from http.client import HTTPMessage
from typing import IO, Any

from pydantic import SecretStr
from sqlalchemy import Engine, create_engine

from app.application.portas.importacoes import (
    ArmazenamentoDeArquivos,
    ArquivoRecebido,
    RecebimentoDeArquivo,
)
from app.domain.erros import ErroDeDominio, OrigemIndisponivel, OrigemRecusada
from app.domain.importacao.origens import (
    exigir_consulta_de_leitura,
    exigir_endereco_permitido,
    nome_do_arquivo_do_endereco,
)

TAMANHO_DO_BLOCO = 1024 * 1024
SEGUNDOS_DE_ESPERA_DO_DOWNLOAD = 120
LINHAS_POR_LOTE = 5000
MILISSEGUNDOS_POR_SEGUNDO = 1000
CABECALHOS_DO_DOWNLOAD = {"User-Agent": "RecifeView (importacao de dados abertos)"}

registro_de_log = logging.getLogger(__name__)


class RedirecionamentoConferido(urllib.request.HTTPRedirectHandler):
    """Um redirecionamento também precisa cair num host permitido."""

    def __init__(self, hosts_permitidos: Sequence[str]) -> None:
        self._hosts = hosts_permitidos

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> urllib.request.Request | None:
        exigir_endereco_permitido(newurl, self._hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _copiar(origem: IO[bytes], recebimento: RecebimentoDeArquivo) -> None:
    while bloco := origem.read(TAMANHO_DO_BLOCO):
        recebimento.gravar(bloco)


class DownloadPorHttps:
    def __init__(self, armazenamento: ArmazenamentoDeArquivos, hosts: Sequence[str]) -> None:
        self._armazenamento = armazenamento
        self._hosts = list(hosts)
        self._abridor = urllib.request.build_opener(RedirecionamentoConferido(self._hosts))

    @property
    def hosts_permitidos(self) -> list[str]:
        return self._hosts

    def baixar(self, endereco: str) -> ArquivoRecebido:
        url = exigir_endereco_permitido(endereco, self._hosts)
        recebimento = self._armazenamento.iniciar_recebimento(nome_do_arquivo_do_endereco(url))
        requisicao = urllib.request.Request(url, headers=CABECALHOS_DO_DOWNLOAD)  # noqa: S310
        try:
            with self._abridor.open(requisicao, timeout=SEGUNDOS_DE_ESPERA_DO_DOWNLOAD) as resposta:
                _copiar(resposta, recebimento)
        except ErroDeDominio:
            recebimento.abandonar()
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as erro:
            recebimento.abandonar()
            registro_de_log.error("Download de importação falhou: %s", type(erro).__name__)
            raise OrigemIndisponivel from erro
        return recebimento.concluir()


def _texto_da_celula(valor: object) -> str:
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.isoformat()
    return str(valor)


def _lote_em_csv(linhas: Iterable[Sequence[object]]) -> bytes:
    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    escritor.writerows([_texto_da_celula(valor) for valor in linha] for linha in linhas)
    return buffer.getvalue().encode()


class ExtracaoDeBanco:
    """Lê de um banco configurado, em transação só de leitura, e entrega um CSV à importação."""

    def __init__(
        self,
        armazenamento: ArmazenamentoDeArquivos,
        bancos: dict[str, SecretStr],
        segundos_limite: int,
    ) -> None:
        self._armazenamento = armazenamento
        self._bancos = bancos
        self._segundos_limite = segundos_limite
        self._motores: dict[str, Engine] = {}

    def conexoes(self) -> list[str]:
        return sorted(self._bancos)

    def extrair(self, conexao: str, consulta: str) -> ArquivoRecebido:
        consulta_limpa = exigir_consulta_de_leitura(consulta)
        motor = self._motor(conexao)
        carimbo = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        recebimento = self._armazenamento.iniciar_recebimento(f"{conexao}-{carimbo}.csv")
        try:
            self._ler_para(motor, consulta_limpa, recebimento)
        except ErroDeDominio:
            recebimento.abandonar()
            raise
        except Exception as erro:
            recebimento.abandonar()
            registro_de_log.error("Extração do banco %s falhou: %s", conexao, type(erro).__name__)
            raise OrigemIndisponivel from erro
        return recebimento.concluir()

    def _motor(self, conexao: str) -> Engine:
        if conexao not in self._bancos:
            raise OrigemRecusada("Escolha uma das conexões configuradas.")
        if conexao not in self._motores:
            url = self._bancos[conexao].get_secret_value()
            self._motores[conexao] = create_engine(url, pool_pre_ping=True)
        return self._motores[conexao]

    def _ler_para(self, motor: Engine, consulta: str, recebimento: RecebimentoDeArquivo) -> None:
        limite_em_ms = self._segundos_limite * MILISSEGUNDOS_POR_SEGUNDO
        with motor.connect() as conexao, conexao.begin():
            conexao.exec_driver_sql("SET TRANSACTION READ ONLY")
            conexao.exec_driver_sql(f"SET LOCAL statement_timeout = {int(limite_em_ms)}")
            resultado: Any = conexao.execution_options(stream_results=True).exec_driver_sql(
                consulta
            )
            recebimento.gravar(_lote_em_csv([list(resultado.keys())]))
            while lote := resultado.fetchmany(LINHAS_POR_LOTE):
                recebimento.gravar(_lote_em_csv(lote))
