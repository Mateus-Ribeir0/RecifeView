from dataclasses import dataclass, replace

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.domain.erros import ImportacaoNaoPodeSerDesfeita
from app.domain.importacao.importacao import Importacao, StatusDaImportacao


@dataclass(frozen=True)
class DesfazerImportacao:
    """Só a importação mais recente volta: uma mais nova pode ter atualizado as mesmas linhas."""

    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> Importacao:
        importacao = self.servicos.obter(importacao_id)
        ultima = self.servicos.importacoes.ultima_concluida()
        if ultima is None or ultima.id != importacao_id or importacao.carga_inicial:
            raise ImportacaoNaoPodeSerDesfeita
        em_andamento = importacao.com_status(StatusDaImportacao.DESFAZENDO)
        self.servicos.importacoes.salvar(em_andamento)
        self.servicos.fila.enfileirar(lambda: self._desfazer(importacao_id))
        return em_andamento

    def _desfazer(self, importacao_id: int) -> None:
        def registrar_avanco(progresso: int) -> None:
            self.servicos.importacoes.atualizar_progresso(
                importacao_id, StatusDaImportacao.DESFAZENDO, progresso
            )

        self.servicos.carregador.desfazer(importacao_id)
        self.servicos.atualizador.atualizar(registrar_avanco)
        importacao = self.servicos.obter(importacao_id)
        self.servicos.importacoes.salvar(
            replace(
                importacao,
                status=StatusDaImportacao.DESFEITA,
                progresso=100,
                desfeita_em=self.servicos.relogio.agora(),
            )
        )
