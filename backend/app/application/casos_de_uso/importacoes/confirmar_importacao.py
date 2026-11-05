from dataclasses import dataclass

from app.application.casos_de_uso.importacoes.carregar_importacao import CarregarImportacao
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.domain.importacao.importacao import Importacao, StatusDaImportacao


@dataclass(frozen=True)
class ConfirmarImportacao:
    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> Importacao:
        importacao = self.servicos.obter(importacao_id)
        importacao.exigir_que_esteja_pronta()
        em_carga = importacao.com_status(StatusDaImportacao.CARREGANDO)
        self.servicos.importacoes.salvar(em_carga)
        carregar = CarregarImportacao(self.servicos)
        self.servicos.fila.enfileirar(lambda: carregar.executar(importacao_id))
        return em_carga
