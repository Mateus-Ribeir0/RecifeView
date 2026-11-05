"""Índice de prioridade com AHP (Analytic Hierarchy Process, Saaty).

Quem decide compara os critérios dois a dois; o autovetor principal da matriz dá os pesos e a razão
de consistência diz se os julgamentos são coerentes. Os julgamentos padrão são uma proposta do grupo
para discussão, não validada pela Prefeitura.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from math import log1p

ITERACOES_DO_AUTOVETOR = 200
RC_ACEITAVEL = 0.10
NOTA_MAXIMA = 10
ATRASO_TETO = 2.0
REINCIDENCIA_TETO = 10
TOP_DA_SENSIBILIDADE = 10
FATORES_DE_SENSIBILIDADE = (0.5, 0.75, 1.25, 1.5)
INDICE_ALEATORIO = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}


@dataclass(frozen=True)
class Criterio:
    chave: str
    nome: str
    unidade: str
    descricao: str


CRITERIOS = (
    Criterio(
        "risco",
        "Risco",
        "ações / mil hab. / ano",
        "Demanda do cidadão à Defesa Civil (vistoria, lona) por habitante, 2021 a 2024. "
        "Mede exposição a risco em encostas e áreas alagáveis.",
    ),
    Criterio(
        "vulnerabilidade",
        "Vulnerabilidade",
        "% da população",
        "Parcela da população do bairro em favelas e comunidades urbanas (Censo 2022). O mesmo "
        "problema pesa mais onde a capacidade de se recuperar é menor, e o volume de pedidos "
        "não mostra isso.",
    ),
    Criterio(
        "atraso",
        "Atraso",
        "% do estoque aberto",
        "Parcela dos pedidos do 156 ainda abertos (dois arquivos mais recentes) que já passaram "
        "do prazo típico da categoria (p90 dos atendidos de 2021 a 2025).",
    ),
    Criterio(
        "reincidencia",
        "Reincidência",
        "% dos pedidos",
        "Parcela dos pedidos do 156 (2021 a 2025, com número no endereço) que caem num local e "
        "serviço que se repete. O problema que volta pesa mais que o problema novo.",
    ),
)
CHAVES = tuple(criterio.chave for criterio in CRITERIOS)

# Valor acima de 1: o primeiro critério do par pesa mais; abaixo de 1, o segundo.
JULGAMENTOS_PADRAO = {
    ("risco", "vulnerabilidade"): 2.0,
    ("risco", "atraso"): 3.0,
    ("risco", "reincidencia"): 3.0,
    ("vulnerabilidade", "atraso"): 2.0,
    ("vulnerabilidade", "reincidencia"): 2.0,
    ("atraso", "reincidencia"): 1.0,
}

type Matriz = list[list[float]]
type Pesos = dict[str, float]


def pares(chaves: Sequence[str] = CHAVES) -> list[tuple[str, str]]:
    return list(combinations(chaves, 2))


def matriz_de_comparacao(
    julgamentos: dict[tuple[str, str], float], chaves: Sequence[str] = CHAVES
) -> Matriz:
    posicao = {chave: indice for indice, chave in enumerate(chaves)}
    matriz = [[1.0] * len(chaves) for _ in chaves]
    for (primeiro, segundo), valor in julgamentos.items():
        matriz[posicao[primeiro]][posicao[segundo]] = valor
        matriz[posicao[segundo]][posicao[primeiro]] = 1 / valor
    return matriz


def _multiplicar(matriz: Matriz, vetor: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(linha, vetor, strict=True)) for linha in matriz]


def pesos_da_matriz(matriz: Matriz) -> list[float]:
    vetor = [1 / len(matriz)] * len(matriz)
    for _ in range(ITERACOES_DO_AUTOVETOR):
        produto = _multiplicar(matriz, vetor)
        soma = sum(produto)
        vetor = [valor / soma for valor in produto]
    return vetor


def razao_de_consistencia(matriz: Matriz) -> float:
    tamanho = len(matriz)
    if tamanho <= 2:
        return 0.0
    vetor = pesos_da_matriz(matriz)
    produto = _multiplicar(matriz, vetor)
    autovalor = sum(p / v for p, v in zip(produto, vetor, strict=True)) / tamanho
    indice_de_consistencia = (autovalor - tamanho) / (tamanho - 1)
    return max(indice_de_consistencia / INDICE_ALEATORIO[tamanho], 0.0)


def calcular_pesos(julgamentos: dict[tuple[str, str], float]) -> Pesos:
    pesos = pesos_da_matriz(matriz_de_comparacao(julgamentos))
    return dict(zip(CHAVES, pesos, strict=True))


def posicoes_relativas(valores: Sequence[float | None]) -> list[float]:
    """Posição de cada valor entre os demais, de 0 a 1. Sem dado recebe 0.

    Usar a posição, e não o valor bruto, evita que poucos bairros extremos achatem os outros:
    a Defesa Civil vai de 0,1 a 119 ações por mil habitantes.
    """
    presentes = sorted(valor for valor in valores if valor is not None)
    if not presentes:
        return [0.0] * len(valores)
    posicoes: dict[float, float] = {}
    inicio = 0
    while inicio < len(presentes):
        fim = inicio
        while fim + 1 < len(presentes) and presentes[fim + 1] == presentes[inicio]:
            fim += 1
        posicoes[presentes[inicio]] = (inicio + fim + 2) / 2 / len(presentes)
        inicio = fim + 1
    return [0.0 if valor is None else posicoes[valor] for valor in valores]


@dataclass(frozen=True)
class IndicadoresDoBairro:
    bairro_oficial: str
    nome: str
    rpa: str
    risco: float | None
    vulnerabilidade: float | None
    atraso: float | None
    reincidencia: float | None


@dataclass(frozen=True)
class BairroPriorizado:
    indicadores: IndicadoresDoBairro
    indice: float
    posicao: int
    contribuicoes: dict[str, float]


def notas_dos_bairros(indicadores: Sequence[IndicadoresDoBairro]) -> dict[str, dict[str, float]]:
    colunas = {
        chave: posicoes_relativas([getattr(item, chave) for item in indicadores])
        for chave in CHAVES
    }
    return {
        item.bairro_oficial: {chave: colunas[chave][indice] for chave in CHAVES}
        for indice, item in enumerate(indicadores)
    }


def indice_de_prioridade(
    indicadores: Sequence[IndicadoresDoBairro], pesos: Pesos
) -> list[BairroPriorizado]:
    notas = notas_dos_bairros(indicadores)
    pontuados = []
    for item in indicadores:
        contribuicoes = {
            chave: notas[item.bairro_oficial][chave] * pesos[chave] * NOTA_MAXIMA
            for chave in CHAVES
        }
        pontuados.append((item, sum(contribuicoes.values()), contribuicoes))
    ordenados = sorted(pontuados, key=lambda linha: linha[1], reverse=True)
    resultado: list[BairroPriorizado] = []
    for ordem, (item, indice, contribuicoes) in enumerate(ordenados, start=1):
        anterior = resultado[-1] if resultado else None
        empatou = anterior is not None and anterior.indice == indice
        posicao = anterior.posicao if anterior is not None and empatou else ordem
        resultado.append(BairroPriorizado(item, indice, posicao, contribuicoes))
    return resultado


@dataclass(frozen=True)
class TesteDeSensibilidade:
    criterio: str
    fator: float
    peso_testado: float
    mantidos_no_top: int


def _pesos_com_fator(pesos: Pesos, chave: str, fator: float) -> Pesos:
    alterados = {**pesos, chave: pesos[chave] * fator}
    soma = sum(alterados.values())
    return {nome: valor / soma for nome, valor in alterados.items()}


def _top(indicadores: Sequence[IndicadoresDoBairro], pesos: Pesos) -> set[str]:
    ordenados = indice_de_prioridade(indicadores, pesos)[:TOP_DA_SENSIBILIDADE]
    return {item.indicadores.bairro_oficial for item in ordenados}


def medir_sensibilidade(
    indicadores: Sequence[IndicadoresDoBairro], pesos: Pesos
) -> list[TesteDeSensibilidade]:
    base = _top(indicadores, pesos)
    testes = []
    for criterio in CRITERIOS:
        for fator in FATORES_DE_SENSIBILIDADE:
            novos = _pesos_com_fator(pesos, criterio.chave, fator)
            mantidos = len(base & _top(indicadores, novos))
            testes.append(
                TesteDeSensibilidade(criterio.nome, fator, novos[criterio.chave], mantidos)
            )
    return testes


def nota_de_atraso(idade_dias: float, prazo_tipico_dias: float | None) -> float:
    """0,5 quando chega ao prazo típico; 1 no dobro do prazo ou mais. Sem prazo típico: 0."""
    if prazo_tipico_dias is None or (prazo_tipico_dias == 0 and idade_dias == 0):
        return 0.0
    if prazo_tipico_dias == 0:
        return 1.0
    return min(max(idade_dias / prazo_tipico_dias, 0.0), ATRASO_TETO) / ATRASO_TETO


def nota_de_reincidencia(pedidos_anteriores: int | None) -> float:
    """Escala log: 1 anterior vale cerca de 0,29; 10 ou mais vale 1. Sem número no endereço: 0."""
    if pedidos_anteriores is None:
        return 0.0
    return min(log1p(pedidos_anteriores) / log1p(REINCIDENCIA_TETO), 1.0)
