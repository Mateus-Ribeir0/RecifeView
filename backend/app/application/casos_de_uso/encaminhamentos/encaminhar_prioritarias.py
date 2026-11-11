from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum

from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
    PrepararEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.casos_de_uso.painel.prioridade import ClassificarFila, PedidoDeFila
from app.application.portas.painel import PrioridadeRepository
from app.domain.ahp import JULGAMENTOS_PADRAO
from app.domain.encaminhamento.encaminhamento import Encaminhamento, SituacaoDoEncaminhamento
from app.domain.filtros import Filtros
from app.domain.prioridade import NOTA_ALTA, FonteDaFila

LIMITE_PADRAO_POR_EXECUCAO = 20
SEMENTE_SEM_SORTEIO = 0


class MotivoParaPular(StrEnum):
    JA_ENCAMINHADA = "ja_encaminhada"
    SEM_SUGESTAO = "sem_sugestao"


@dataclass(frozen=True)
class PedidoAutomatico:
    fonte: FonteDaFila
    nota_minima: float = NOTA_ALTA
    limite: int = LIMITE_PADRAO_POR_EXECUCAO


@dataclass(frozen=True)
class CandidataAoEnvio:
    chave_registro: int
    nota: float


@dataclass(frozen=True)
class ResultadoDoEnvioAutomatico:
    candidatas: int = 0
    puladas: Counter[MotivoParaPular] = field(default_factory=Counter)
    encaminhadas: list[Encaminhamento] = field(default_factory=list)

    @property
    def falhas(self) -> int:
        return sum(
            1 for item in self.encaminhadas if item.situacao is SituacaoDoEncaminhamento.FALHOU
        )


@dataclass(frozen=True)
class EncaminharPrioritarias:
    """Para o agendador: segue a fila pela nota e usa a sugestão de destino, sem perguntar."""

    servicos: ServicosDeEncaminhamento
    prioridade: PrioridadeRepository

    def executar(self, pedido: PedidoAutomatico) -> ResultadoDoEnvioAutomatico:
        candidatas = self._candidatas(pedido)
        resultado = ResultadoDoEnvioAutomatico(len(candidatas))
        for candidata in candidatas:
            if len(resultado.encaminhadas) >= pedido.limite:
                break
            tentativa = self._encaminhar_se_possivel(candidata)
            if isinstance(tentativa, MotivoParaPular):
                resultado.puladas[tentativa] += 1
            else:
                resultado.encaminhadas.append(tentativa)
        return resultado

    def _candidatas(self, pedido: PedidoAutomatico) -> list[CandidataAoEnvio]:
        fila = ClassificarFila(self.prioridade).classificar(
            PedidoDeFila(pedido.fonte, JULGAMENTOS_PADRAO, SEMENTE_SEM_SORTEIO, Filtros())
        )
        return [
            CandidataAoEnvio(item.ocorrencia.chave_registro, item.indice)
            for item in fila
            if item.indice >= pedido.nota_minima and item.ocorrencia.chave_registro is not None
        ]

    def _encaminhar_se_possivel(
        self, candidata: CandidataAoEnvio
    ) -> Encaminhamento | MotivoParaPular:
        preparo = PrepararEncaminhamento(self.servicos).executar(candidata.chave_registro)
        if not preparo.pode_encaminhar:
            return MotivoParaPular.JA_ENCAMINHADA
        if preparo.sugestao.orgao is None:
            return MotivoParaPular.SEM_SUGESTAO
        pedido = PedidoDeEncaminhamento(
            candidata.chave_registro, preparo.sugestao.orgao, nota=candidata.nota, automatico=True
        )
        return EncaminharOcorrencia(self.servicos).executar(pedido)
