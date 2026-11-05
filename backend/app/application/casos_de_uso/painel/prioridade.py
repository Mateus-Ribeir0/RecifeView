from dataclasses import dataclass

from app.application.portas.painel import PrioridadeRepository
from app.domain.ahp import (
    RC_ACEITAVEL,
    calcular_pesos,
    indice_de_prioridade,
    matriz_de_comparacao,
    medir_sensibilidade,
    razao_de_consistencia,
)
from app.domain.filtros import Filtros
from app.domain.prioridade import (
    NOTA_ALTA,
    TAMANHO_DA_FILA_MOSTRADA,
    FilaClassificada,
    FonteDaFila,
    Ocorrencia,
    OcorrenciaClassificada,
    Prioridade,
    classificar_ocorrencias,
    classificar_so_pelo_atraso,
    distribuir_notas,
    sortear_amostra,
)


@dataclass(frozen=True)
class CalcularPrioridade:
    prioridade: PrioridadeRepository

    def executar(self, julgamentos: dict[tuple[str, str], float]) -> Prioridade:
        pesos = calcular_pesos(julgamentos)
        indicadores = self.prioridade.indicadores_dos_bairros()
        razao = razao_de_consistencia(matriz_de_comparacao(julgamentos))
        return Prioridade(
            pesos=pesos,
            razao_de_consistencia=razao,
            coerente=razao <= RC_ACEITAVEL,
            bairros=indice_de_prioridade(indicadores, pesos),
            sensibilidade=medir_sensibilidade(indicadores, pesos),
        )


@dataclass(frozen=True)
class PedidoDeFila:
    fonte: FonteDaFila
    julgamentos: dict[tuple[str, str], float]
    semente: int
    filtros: Filtros


@dataclass(frozen=True)
class ClassificarFila:
    prioridade: PrioridadeRepository

    def executar(self, pedido: PedidoDeFila) -> FilaClassificada:
        ocorrencias = self._ocorrencias(pedido)
        fila = self._classificar(pedido, ocorrencias)
        alta = sum(1 for item in fila if item.indice >= NOTA_ALTA)
        return FilaClassificada(
            fonte=pedido.fonte,
            registros_na_base=self.prioridade.registros_na_base(pedido.fonte),
            em_aberto=len(ocorrencias),
            classificados=len(fila),
            com_nota_alta=alta,
            pct_nota_alta=alta / len(fila) * 100 if fila else None,
            amostra=sortear_amostra(fila, pedido.semente),
            topo=fila[:TAMANHO_DA_FILA_MOSTRADA],
            distribuicao=distribuir_notas(fila),
        )

    def _ocorrencias(self, pedido: PedidoDeFila) -> list[Ocorrencia]:
        if pedido.fonte is FonteDaFila.OUVIDORIA:
            return self.prioridade.ocorrencias_da_ouvidoria()
        if pedido.fonte is FonteDaFila.CAMARA:
            return self.prioridade.ocorrencias_da_camara(pedido.filtros)
        return self.prioridade.ocorrencias_156(pedido.filtros)

    def _classificar(
        self, pedido: PedidoDeFila, ocorrencias: list[Ocorrencia]
    ) -> list[OcorrenciaClassificada]:
        if pedido.fonte is FonteDaFila.OUVIDORIA:
            return classificar_so_pelo_atraso(ocorrencias)
        indicadores = self.prioridade.indicadores_dos_bairros()
        return classificar_ocorrencias(ocorrencias, indicadores, calcular_pesos(pedido.julgamentos))
