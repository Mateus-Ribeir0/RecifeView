from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from app.application.casos_de_uso.importacoes.analisar_arquivo import AnalisarArquivo
from app.application.casos_de_uso.importacoes.carregar_importacao import CarregarImportacao
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.casos_de_uso.importacoes.validar_importacao import ValidarImportacao
from app.application.portas.importacoes import ArquivoRecebido, NovaImportacao
from app.domain.importacao.importacao import Importacao, StatusDaImportacao

TAMANHO_DO_BLOCO = 1024 * 1024


class ImportacaoPendente(Exception):
    def __init__(self, importacao_id: int) -> None:
        super().__init__(str(importacao_id))
        self.importacao_id = importacao_id


@dataclass(frozen=True)
class ImportarPeloTerminal:
    """Mesmo caminho da tela, sem perguntas: se algo precisar de decisão, para e avisa."""

    servicos: ServicosDeImportacao

    def executar(self, caminho: Path, data_do_retrato: date, carga_inicial: bool) -> Importacao:
        return self.executar_recebido(self._copiar_arquivo(caminho), data_do_retrato, carga_inicial)

    def executar_recebido(
        self, arquivo: ArquivoRecebido, data_do_retrato: date, carga_inicial: bool
    ) -> Importacao:
        """Para o arquivo que já chegou por outra origem (endereço ou banco)."""
        importacao = self.servicos.importacoes.criar(
            NovaImportacao(arquivo, None, carga_inicial), StatusDaImportacao.ANALISANDO
        )
        AnalisarArquivo(self.servicos).executar(importacao.id)
        importacao = self.servicos.obter(importacao.id)
        if importacao.status is not StatusDaImportacao.AGUARDANDO_COLUNAS:
            return importacao
        importacao = self._com_data_do_retrato(importacao, data_do_retrato)
        if not carga_inicial:
            self._exigir_que_nao_haja_pendencias(importacao)
        self.servicos.importacoes.salvar(importacao.com_status(StatusDaImportacao.CARREGANDO))
        CarregarImportacao(self.servicos).executar(importacao.id)
        return self.servicos.obter(importacao.id)

    def _copiar_arquivo(self, caminho: Path) -> ArquivoRecebido:
        recebimento = self.servicos.armazenamento.iniciar_recebimento(caminho.name)
        with caminho.open("rb") as origem:
            while bloco := origem.read(TAMANHO_DO_BLOCO):
                recebimento.gravar(bloco)
        return recebimento.concluir()

    def _com_data_do_retrato(self, importacao: Importacao, retrato: date) -> Importacao:
        decisoes = replace(importacao.decisoes, data_do_retrato=retrato)
        atualizada = replace(importacao, decisoes=decisoes, data_do_retrato=retrato)
        self.servicos.importacoes.salvar(atualizada)
        return atualizada

    def _exigir_que_nao_haja_pendencias(self, importacao: Importacao) -> None:
        ValidarImportacao(self.servicos).executar(importacao.id)
        if self.servicos.obter(importacao.id).status is not StatusDaImportacao.PRONTA:
            raise ImportacaoPendente(importacao.id)
