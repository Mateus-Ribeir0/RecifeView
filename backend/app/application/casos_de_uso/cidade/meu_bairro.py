from dataclasses import dataclass

from app.application.portas.painel import TerritorioRepository, VisaoGeralRepository
from app.domain.catalogos import BairroDoCatalogo
from app.domain.erros import ValorDeFiltroInvalido
from app.domain.filtros import Filtros
from app.domain.territorio import calcular_taxa


@dataclass(frozen=True)
class Comparacao:
    bairro: float | None
    recife: float | None


@dataclass(frozen=True)
class IndicadoresDoBairro:
    """Números agregados dos dados abertos: o mesmo nível de detalhe da página pública."""

    bairro_oficial: str
    nome: str
    rpa: str
    populacao: int
    ano_inicio: int
    ano_fim: int
    pedidos_ao_156: int
    pedidos_por_mil_habitantes: Comparacao
    prazo_mediano: Comparacao
    prazo_p90: Comparacao
    pct_local_repetido: Comparacao


def _encontrar(bairros: list[BairroDoCatalogo], bairro_oficial: str) -> BairroDoCatalogo:
    bairro = next((item for item in bairros if item.bairro_oficial == bairro_oficial), None)
    if bairro is None:
        raise ValorDeFiltroInvalido
    return bairro


@dataclass(frozen=True)
class ConsultarMeuBairro:
    visao_geral: VisaoGeralRepository
    territorio: TerritorioRepository

    def executar(self, bairro_oficial: str) -> IndicadoresDoBairro:
        bairros = self.territorio.bairros()
        bairro = _encontrar(bairros, bairro_oficial)
        cidade, do_bairro = Filtros(), Filtros(bairros=(bairro_oficial,))
        prazo_bairro = self.visao_geral.percentis_de_prazo(do_bairro)
        prazo_cidade = self.visao_geral.percentis_de_prazo(cidade)
        volume, taxas = self._taxas(bairro, bairros)
        return IndicadoresDoBairro(
            bairro_oficial=bairro.bairro_oficial,
            nome=bairro.nome,
            rpa=bairro.rpa,
            populacao=bairro.populacao,
            ano_inicio=cidade.ano_inicio,
            ano_fim=cidade.ano_fim,
            pedidos_ao_156=volume,
            pedidos_por_mil_habitantes=taxas,
            prazo_mediano=Comparacao(prazo_bairro.mediana, prazo_cidade.mediana),
            prazo_p90=Comparacao(prazo_bairro.p90, prazo_cidade.p90),
            pct_local_repetido=Comparacao(
                self.visao_geral.pct_local_repetido(do_bairro),
                self.visao_geral.pct_local_repetido(cidade),
            ),
        )

    def _taxas(
        self, bairro: BairroDoCatalogo, bairros: list[BairroDoCatalogo]
    ) -> tuple[int, Comparacao]:
        """Bairro com menos de 1.000 moradores não tem taxa: ela distorce (docs/dados.md)."""
        volumes, anos = self.territorio.volumes_de_156(Filtros())
        por_bairro = {item.bairro_oficial: item.n for item in volumes}
        volume = por_bairro.get(bairro.bairro_oficial, 0)
        populacao_total = sum(item.populacao for item in bairros)
        taxa_do_bairro = (
            calcular_taxa(volume, anos, bairro.populacao) if bairro.taxa_confiavel else None
        )
        taxa_do_recife = calcular_taxa(sum(por_bairro.values()), anos, populacao_total)
        return volume, Comparacao(taxa_do_bairro, taxa_do_recife)
