from dataclasses import dataclass, field, replace
from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.domain.erros import ImportacaoEmEstadoInvalido
from app.domain.importacao.decisoes import Decisoes


class StatusDaImportacao(StrEnum):
    ANALISANDO = "ANALISANDO"
    AGUARDANDO_COLUNAS = "AGUARDANDO_COLUNAS"
    VALIDANDO = "VALIDANDO"
    AGUARDANDO_DECISOES = "AGUARDANDO_DECISOES"
    PRONTA = "PRONTA"
    CARREGANDO = "CARREGANDO"
    ATUALIZANDO_PAINEL = "ATUALIZANDO_PAINEL"
    CONCLUIDA = "CONCLUIDA"
    FALHOU = "FALHOU"
    CANCELADA = "CANCELADA"
    DESFAZENDO = "DESFAZENDO"
    DESFEITA = "DESFEITA"


STATUS_EDITAVEIS = frozenset(
    {
        StatusDaImportacao.AGUARDANDO_COLUNAS,
        StatusDaImportacao.AGUARDANDO_DECISOES,
        StatusDaImportacao.PRONTA,
    }
)
STATUS_CANCELAVEIS = STATUS_EDITAVEIS | {StatusDaImportacao.FALHOU}


@dataclass(frozen=True)
class Importacao:
    id: int
    nome_do_arquivo: str
    tamanho_em_bytes: int
    hash_do_arquivo: str
    usuario_id: UUID | None
    status: StatusDaImportacao
    criada_em: datetime
    progresso: int = 0
    fonte: str | None = None
    layout: str | None = None
    data_do_retrato: date | None = None
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    carga_inicial: bool = False
    arquivo_guardado: bool = True
    estrutura: dict[str, Any] = field(default_factory=dict)
    decisoes: Decisoes = field(default_factory=Decisoes)
    pendencias: dict[str, Any] = field(default_factory=dict)
    resultado: dict[str, Any] = field(default_factory=dict)
    mensagem_de_erro: str | None = None
    concluida_em: datetime | None = None
    desfeita_em: datetime | None = None
    nome_de_quem_importou: str | None = None

    def exigir_edicao_aberta(self) -> None:
        if self.status not in STATUS_EDITAVEIS:
            raise ImportacaoEmEstadoInvalido

    def exigir_que_esteja_pronta(self) -> None:
        if self.status is not StatusDaImportacao.PRONTA:
            raise ImportacaoEmEstadoInvalido

    def exigir_que_possa_ser_cancelada(self) -> None:
        if self.status not in STATUS_CANCELAVEIS:
            raise ImportacaoEmEstadoInvalido

    def com_status(self, status: StatusDaImportacao, progresso: int = 0) -> "Importacao":
        return replace(self, status=status, progresso=progresso)
