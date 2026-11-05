from dataclasses import dataclass

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import (
    FiltroDeImportacoes,
    PaginaDeImportacoes,
    PaginaDeRegistros,
)
from app.domain.importacao.importacao import Importacao


@dataclass(frozen=True)
class ImportacaoDetalhada:
    importacao: Importacao
    pode_desfazer: bool


@dataclass(frozen=True)
class ConsultarImportacao:
    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> ImportacaoDetalhada:
        importacao = self.servicos.obter(importacao_id)
        ultima = self.servicos.importacoes.ultima_concluida()
        pode_desfazer = (
            ultima is not None and ultima.id == importacao_id and not importacao.carga_inicial
        )
        return ImportacaoDetalhada(importacao, pode_desfazer)


@dataclass(frozen=True)
class ListarImportacoes:
    servicos: ServicosDeImportacao

    def executar(self, filtro: FiltroDeImportacoes) -> PaginaDeImportacoes:
        return self.servicos.importacoes.listar(filtro)


@dataclass(frozen=True)
class ListarRegistrosImportados:
    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int, limite: int, deslocamento: int) -> PaginaDeRegistros:
        self.servicos.obter(importacao_id)
        return self.servicos.carregador.listar_registros(importacao_id, limite, deslocamento)
