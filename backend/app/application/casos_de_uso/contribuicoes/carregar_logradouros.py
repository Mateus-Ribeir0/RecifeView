from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from app.application.portas.contribuicoes import ReferenciaDoFormulario
from app.application.portas.importacoes import TabelaDoArquivo
from app.domain.erros import ArquivoIlegivel
from app.domain.importacao.bairros import localizar_bairro
from app.domain.importacao.texto import normalizar_nome_de_coluna, normalizar_texto

COLUNA_DA_VIA = "LOGRADOURO"
COLUNA_DO_BAIRRO = "BAIRRO"
PEDIDOS_MINIMOS_POR_VIA = 2


def _indice(tabela: TabelaDoArquivo, nome: str) -> int:
    nomes = [normalizar_nome_de_coluna(coluna) for coluna in tabela.colunas]
    if nome not in nomes:
        raise ArquivoIlegivel
    return nomes.index(nome)


def _contar_vias(tabela: TabelaDoArquivo, bairros: dict[str, str]) -> Counter[tuple[str, str]]:
    via, bairro = _indice(tabela, COLUNA_DA_VIA), _indice(tabela, COLUNA_DO_BAIRRO)
    contagem: Counter[tuple[str, str]] = Counter()
    for linha in tabela.linhas():
        if max(via, bairro) >= len(linha):
            continue
        oficial = localizar_bairro(normalizar_texto(linha[bairro]), bairros)
        nome = normalizar_texto(linha[via])
        if oficial and nome:
            contagem[(oficial, nome)] += 1
    return contagem


def _vias_recorrentes(
    contagem: Counter[tuple[str, str]],
) -> Iterator[tuple[str, str, int]]:
    for (bairro, via), pedidos in contagem.items():
        if pedidos >= PEDIDOS_MINIMOS_POR_VIA:
            yield bairro, via, pedidos


@dataclass(frozen=True)
class CarregarLogradouros:
    """Monta a lista de vias a partir de arquivos públicos do 156, para escrever igual à fonte."""

    referencia: ReferenciaDoFormulario

    def executar(self, tabelas: Iterable[TabelaDoArquivo], bairros: dict[str, str]) -> int:
        contagem: Counter[tuple[str, str]] = Counter()
        for tabela in tabelas:
            contagem.update(_contar_vias(tabela, bairros))
        return self.referencia.somar_logradouros(_vias_recorrentes(contagem))
