from datetime import date, datetime

from app.api.schemas.painel import Esquema


class CalendarioResposta(Esquema):
    hoje: date
    primeiro_dia: date
    ultimo_dia: date
    ultimo_registro_156: date | None
    ultimo_registro_ouvidoria: date | None
    segundos_por_dia: float
    dias_simulados: int


class EntradasDoDiaResposta(Esquema):
    entradas: int
    atendidos: int
    media_do_dia_da_semana: float
    camara: int
    ouvidoria: int
    defesa_civil: int


class SemRespostaDaCamaraResposta(Esquema):
    total: int
    mediana_de_dias: float | None
    tema_com_mais: str | None
    tema_quantidade: int


class AlemDoPrazoDaOuvidoriaResposta(Esquema):
    total: int
    mediana_de_dias: float | None
    orgao_com_mais: str | None
    orgao_quantidade: int


class EstoqueDoDiaResposta(Esquema):
    abertos: int
    atrasados: int
    classificaveis: int
    prioritarios: int
    com_nota_muito_alta: int
    camara: SemRespostaDaCamaraResposta
    ouvidoria: AlemDoPrazoDaOuvidoriaResposta
    entradas_nos_ultimos_30: int
    entradas_nos_30_anteriores: int
    fim_da_janela: date


class AtrasoDoBairroResposta(Esquema):
    bairro_oficial: str
    atrasados: int


class FilaDoDiaResposta(Esquema):
    nota: float
    servico: str | None
    bairro_oficial: str | None
    idade_dias: int
    pedidos_anteriores: int | None


class DiaDaSerieResposta(Esquema):
    data: date
    entradas: int
    atendidos: int


class ContagemDeCategoriaResposta(Esquema):
    categoria: str
    abertos: int
    atrasados: int


class EntradaPorCategoriaResposta(Esquema):
    nome: str
    n: int


class QuadroDoDiaResposta(Esquema):
    dia: date
    entradas: EntradasDoDiaResposta | None
    estoque: EstoqueDoDiaResposta
    atraso_por_bairro: list[AtrasoDoBairroResposta]
    fila: list[FilaDoDiaResposta]
    serie: list[DiaDaSerieResposta]
    categorias: list[ContagemDeCategoriaResposta]
    categorias_do_dia: list[EntradaPorCategoriaResposta]
    bairros_do_dia: list[EntradaPorCategoriaResposta]


class CoberturaPorFonteResposta(Esquema):
    fonte: str
    ano: int
    n: int


class CorrecaoAplicadaResposta(Esquema):
    correcao: str
    registros: int


class SobreOsDadosResposta(Esquema):
    cobertura: list[CoberturaPorFonteResposta]
    correcoes: list[CorrecaoAplicadaResposta]
    registros_na_base: int
    atualizado_em: datetime | None
