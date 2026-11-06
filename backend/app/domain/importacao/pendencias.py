from collections import Counter
from dataclasses import dataclass, field
from difflib import get_close_matches
from enum import StrEnum

from app.domain.importacao.campos import CAMPOS_POR_NOME
from app.domain.importacao.decisoes import Decisoes

VALORES_MOSTRADOS = 200
SEMELHANCA_DA_SUGESTAO = 0.72


class TipoDePendencia(StrEnum):
    FONTE = "fonte"
    DATA_DO_RETRATO = "data_do_retrato"
    CAMPO_OBRIGATORIO = "campo_obrigatorio"
    FORMATO_DE_DATA = "formato_de_data"
    BAIRRO_DESCONHECIDO = "bairro_desconhecido"
    VALOR_NOVO = "valor_novo"
    DATAS_INVALIDAS = "datas_invalidas"
    REPETIDOS_NA_BASE = "repetidos_na_base"
    REPETIDOS_NO_ARQUIVO = "repetidos_no_arquivo"
    COINCIDENCIAS_CERTAS = "coincidencias_certas"
    COINCIDENCIAS_PROVAVEIS = "coincidencias_provaveis"


@dataclass(frozen=True)
class ValorEmDuvida:
    valor: str
    quantidade: int
    sugestao: str | None = None


@dataclass(frozen=True)
class Pendencia:
    tipo: TipoDePendencia
    campo: str | None = None
    rotulo_do_campo: str | None = None
    quantidade: int = 0
    valores: tuple[ValorEmDuvida, ...] = ()
    alternativas: tuple[str, ...] = ()
    total_de_valores: int = 0
    detalhes: dict[str, int] = field(default_factory=dict)


def valores_ainda_sem_resposta(
    campo: str, valores: Counter[str], decisoes: Decisoes
) -> Counter[str]:
    if campo in decisoes.padrao_para_valores:
        return Counter()
    respondidos = decisoes.substituicoes.get(campo, {})
    return Counter({valor: n for valor, n in valores.items() if valor not in respondidos})


def _melhor_sugestao(valor: str, conhecidos: list[str]) -> str | None:
    parecidos = get_close_matches(valor, conhecidos, n=1, cutoff=SEMELHANCA_DA_SUGESTAO)
    return parecidos[0] if parecidos else None


def montar_pendencia_de_valores(
    tipo: TipoDePendencia, campo: str, valores: Counter[str], conhecidos: list[str]
) -> Pendencia:
    mais_comuns = valores.most_common(VALORES_MOSTRADOS)
    return Pendencia(
        tipo=tipo,
        campo=campo,
        rotulo_do_campo=CAMPOS_POR_NOME[campo].rotulo,
        quantidade=sum(valores.values()),
        valores=tuple(
            ValorEmDuvida(valor, quantidade, _melhor_sugestao(valor, conhecidos))
            for valor, quantidade in mais_comuns
        ),
        alternativas=tuple(sorted(conhecidos)),
        total_de_valores=len(valores),
    )
