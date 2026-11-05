from dataclasses import dataclass, replace

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.domain.importacao.importacao import Importacao, StatusDaImportacao


@dataclass(frozen=True)
class CancelarImportacao:
    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> Importacao:
        importacao = self.servicos.obter(importacao_id)
        importacao.exigir_que_possa_ser_cancelada()
        cancelada = replace(
            importacao.com_status(StatusDaImportacao.CANCELADA), arquivo_guardado=False
        )
        self.servicos.importacoes.salvar(cancelada)
        self.servicos.armazenamento.remover(str(importacao.estrutura["referencia"]))
        return cancelada
