from dataclasses import dataclass
from datetime import date

SEGUNDOS_POR_DIA = 2.5
DIAS_SIMULADOS = 30
DIAS_DA_JANELA = 30
PEDIDOS_NA_FILA_DO_DIA = 12
CATEGORIAS_COM_MAIS_ATRASO = 7
MAIS_ENTRADAS_DO_DIA = 5
NOTA_MUITO_ALTA = 9


@dataclass(frozen=True)
class CalendarioDaWarRoom:
    hoje: date
    primeiro_dia: date
    ultimo_dia: date
    ultimo_registro_156: date | None
    ultimo_registro_ouvidoria: date | None
    segundos_por_dia: float
    dias_simulados: int


@dataclass(frozen=True)
class EntradasDoDia:
    entradas: int
    atendidos: int
    media_do_dia_da_semana: float
    camara: int
    ouvidoria: int
    defesa_civil: int


@dataclass(frozen=True)
class ContagemDeCategoria:
    categoria: str
    abertos: int
    atrasados: int


@dataclass(frozen=True)
class AtrasoDoBairro:
    bairro_oficial: str
    atrasados: int


@dataclass(frozen=True)
class EntradaPorCategoria:
    nome: str
    n: int


@dataclass(frozen=True)
class DiaDaSerie:
    data: date
    entradas: int
    atendidos: int


@dataclass(frozen=True)
class FilaDoDia:
    nota: float
    servico: str | None
    bairro_oficial: str | None
    idade_dias: int
    pedidos_anteriores: int | None


@dataclass(frozen=True)
class SemRespostaDaCamara:
    total: int
    mediana_de_dias: float | None
    tema_com_mais: str | None
    tema_quantidade: int


@dataclass(frozen=True)
class AlemDoPrazoDaOuvidoria:
    total: int
    mediana_de_dias: float | None
    orgao_com_mais: str | None
    orgao_quantidade: int


@dataclass(frozen=True)
class EstoqueDoDia:
    abertos: int
    atrasados: int
    classificaveis: int
    prioritarios: int
    com_nota_muito_alta: int
    camara: SemRespostaDaCamara
    ouvidoria: AlemDoPrazoDaOuvidoria
    entradas_nos_ultimos_30: int
    entradas_nos_30_anteriores: int
    fim_da_janela: date


@dataclass(frozen=True)
class QuadroDoDia:
    dia: date
    entradas: EntradasDoDia | None
    estoque: EstoqueDoDia
    atraso_por_bairro: list[AtrasoDoBairro]
    fila: list[FilaDoDia]
    serie: list[DiaDaSerie]
    categorias: list[ContagemDeCategoria]
    categorias_do_dia: list[EntradaPorCategoria]
    bairros_do_dia: list[EntradaPorCategoria]
