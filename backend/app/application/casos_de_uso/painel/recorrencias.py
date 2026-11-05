from dataclasses import dataclass

from app.application.casos_de_uso.painel.comum import ResultadoDaConsulta
from app.application.portas.painel import RecorrenciaRepository, ReferenciaRepository
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.procedencia import Procedencia
from app.domain.recorrencias import Recorrencias, minimo_de_pedidos_por_categoria


@dataclass(frozen=True)
class ConsultarRecorrencias:
    recorrencias: RecorrenciaRepository
    referencia: ReferenciaRepository

    def executar(self, filtros: Filtros, sem_generico: bool) -> ResultadoDaConsulta[Recorrencias]:
        pedidos, repetidos, intervalos = self.recorrencias.totais(filtros, sem_generico)
        minimo = minimo_de_pedidos_por_categoria(pedidos)
        por_categoria = [
            item
            for item in self.recorrencias.por_categoria(filtros, sem_generico)
            if item.pedidos >= minimo
        ]
        dados = Recorrencias(
            pedidos=pedidos,
            repetidos=repetidos,
            pct_repetidos=repetidos / pedidos * 100 if pedidos else None,
            intervalos=intervalos,
            pontos_cronicos=self.recorrencias.contar_pontos_cronicos(filtros),
            minimo_por_categoria=minimo,
            por_categoria=sorted(por_categoria, key=lambda i: i.pct_repetidos, reverse=True),
            lista_de_pontos=self.recorrencias.listar_pontos_cronicos(filtros),
        )
        meta = Procedencia(
            (Fonte.CENTRAL_156.value,), filtros, pedidos, self.referencia.atual().atualizado_em
        )
        return ResultadoDaConsulta(dados, meta)
