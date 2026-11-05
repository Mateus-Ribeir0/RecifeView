from dataclasses import dataclass

from app.application.casos_de_uso.painel.comum import ResultadoDaConsulta
from app.application.portas.painel import ReferenciaRepository, TerritorioRepository
from app.domain.catalogos import BairroDoCatalogo
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.procedencia import Procedencia
from app.domain.suavizacao import Ponto, suavizar
from app.domain.territorio import (
    BairroDoTerritorio,
    FaixaDeTaxa,
    IndicadorDeTerritorio,
    Territorio,
    calcular_taxa,
    classe_da_taxa,
    limites_das_faixas,
)


def _indicador(
    volume: int, anos: int, populacao: int, confiavel: bool, faixas: list[FaixaDeTaxa]
) -> IndicadorDeTerritorio:
    taxa = calcular_taxa(volume, anos, populacao) if confiavel else None
    return IndicadorDeTerritorio(volume, taxa, classe_da_taxa(taxa, faixas))


def _taxas_validas(
    bairros: list[BairroDoCatalogo], volumes: dict[str, int], anos: int
) -> list[float]:
    return [
        calcular_taxa(volumes.get(bairro.bairro_oficial, 0), anos, bairro.populacao)
        for bairro in bairros
        if bairro.taxa_confiavel
    ]


def _tendencia(bairros: list[BairroDoCatalogo], volumes: dict[str, int], anos: int) -> list[Ponto]:
    pontos = [
        Ponto(
            bairro.pct_favela,
            calcular_taxa(volumes.get(bairro.bairro_oficial, 0), anos, bairro.populacao),
        )
        for bairro in bairros
        if bairro.taxa_confiavel
    ]
    return suavizar(pontos)


def _esta_em_destaque(bairro: BairroDoCatalogo, filtros: Filtros) -> bool:
    dentro_da_rpa = not filtros.rpas or bairro.rpa in filtros.rpas
    dentro_dos_bairros = not filtros.bairros or bairro.bairro_oficial in filtros.bairros
    return dentro_da_rpa and dentro_dos_bairros


@dataclass(frozen=True)
class ConsultarTerritorio:
    territorio: TerritorioRepository
    referencia: ReferenciaRepository

    def executar(self, filtros: Filtros) -> ResultadoDaConsulta[Territorio]:
        lista_156, anos_156 = self.territorio.volumes_de_156(filtros)
        lista_dc, anos_dc = self.territorio.volumes_da_defesa_civil(filtros)
        volumes_156 = {item.bairro_oficial: item.n for item in lista_156}
        volumes_dc = {item.bairro_oficial: item.n for item in lista_dc}
        bairros = self.territorio.bairros()
        faixas_156 = limites_das_faixas(_taxas_validas(bairros, volumes_156, anos_156))
        faixas_dc = limites_das_faixas(_taxas_validas(bairros, volumes_dc, anos_dc))
        indicadores = self.territorio.indicadores()
        dados = Territorio(
            bairros=[
                BairroDoTerritorio(
                    bairro_oficial=bairro.bairro_oficial,
                    nome=bairro.nome,
                    rpa=bairro.rpa,
                    populacao=bairro.populacao,
                    pct_favela=bairro.pct_favela,
                    taxa_confiavel=bairro.taxa_confiavel,
                    em_destaque=_esta_em_destaque(bairro, filtros),
                    central_156=_indicador(
                        volumes_156.get(bairro.bairro_oficial, 0),
                        anos_156,
                        bairro.populacao,
                        bairro.taxa_confiavel,
                        faixas_156,
                    ),
                    defesa_civil=_indicador(
                        volumes_dc.get(bairro.bairro_oficial, 0),
                        anos_dc,
                        bairro.populacao,
                        bairro.taxa_confiavel,
                        faixas_dc,
                    ),
                    pct_reincidencia_156=indicadores.get(bairro.bairro_oficial, (None, None, 0))[0],
                    pct_atraso_156=indicadores.get(bairro.bairro_oficial, (None, None, 0))[1],
                    abertos_156=indicadores.get(bairro.bairro_oficial, (None, None, None))[2],
                )
                for bairro in bairros
            ],
            faixas_156=faixas_156,
            faixas_defesa_civil=faixas_dc,
            tendencia_156=_tendencia(bairros, volumes_156, anos_156),
            tendencia_defesa_civil=_tendencia(bairros, volumes_dc, anos_dc),
            anos_156=anos_156,
            anos_defesa_civil=anos_dc,
        )
        n = sum(volumes_156.values()) + sum(volumes_dc.values())
        fontes = (Fonte.CENTRAL_156.value, Fonte.DEFESA_CIVIL.value)
        return ResultadoDaConsulta(
            dados, Procedencia(fontes, filtros, n, self.referencia.atual().atualizado_em)
        )
