from dataclasses import dataclass, replace

from app.application.casos_de_uso.painel.comum import ResultadoDaConsulta
from app.application.portas.painel import (
    ReferenciaRepository,
    RetornoRepository,
    VisaoGeralRepository,
)
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.procedencia import Procedencia
from app.domain.retorno import CanaisDaOuvidoria, RetornoDasIndicacoes


@dataclass(frozen=True)
class ConsultarRetorno:
    indicadores: VisaoGeralRepository
    retorno: RetornoRepository
    referencia: ReferenciaRepository

    def executar(self, filtros: Filtros) -> ResultadoDaConsulta[RetornoDasIndicacoes]:
        resumo = self.indicadores.resumo_das_indicacoes(filtros)
        dispersoes = self.retorno.dispersoes(filtros)
        dados = RetornoDasIndicacoes(
            resumo=resumo,
            por_ano=self.retorno.resposta_por_ano(filtros),
            celulas=self.retorno.celulas_de_destino(filtros),
            orgaos=sorted({celula.orgao for celula in self.retorno.celulas_de_destino(filtros)}),
            dispersoes=dispersoes,
            caminhos=[
                self.retorno.caminho_da_categoria(filtros, dispersao.categoria)
                for dispersao in dispersoes
            ],
        )
        meta = Procedencia(
            (Fonte.CAMARA.value,), filtros, resumo.total, self.referencia.atual().atualizado_em
        )
        return ResultadoDaConsulta(dados, meta)


@dataclass(frozen=True)
class ConsultarCanaisDaOuvidoria:
    retorno: RetornoRepository
    referencia: ReferenciaRepository

    def executar(self, filtros: Filtros) -> ResultadoDaConsulta[CanaisDaOuvidoria]:
        canais = self.retorno.canais_da_ouvidoria(filtros)
        recorte_real = replace(filtros, rpas=(), bairros=(), categorias=())
        meta = Procedencia(
            (Fonte.OUVIDORIA.value,),
            recorte_real,
            canais.total,
            self.referencia.atual().atualizado_em,
        )
        return ResultadoDaConsulta(canais, meta)
