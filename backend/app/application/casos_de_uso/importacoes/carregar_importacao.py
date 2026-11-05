from dataclasses import asdict, dataclass, replace
from datetime import date
from typing import Any

from app.application.casos_de_uso.importacoes.servicos import (
    ServicosDeImportacao,
    registros_validos,
)
from app.application.casos_de_uso.importacoes.validar_importacao import resumir_relatorio
from app.application.portas.importacoes import ResultadoDaCarga
from app.domain.importacao.decisoes import PoliticaDeRepetidos
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.relatorio import RelatorioDeLinhas

PROGRESSO_INICIAL_DAS_VIEWS = 0


@dataclass(frozen=True)
class CarregarImportacao:
    """Grava os registros na base, atualiza as views e fecha a importação."""

    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> None:
        importacao = self.servicos.obter(importacao_id)
        try:
            relatorio, carga = self._carregar(importacao)
        except Exception as erro:
            self._registrar_falha(importacao, erro)
            raise
        self._registrar_carga(importacao, relatorio, carga)
        self.atualizar_painel(importacao_id)

    def _carregar(self, importacao: Importacao) -> tuple[RelatorioDeLinhas, ResultadoDaCarga]:
        tabela = self.servicos.abrir_tabela(importacao)
        normalizador = self.servicos.criar_normalizador(importacao, tabela)
        politica = importacao.decisoes.repetidos_na_base or PoliticaDeRepetidos.MANTER_ATUAIS
        carga = self.servicos.carregador.carregar(
            importacao.id, registros_validos(tabela, normalizador), politica
        )
        return normalizador.relatorio, carga

    def _registrar_carga(
        self, importacao: Importacao, relatorio: RelatorioDeLinhas, carga: ResultadoDaCarga
    ) -> None:
        resultado: dict[str, Any] = {**resumir_relatorio(relatorio), **asdict(carga)}
        self.servicos.importacoes.salvar(
            replace(
                importacao,
                status=StatusDaImportacao.ATUALIZANDO_PAINEL,
                progresso=PROGRESSO_INICIAL_DAS_VIEWS,
                resultado=resultado,
                periodo_inicio=relatorio.primeira_data,
                periodo_fim=relatorio.ultima_data,
                data_do_retrato=importacao.decisoes.data_do_retrato or _hoje(self.servicos),
            )
        )

    def atualizar_painel(self, importacao_id: int) -> None:
        def registrar_avanco(progresso: int) -> None:
            self.servicos.importacoes.atualizar_progresso(
                importacao_id, StatusDaImportacao.ATUALIZANDO_PAINEL, progresso
            )

        self.servicos.atualizador.atualizar(registrar_avanco)
        importacao = self.servicos.obter(importacao_id)
        self.servicos.importacoes.salvar(
            replace(
                importacao,
                status=StatusDaImportacao.CONCLUIDA,
                progresso=100,
                concluida_em=self.servicos.relogio.agora(),
                arquivo_guardado=self._guardar_ou_apagar_arquivo(importacao),
            )
        )

    def _guardar_ou_apagar_arquivo(self, importacao: Importacao) -> bool:
        if importacao.estrutura.get("guardar_arquivo", False):
            return True
        self.servicos.armazenamento.remover(str(importacao.estrutura["referencia"]))
        return False

    def _registrar_falha(self, importacao: Importacao, erro: Exception) -> None:
        self.servicos.importacoes.salvar(
            replace(
                importacao,
                status=StatusDaImportacao.FALHOU,
                mensagem_de_erro=(
                    "A carga foi interrompida e nada foi gravado. "
                    f"Tente de novo. Detalhe técnico: {type(erro).__name__}."
                ),
            )
        )


def _hoje(servicos: ServicosDeImportacao) -> date:
    return servicos.relogio.agora().date()
