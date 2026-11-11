from dataclasses import dataclass
from uuid import UUID

from app.application.casos_de_uso.importacoes.receber_arquivo import ReceberArquivo
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import OrigensDeDados
from app.domain.importacao.importacao import Importacao


@dataclass(frozen=True)
class PedidoDeExtracao:
    conexao: str
    consulta: str


@dataclass(frozen=True)
class ImportarDeEndereco:
    """O arquivo baixado segue o mesmo caminho do enviado: colunas, pendências, carga, desfazer."""

    servicos: ServicosDeImportacao
    origens: OrigensDeDados

    def executar(self, endereco: str, usuario_id: UUID) -> Importacao:
        arquivo = self.origens.por_endereco.baixar(endereco)
        return ReceberArquivo(self.servicos).executar(arquivo, usuario_id)


@dataclass(frozen=True)
class ImportarDeBanco:
    servicos: ServicosDeImportacao
    origens: OrigensDeDados

    def executar(self, pedido: PedidoDeExtracao, usuario_id: UUID) -> Importacao:
        arquivo = self.origens.por_banco.extrair(pedido.conexao, pedido.consulta)
        return ReceberArquivo(self.servicos).executar(arquivo, usuario_id)
