from dataclasses import dataclass

from app.application.casos_de_uso.painel.comum import TODAS_AS_FONTES, ResultadoDaConsulta
from app.application.portas.painel import ReferenciaRepository, VisaoGeralRepository
from app.domain.filtros import Filtros
from app.domain.procedencia import Procedencia
from app.domain.visao_geral import VisaoGeral


@dataclass(frozen=True)
class ConsultarVisaoGeral:
    indicadores: VisaoGeralRepository
    referencia: ReferenciaRepository

    def executar(self, filtros: Filtros) -> ResultadoDaConsulta[VisaoGeral]:
        serie = self.indicadores.demandas_por_ano(filtros)
        demandas = sum(ponto.n for ponto in serie)
        visao = VisaoGeral(
            demandas=demandas,
            indicacoes=self.indicadores.resumo_das_indicacoes(filtros),
            pct_local_repetido=self.indicadores.pct_local_repetido(filtros),
            prazo=self.indicadores.percentis_de_prazo(filtros),
            serie=serie,
        )
        meta = Procedencia(
            TODAS_AS_FONTES, filtros, demandas, self.referencia.atual().atualizado_em
        )
        return ResultadoDaConsulta(visao, meta)
