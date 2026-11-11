import csv
import urllib.request
from http.client import HTTPMessage
from io import BytesIO
from pathlib import Path

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, text

from app.domain.erros import OrigemIndisponivel, OrigemRecusada
from app.infrastructure.importacao.armazenamento_local import ArmazenamentoLocal
from app.infrastructure.importacao.origens import (
    DownloadPorHttps,
    ExtracaoDeBanco,
    RedirecionamentoConferido,
)
from tests.integracao.test_importacao_e_painel import URL_DO_BANCO_DE_TESTE

LIMITE_EM_BYTES = 1024 * 1024
SEGUNDOS_LIMITE = 10


def armazenamento(pasta: Path) -> ArmazenamentoLocal:
    return ArmazenamentoLocal(pasta, LIMITE_EM_BYTES)


def test_redirecionamento_para_host_fora_da_lista_e_recusado() -> None:
    conferidor = RedirecionamentoConferido(["dados.recife.pe.gov.br"])
    requisicao = urllib.request.Request("https://dados.recife.pe.gov.br/a.csv")

    with pytest.raises(OrigemRecusada):
        conferidor.redirect_request(
            requisicao, BytesIO(), 302, "Found", HTTPMessage(), "https://interno.exemplo/a.csv"
        )


def test_download_sem_https_nem_comeca(tmp_path: Path) -> None:
    download = DownloadPorHttps(armazenamento(tmp_path), ["dados.recife.pe.gov.br"])

    with pytest.raises(OrigemRecusada):
        download.baixar("http://dados.recife.pe.gov.br/a.csv")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)
class TestExtracaoDeBanco:
    @pytest.fixture
    def extracao(self, tmp_path: Path) -> ExtracaoDeBanco:
        assert URL_DO_BANCO_DE_TESTE
        motor = create_engine(URL_DO_BANCO_DE_TESTE)
        with motor.begin() as conexao:
            conexao.execute(text("DROP TABLE IF EXISTS public.origem_de_teste"))
            conexao.execute(
                text("CREATE TABLE public.origem_de_teste (protocolo text, aberto_em date)")
            )
            conexao.execute(
                text(
                    "INSERT INTO public.origem_de_teste VALUES "
                    "('2026/1', DATE '2026-09-01'), ('2026/2', NULL)"
                )
            )
        motor.dispose()
        bancos = {"teste": SecretStr(URL_DO_BANCO_DE_TESTE)}
        return ExtracaoDeBanco(armazenamento(tmp_path), bancos, SEGUNDOS_LIMITE)

    def test_consulta_vira_csv_com_cabecalho(
        self, extracao: ExtracaoDeBanco, tmp_path: Path
    ) -> None:
        arquivo = extracao.extrair("teste", "SELECT * FROM public.origem_de_teste ORDER BY 1")

        conteudo = (tmp_path / arquivo.referencia / "original").read_text()
        assert list(csv.reader(conteudo.splitlines())) == [
            ["protocolo", "aberto_em"],
            ["2026/1", "2026-09-01"],
            ["2026/2", ""],
        ]
        assert arquivo.nome.startswith("teste-")

    def test_consulta_que_tenta_escrever_cai_na_transacao_so_de_leitura(
        self, extracao: ExtracaoDeBanco, tmp_path: Path
    ) -> None:
        consulta = "WITH apagados AS (DELETE FROM public.origem_de_teste RETURNING 1) SELECT 1"

        with pytest.raises(OrigemIndisponivel):
            extracao.extrair("teste", consulta)
        assert list(tmp_path.iterdir()) == []

    def test_conexao_que_nao_esta_na_configuracao_e_recusada(
        self, extracao: ExtracaoDeBanco
    ) -> None:
        with pytest.raises(OrigemRecusada):
            extracao.extrair("outro", "SELECT 1")
