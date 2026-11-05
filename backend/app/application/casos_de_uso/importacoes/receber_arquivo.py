from dataclasses import dataclass
from pathlib import PurePath
from uuid import UUID

from app.application.casos_de_uso.importacoes.analisar_arquivo import AnalisarArquivo
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import ArquivoRecebido, NovaImportacao
from app.domain.erros import ArquivoVazio
from app.domain.importacao.importacao import Importacao, StatusDaImportacao


@dataclass(frozen=True)
class ReceberArquivo:
    servicos: ServicosDeImportacao

    def executar(self, arquivo: ArquivoRecebido, usuario_id: UUID) -> Importacao:
        if arquivo.tamanho_em_bytes == 0:
            self.servicos.armazenamento.remover(arquivo.referencia)
            raise ArquivoVazio
        nome_seguro = PurePath(arquivo.nome).name
        limpo = ArquivoRecebido(
            arquivo.referencia, nome_seguro, arquivo.tamanho_em_bytes, arquivo.hash_do_arquivo
        )
        importacao = self.servicos.importacoes.criar(
            NovaImportacao(limpo, usuario_id), StatusDaImportacao.ANALISANDO
        )
        analisar = AnalisarArquivo(self.servicos)
        self.servicos.fila.enfileirar(lambda: analisar.executar(importacao.id))
        return importacao
