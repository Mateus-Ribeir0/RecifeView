from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date
from enum import StrEnum
from math import ceil
from random import Random

from app.domain.ahp import (
    CHAVES,
    NOTA_MAXIMA,
    BairroPriorizado,
    IndicadoresDoBairro,
    Pesos,
    TesteDeSensibilidade,
    nota_de_atraso,
    nota_de_reincidencia,
    notas_dos_bairros,
    posicoes_relativas,
)

NOTA_ALTA = 7
TAMANHO_DA_AMOSTRA = 3
TAMANHO_DA_FILA_MOSTRADA = 20
LARGURA_DA_FAIXA_DE_NOTA = 0.5
BAIRROS_NO_TOPO = 15


class FonteDaFila(StrEnum):
    CENTRAL_156 = "156"
    CAMARA = "camara"
    OUVIDORIA = "ouvidoria"


@dataclass(frozen=True)
class Ocorrencia:
    data_abertura: date | None
    idade_dias: int
    prazo_tipico_dias: float | None = None
    pedidos_anteriores: int | None = None
    bairro_oficial: str | None = None
    rpa: str | None = None
    categoria: str | None = None
    servico: str | None = None
    situacao: str | None = None
    orgao: str | None = None
    canal: str | None = None
    data_envio: date | None = None
    data_prazo: date | None = None
    natureza: str | None = None
    dias_alem_do_prazo: int | None = None


@dataclass(frozen=True)
class OcorrenciaClassificada:
    ocorrencia: Ocorrencia
    indice: float
    fila: int
    notas: dict[str, float | None]
    contribuicoes: dict[str, float]


@dataclass(frozen=True)
class FaixaDeNota:
    inicio: float
    fim: float
    registros: int


@dataclass(frozen=True)
class FilaClassificada:
    fonte: FonteDaFila
    registros_na_base: int
    em_aberto: int
    classificados: int
    com_nota_alta: int
    pct_nota_alta: float | None
    amostra: list[OcorrenciaClassificada]
    topo: list[OcorrenciaClassificada]
    distribuicao: list[FaixaDeNota]


@dataclass(frozen=True)
class Prioridade:
    pesos: Pesos
    razao_de_consistencia: float
    coerente: bool
    bairros: list[BairroPriorizado]
    sensibilidade: list[TesteDeSensibilidade]


def _classificar_com_notas(
    ocorrencia: Ocorrencia, notas: dict[str, float], pesos: Pesos
) -> OcorrenciaClassificada:
    contribuicoes = {chave: notas[chave] * pesos[chave] * NOTA_MAXIMA for chave in CHAVES}
    notas_em_escala: dict[str, float | None] = {
        chave: notas[chave] * NOTA_MAXIMA for chave in CHAVES
    }
    return OcorrenciaClassificada(
        ocorrencia, sum(contribuicoes.values()), 0, notas_em_escala, contribuicoes
    )


def classificar_ocorrencias(
    ocorrencias: Sequence[Ocorrencia], indicadores: Sequence[IndicadoresDoBairro], pesos: Pesos
) -> list[OcorrenciaClassificada]:
    """Risco e vulnerabilidade vêm do bairro; atraso e reincidência, do próprio registro.

    Registros de bairros fora do índice (menos de 1.000 moradores) ficam de fora.
    """
    lugar = notas_dos_bairros(indicadores)
    classificadas = []
    for ocorrencia in ocorrencias:
        notas_do_bairro = lugar.get(ocorrencia.bairro_oficial or "")
        if notas_do_bairro is None:
            continue
        notas = {
            "risco": notas_do_bairro["risco"],
            "vulnerabilidade": notas_do_bairro["vulnerabilidade"],
            "atraso": nota_de_atraso(ocorrencia.idade_dias, ocorrencia.prazo_tipico_dias),
            "reincidencia": nota_de_reincidencia(ocorrencia.pedidos_anteriores),
        }
        classificadas.append(_classificar_com_notas(ocorrencia, notas, pesos))
    return ordenar_fila(classificadas)


def classificar_so_pelo_atraso(ocorrencias: Sequence[Ocorrencia]) -> list[OcorrenciaClassificada]:
    """A Ouvidoria não tem lugar na base aberta: só o atraso pode ser medido.

    Todas as manifestações abertas já passaram do prazo legal, então a nota é a posição entre
    elas. Por isso ela não é comparável com a das outras fontes.
    """
    posicoes = posicoes_relativas([item.dias_alem_do_prazo for item in ocorrencias])
    classificadas = []
    for ocorrencia, posicao in zip(ocorrencias, posicoes, strict=True):
        nota = posicao * NOTA_MAXIMA
        notas: dict[str, float | None] = dict.fromkeys(CHAVES)
        notas["atraso"] = nota
        contribuicoes = dict.fromkeys(CHAVES, 0.0)
        contribuicoes["atraso"] = nota
        classificadas.append(OcorrenciaClassificada(ocorrencia, nota, 0, notas, contribuicoes))
    return ordenar_fila(classificadas)


def ordenar_fila(
    classificadas: Sequence[OcorrenciaClassificada],
) -> list[OcorrenciaClassificada]:
    ordenadas = sorted(classificadas, key=lambda item: item.indice, reverse=True)
    resultado: list[OcorrenciaClassificada] = []
    for ordem, item in enumerate(ordenadas, start=1):
        anterior = resultado[-1] if resultado else None
        empatou = anterior is not None and anterior.indice == item.indice
        fila = anterior.fila if anterior is not None and empatou else ordem
        resultado.append(replace(item, fila=fila))
    return resultado


def sortear_amostra(
    fila: Sequence[OcorrenciaClassificada], semente: int
) -> list[OcorrenciaClassificada]:
    tamanho = min(TAMANHO_DA_AMOSTRA, len(fila))
    sorteados = Random(semente).sample(list(fila), tamanho)  # noqa: S311
    return sorted(sorteados, key=lambda item: item.indice, reverse=True)


def distribuir_notas(fila: Sequence[OcorrenciaClassificada]) -> list[FaixaDeNota]:
    quantidade = int(NOTA_MAXIMA / LARGURA_DA_FAIXA_DE_NOTA)
    contagem = [0] * quantidade
    for item in fila:
        posicao = max(ceil(item.indice / LARGURA_DA_FAIXA_DE_NOTA) - 1, 0)
        contagem[min(posicao, quantidade - 1)] += 1
    return [
        FaixaDeNota(
            indice * LARGURA_DA_FAIXA_DE_NOTA, (indice + 1) * LARGURA_DA_FAIXA_DE_NOTA, registros
        )
        for indice, registros in enumerate(contagem)
    ]
