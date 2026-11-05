from dataclasses import dataclass, replace

from app.application.casos_de_uso.importacoes.carregar_importacao import CarregarImportacao
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.domain.importacao.importacao import Importacao, StatusDaImportacao

MENSAGEM_DE_INTERRUPCAO = "A API reiniciou durante o processamento. Envie o arquivo de novo."


@dataclass(frozen=True)
class RetomarImportacoes:
    """Ao subir, nenhuma tarefa da fila em processo sobreviveu: fecha o que ficou pela metade."""

    servicos: ServicosDeImportacao

    def executar(self) -> None:
        for importacao in self.servicos.importacoes.em_andamento():
            if importacao.status is StatusDaImportacao.ATUALIZANDO_PAINEL:
                self._retomar_atualizacao(importacao)
                continue
            self.servicos.importacoes.salvar(
                replace(
                    importacao,
                    status=StatusDaImportacao.FALHOU,
                    mensagem_de_erro=MENSAGEM_DE_INTERRUPCAO,
                )
            )

    def _retomar_atualizacao(self, importacao: Importacao) -> None:
        carregar = CarregarImportacao(self.servicos)
        self.servicos.fila.enfileirar(lambda: carregar.atualizar_painel(importacao.id))
