from dataclasses import dataclass

from app.application.casos_de_uso.painel.comum import ResultadoDaConsulta
from app.application.portas.painel import PrazoRepository, ReferenciaRepository
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.prazos import Prazos, minimo_de_pedidos_por_categoria
from app.domain.procedencia import Procedencia


@dataclass(frozen=True)
class ConsultarPrazos:
    prazos: PrazoRepository
    referencia: ReferenciaRepository

    def executar(self, filtros: Filtros, sem_mesmo_dia: bool) -> ResultadoDaConsulta[Prazos]:
        resumo = self.prazos.resumo(filtros, sem_mesmo_dia)
        minimo = minimo_de_pedidos_por_categoria(resumo.pedidos)
        categorias = [
            item
            for item in self.prazos.por_categoria(filtros, sem_mesmo_dia)
            if item.pedidos >= minimo
        ]
        dados = Prazos(
            resumo=resumo,
            por_ano=self.prazos.por_ano(filtros, sem_mesmo_dia),
            faixas=self.prazos.faixas(filtros, sem_mesmo_dia),
            minimo_por_categoria=minimo,
            por_categoria=sorted(categorias, key=lambda item: item.p90, reverse=True),
            estoque=self.prazos.estoque(filtros),
        )
        meta = Procedencia(
            (Fonte.CENTRAL_156.value,),
            filtros,
            resumo.pedidos,
            self.referencia.atual().atualizado_em,
        )
        return ResultadoDaConsulta(dados, meta)
