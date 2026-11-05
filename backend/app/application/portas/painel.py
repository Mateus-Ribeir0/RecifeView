from datetime import date
from typing import Protocol

from app.domain.ahp import IndicadoresDoBairro
from app.domain.auditoria import ConsultaAuditada
from app.domain.catalogos import BairroDoCatalogo, CatalogoDeFiltros
from app.domain.filtros import Filtros
from app.domain.prazos import (
    EstoqueAberto,
    FaixaDePrazo,
    PrazoPorAno,
    PrazoPorCategoria,
    ResumoDosPrazos,
)
from app.domain.prioridade import FonteDaFila, Ocorrencia
from app.domain.procedencia import Referencia
from app.domain.recorrencias import IntervalosDeRepeticao, PontoCronico, RecorrenciaPorCategoria
from app.domain.retorno import (
    CaminhoDaCategoria,
    CanaisDaOuvidoria,
    CelulaDeDestino,
    DispersaoDaCategoria,
    RespostaPorAno,
)
from app.domain.sobre import CoberturaPorFonte, CorrecaoAplicada
from app.domain.territorio import VolumeDoBairro
from app.domain.visao_geral import DemandaPorAno, PercentisDePrazo, ResumoDasIndicacoes
from app.domain.war_room import (
    AlemDoPrazoDaOuvidoria,
    CalendarioDaWarRoom,
    DiaDaSerie,
    EntradaPorCategoria,
    EntradasDoDia,
    SemRespostaDaCamara,
)


class CatalogoRepository(Protocol):
    def filtros(self) -> CatalogoDeFiltros: ...


class ReferenciaRepository(Protocol):
    def atual(self) -> Referencia: ...


class VisaoGeralRepository(Protocol):
    def demandas_por_ano(self, filtros: Filtros) -> list[DemandaPorAno]: ...

    def resumo_das_indicacoes(self, filtros: Filtros) -> ResumoDasIndicacoes: ...

    def pct_local_repetido(self, filtros: Filtros) -> float | None: ...

    def percentis_de_prazo(self, filtros: Filtros) -> PercentisDePrazo: ...


class RetornoRepository(Protocol):
    def resposta_por_ano(self, filtros: Filtros) -> list[RespostaPorAno]: ...

    def celulas_de_destino(self, filtros: Filtros) -> list[CelulaDeDestino]: ...

    def dispersoes(self, filtros: Filtros) -> list[DispersaoDaCategoria]: ...

    def caminho_da_categoria(self, filtros: Filtros, categoria: str) -> CaminhoDaCategoria: ...

    def canais_da_ouvidoria(self, filtros: Filtros) -> CanaisDaOuvidoria: ...


class RecorrenciaRepository(Protocol):
    def por_categoria(
        self, filtros: Filtros, sem_generico: bool
    ) -> list[RecorrenciaPorCategoria]: ...

    def totais(
        self, filtros: Filtros, sem_generico: bool
    ) -> tuple[int, int, IntervalosDeRepeticao]: ...

    def contar_pontos_cronicos(self, filtros: Filtros) -> int: ...

    def listar_pontos_cronicos(self, filtros: Filtros) -> list[PontoCronico]: ...


class PrazoRepository(Protocol):
    def resumo(self, filtros: Filtros, sem_mesmo_dia: bool) -> ResumoDosPrazos: ...

    def por_ano(self, filtros: Filtros, sem_mesmo_dia: bool) -> list[PrazoPorAno]: ...

    def faixas(self, filtros: Filtros, sem_mesmo_dia: bool) -> list[FaixaDePrazo]: ...

    def por_categoria(self, filtros: Filtros, sem_mesmo_dia: bool) -> list[PrazoPorCategoria]: ...

    def estoque(self, filtros: Filtros) -> EstoqueAberto: ...


class TerritorioRepository(Protocol):
    def volumes_de_156(self, filtros: Filtros) -> tuple[list[VolumeDoBairro], int]: ...

    def volumes_da_defesa_civil(self, filtros: Filtros) -> tuple[list[VolumeDoBairro], int]: ...

    def bairros(self) -> list[BairroDoCatalogo]: ...

    def indicadores(self) -> dict[str, tuple[float | None, float | None, int]]: ...


class PrioridadeRepository(Protocol):
    def indicadores_dos_bairros(self) -> list[IndicadoresDoBairro]: ...

    def ocorrencias_156(self, filtros: Filtros) -> list[Ocorrencia]: ...

    def ocorrencias_da_camara(self, filtros: Filtros) -> list[Ocorrencia]: ...

    def ocorrencias_da_ouvidoria(self) -> list[Ocorrencia]: ...

    def registros_na_base(self, fonte: FonteDaFila) -> int: ...


class WarRoomRepository(Protocol):
    def calendario(self) -> CalendarioDaWarRoom: ...

    def abertos_156(self, dia: date) -> list[Ocorrencia]: ...

    def entradas_do_dia(self, dia: date) -> EntradasDoDia | None: ...

    def serie(self, inicio: date, fim: date) -> list[DiaDaSerie]: ...

    def sem_resposta_da_camara(self, dia: date) -> SemRespostaDaCamara: ...

    def alem_do_prazo_da_ouvidoria(self, dia: date) -> AlemDoPrazoDaOuvidoria: ...

    def mais_entradas(self, dia: date, coluna: str) -> list[EntradaPorCategoria]: ...


class SobreRepository(Protocol):
    def cobertura(self) -> list[CoberturaPorFonte]: ...

    def correcoes(self) -> list[CorrecaoAplicada]: ...

    def registros_na_base(self) -> int: ...


class RegistroDeConsultas(Protocol):
    def registrar(self, consulta: ConsultaAuditada) -> None: ...
