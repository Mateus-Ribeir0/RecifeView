from dataclasses import dataclass, field
from uuid import uuid4

import pytest

from app.application.casos_de_uso.importacoes.receber_de_origem import (
    ImportarDeBanco,
    ImportarDeEndereco,
    PedidoDeExtracao,
)
from app.application.portas.importacoes import ArquivoRecebido, OrigensDeDados
from app.domain.erros import OrigemRecusada
from app.domain.importacao.origens import (
    exigir_consulta_de_leitura,
    exigir_endereco_permitido,
    nome_do_arquivo_do_endereco,
)
from tests.fakes_importacao import TabelaFalsa, criar_servicos

HOSTS = ["dados.recife.pe.gov.br"]
ENDERECO_DO_156 = "https://dados.recife.pe.gov.br/dataset/x/resource/y/download/sedec_2025.csv"


@pytest.mark.parametrize(
    "endereco",
    [
        "http://dados.recife.pe.gov.br/arquivo.csv",
        "https://outro.exemplo/arquivo.csv",
        "https://usuario:senha@dados.recife.pe.gov.br/arquivo.csv",
        "file:///etc/passwd",
        "https://dados.recife.pe.gov.br.exemplo/arquivo.csv",
    ],
)
def test_endereco_fora_da_lista_ou_sem_https_e_recusado(endereco: str) -> None:
    with pytest.raises(OrigemRecusada):
        exigir_endereco_permitido(endereco, HOSTS)


def test_endereco_do_portal_e_aceito_e_da_nome_ao_arquivo() -> None:
    assert exigir_endereco_permitido(f"  {ENDERECO_DO_156} ", HOSTS) == ENDERECO_DO_156
    assert nome_do_arquivo_do_endereco(ENDERECO_DO_156) == "sedec_2025.csv"
    assert nome_do_arquivo_do_endereco("https://dados.recife.pe.gov.br/") == "download.csv"


@pytest.mark.parametrize(
    "consulta",
    [
        "DELETE FROM pedidos",
        "SELECT 1; DROP TABLE pedidos",
        "",
        "UPDATE pedidos SET situacao = 'x'",
    ],
)
def test_consulta_que_nao_e_leitura_e_recusada(consulta: str) -> None:
    with pytest.raises(OrigemRecusada):
        exigir_consulta_de_leitura(consulta)


def test_consulta_de_leitura_perde_o_ponto_e_virgula_final() -> None:
    assert exigir_consulta_de_leitura(" with x as (select 1) select * from x; ") == (
        "with x as (select 1) select * from x"
    )


ARQUIVO_BAIXADO = ArquivoRecebido("ref", "156_2026.csv", 10, "hash")


@dataclass
class OrigemFalsa:
    pedidos: list[tuple[str, ...]] = field(default_factory=list)

    @property
    def hosts_permitidos(self) -> list[str]:
        return HOSTS

    def baixar(self, endereco: str) -> ArquivoRecebido:
        self.pedidos.append((endereco,))
        return ARQUIVO_BAIXADO

    def conexoes(self) -> list[str]:
        return ["sgde"]

    def extrair(self, conexao: str, consulta: str) -> ArquivoRecebido:
        self.pedidos.append((conexao, consulta))
        return ARQUIVO_BAIXADO


def test_arquivo_baixado_abre_a_importacao_como_um_enviado() -> None:
    servicos, origem = criar_servicos(TabelaFalsa([], [])), OrigemFalsa()
    origens = OrigensDeDados(origem, origem)

    importacao = ImportarDeEndereco(servicos, origens).executar(ENDERECO_DO_156, uuid4())

    assert origem.pedidos == [(ENDERECO_DO_156,)]
    assert importacao.nome_do_arquivo == "156_2026.csv"


def test_consulta_ao_banco_abre_a_importacao() -> None:
    servicos, origem = criar_servicos(TabelaFalsa([], [])), OrigemFalsa()
    pedido = PedidoDeExtracao("sgde", "SELECT * FROM pedidos")

    ImportarDeBanco(servicos, OrigensDeDados(origem, origem)).executar(pedido, uuid4())

    assert origem.pedidos == [("sgde", "SELECT * FROM pedidos")]
