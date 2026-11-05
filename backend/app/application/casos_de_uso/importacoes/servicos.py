from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import PurePath

from app.application.portas.importacoes import (
    ArmazenamentoDeArquivos,
    AtualizadorDoPainel,
    CarregadorDeDemandas,
    FilaDeImportacoes,
    ImportacaoRepository,
    LeitorDeTabelas,
    ReferenciasRepository,
    TabelaDoArquivo,
)
from app.application.portas.relogio import Relogio
from app.domain.erros import ImportacaoNaoEncontrada
from app.domain.importacao.chaves import OrdemPorConteudo
from app.domain.importacao.importacao import Importacao
from app.domain.importacao.layouts import CodigoDoLayout
from app.domain.importacao.normalizador import (
    NormalizadorDeLinhas,
    PlanoDeNormalizacao,
)
from app.domain.importacao.registro import RegistroDeDemanda


@dataclass(frozen=True)
class ServicosDeImportacao:
    """As portas que os casos de uso de importação usam juntas."""

    importacoes: ImportacaoRepository
    armazenamento: ArmazenamentoDeArquivos
    leitor: LeitorDeTabelas
    carregador: CarregadorDeDemandas
    atualizador: AtualizadorDoPainel
    referencias: ReferenciasRepository
    fila: FilaDeImportacoes
    relogio: Relogio
    sal: str | None = None

    def obter(self, importacao_id: int) -> Importacao:
        importacao = self.importacoes.buscar(importacao_id)
        if importacao is None:
            raise ImportacaoNaoEncontrada
        return importacao

    def abrir_tabela(self, importacao: Importacao) -> TabelaDoArquivo:
        referencia = str(importacao.estrutura["referencia"])
        return self.leitor.abrir(self.armazenamento.localizar(referencia))

    def _criar_normalizador(
        self, importacao: Importacao, tabela: TabelaDoArquivo, ordem: OrdemPorConteudo
    ) -> NormalizadorDeLinhas:
        data_do_retrato = importacao.decisoes.data_do_retrato or self.relogio.agora().date()
        plano = PlanoDeNormalizacao(
            colunas=tuple(tabela.colunas),
            layout=CodigoDoLayout(importacao.layout or CodigoDoLayout.MANUAL),
            decisoes=importacao.decisoes,
            arquivo_origem=PurePath(importacao.nome_do_arquivo).stem,
            data_do_retrato=data_do_retrato,
            importacao_id=importacao.id,
            sal=self.sal,
        )
        return NormalizadorDeLinhas(plano, self.referencias.carregar(), ordem)

    def preparar_normalizador(
        self, importacao: Importacao, tabela: TabelaDoArquivo
    ) -> NormalizadorDeLinhas:
        """Percorre o arquivo uma vez para ordenar os repetidos antes de gerar as chaves."""
        ordem = OrdemPorConteudo()
        primeira_passada = self._criar_normalizador(importacao, tabela, ordem)
        for linha in tabela.linhas():
            primeira_passada.anotar(linha)
        ordem.fechar()
        return self._criar_normalizador(importacao, tabela, ordem)

    def criar_normalizador_da_previa(
        self, importacao: Importacao, tabela: TabelaDoArquivo
    ) -> NormalizadorDeLinhas:
        """Serve só para mostrar a amostra: sem a ordem, as chaves dos repetidos colidem."""
        return self._criar_normalizador(importacao, tabela, OrdemPorConteudo())


def registros_validos(
    tabela: TabelaDoArquivo, normalizador: NormalizadorDeLinhas
) -> Iterator[RegistroDeDemanda]:
    for linha in tabela.linhas():
        registro = normalizador.normalizar(linha)
        if registro is not None:
            yield registro
