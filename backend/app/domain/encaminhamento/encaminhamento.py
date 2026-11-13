from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from app.domain.cidade import faixa_de_numeracao
from app.domain.contribuicao.contribuicao import tem_dado_pessoal
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import EncaminhamentoInvalido, TransicaoInvalida

# Prazo de resposta da Lei 13.460/2017, art. 16 (ADR 0011).
DIAS_PARA_O_ORGAO_RESPONDER = 30
VALIDADE_DO_LINK_DE_RETORNO = timedelta(days=60)
TAMANHO_MAXIMO_DA_OBSERVACAO = 280
TAMANHO_MAXIMO_DO_PROTOCOLO_DO_ORGAO = 40
DIGITOS_DO_CODIGO = 6
AVISO_DE_DADO_PESSOAL = "Retire CPF, telefone ou e-mail do texto."


class SituacaoDoEncaminhamento(StrEnum):
    ENVIADO = "enviado"
    FALHOU = "falhou"
    RECEBIDO = "recebido"
    RESOLVIDO = "resolvido"
    DEVOLVIDO = "devolvido"


class AutorDoEvento(StrEnum):
    GESTAO = "gestao"
    ORGAO = "orgao"
    SISTEMA = "sistema"


class CanalDeEnvio(StrEnum):
    LOCAL = "local"
    EMAIL = "email"
    WEBHOOK = "webhook"


SITUACOES_ABERTAS = frozenset({SituacaoDoEncaminhamento.ENVIADO, SituacaoDoEncaminhamento.RECEBIDO})
SITUACOES_DE_RETORNO = (
    SituacaoDoEncaminhamento.RECEBIDO,
    SituacaoDoEncaminhamento.RESOLVIDO,
    SituacaoDoEncaminhamento.DEVOLVIDO,
)
TRANSICOES_PERMITIDAS: dict[SituacaoDoEncaminhamento, frozenset[SituacaoDoEncaminhamento]] = {
    SituacaoDoEncaminhamento.ENVIADO: frozenset(SITUACOES_DE_RETORNO),
    SituacaoDoEncaminhamento.RECEBIDO: frozenset(
        {SituacaoDoEncaminhamento.RESOLVIDO, SituacaoDoEncaminhamento.DEVOLVIDO}
    ),
    SituacaoDoEncaminhamento.FALHOU: frozenset({SituacaoDoEncaminhamento.ENVIADO}),
    SituacaoDoEncaminhamento.RESOLVIDO: frozenset(),
    SituacaoDoEncaminhamento.DEVOLVIDO: frozenset(),
}


@dataclass(frozen=True)
class OcorrenciaEncaminhavel:
    """Cópia do registro no momento do envio: a importação pode substituir o original depois."""

    chave_registro: int
    fonte: str
    data_abertura: date | None = None
    categoria: str | None = None
    servico: str | None = None
    bairro_oficial: str | None = None
    rpa: str | None = None
    situacao: str | None = None
    orgao: str | None = None
    protocolo: str | None = None
    referencia_de_local: str | None = None


@dataclass(frozen=True)
class EventoDoEncaminhamento:
    situacao: SituacaoDoEncaminhamento
    autor: AutorDoEvento
    ocorrido_em: datetime
    observacao: str | None = None
    protocolo_do_orgao: str | None = None


@dataclass(frozen=True)
class Encaminhamento:
    id: int
    ocorrencia: OcorrenciaEncaminhavel
    orgao: Orgao
    orgao_sugerido: Orgao | None
    canal: CanalDeEnvio
    situacao: SituacaoDoEncaminhamento
    criado_em: datetime
    prazo_de_resposta: date
    atualizado_em: datetime
    nota: float | None = None
    justificativa: str | None = None
    automatico: bool = False
    protocolo_do_orgao: str | None = None
    eventos: tuple[EventoDoEncaminhamento, ...] = ()
    contribuicao_id: UUID | None = None
    lembrete_enviado_em: datetime | None = None

    @property
    def codigo(self) -> str:
        return f"ENC-{self.criado_em.year}-{self.id:0{DIGITOS_DO_CODIGO}d}"

    @property
    def esta_aberto(self) -> bool:
        return self.situacao in SITUACOES_ABERTAS

    def esta_atrasado(self, hoje: date) -> bool:
        return self.esta_aberto and hoje > self.prazo_de_resposta

    @property
    def ultima_observacao(self) -> str | None:
        return next((e.observacao for e in reversed(self.eventos) if e.observacao), None)


def calcular_prazo_de_resposta(enviado_em: date) -> date:
    return enviado_em + timedelta(days=DIAS_PARA_O_ORGAO_RESPONDER)


def exigir_transicao(atual: SituacaoDoEncaminhamento, nova: SituacaoDoEncaminhamento) -> None:
    if nova not in TRANSICOES_PERMITIDAS[atual]:
        raise TransicaoInvalida


def tem_encaminhamento_aberto(existentes: Sequence[Encaminhamento]) -> bool:
    return any(encaminhamento.esta_aberto for encaminhamento in existentes)


def limpar_texto_curto(campo: str, texto: str | None, tamanho_maximo: int) -> str | None:
    limpo = (texto or "").strip()
    if not limpo:
        return None
    if len(limpo) > tamanho_maximo:
        raise EncaminhamentoInvalido(campo, f"Use até {tamanho_maximo} caracteres.")
    if tem_dado_pessoal(limpo):
        raise EncaminhamentoInvalido(campo, AVISO_DE_DADO_PESSOAL)
    return limpo


def descrever_local_aproximado(via_reconhecida: str | None, numero: str | None) -> str | None:
    """Rua da lista oficial e faixa de numeração: o que outras contas de cidadão já veem."""
    if via_reconhecida is None:
        return None
    faixa = faixa_de_numeracao(numero)
    return f"{via_reconhecida}, {faixa}" if faixa else via_reconhecida
