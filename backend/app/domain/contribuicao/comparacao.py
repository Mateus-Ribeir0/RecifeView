from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from app.domain.contribuicao.enderecos import VIAS_GENERICAS, semelhanca_de_via
from app.domain.contribuicao.semelhanca import semelhanca_de_texto
from app.domain.importacao.pseudonimizacao import numero_foi_informado

# docs/dados.md: repetição em até 7 dias é duplicidade; em 30 dias ou mais é reincidência.
DIAS_DE_DUPLICIDADE = 7
DIAS_DE_REINCIDENCIA = 30

PESO_DO_LOCAL = 0.60
PESO_DO_SERVICO = 0.20
PESO_DO_TEMPO = 0.15
PESO_DO_DETALHE = 0.05
PONTUACAO_PARA_REVISAR = 0.72

NOTA_DO_MESMO_TEMA = 0.5
NOTA_DO_DETALHE_AUSENTE = 0.5
NOTA_DO_TEMPO_NO_MESMO_DIA = 1.0
NOTA_DO_TEMPO_DE_DUPLICIDADE = 0.8
NOTA_DO_TEMPO_INTERMEDIARIO = 0.4
DIFERENCA_DE_UM_DIA = 1

DESCONTO_DE_NUMEROS_PROXIMOS = 0.90
DESCONTO_SEM_NUMERO = 0.80
DESCONTO_DE_VIA_GENERICA = 0.60
DESCONTO_DE_NUMEROS_DISTANTES = 0.55
DISTANCIA_DE_NUMEROS_PROXIMOS = 30
VIA_QUASE_CERTA = 0.95
DETALHE_PARECIDO = 0.5


class ClasseDaComparacao(StrEnum):
    MESMA = "mesma"
    PROVAVEL = "provavel"
    DISTINTA = "distinta"


@dataclass(frozen=True)
class Relato:
    """O que dá para comparar entre dois registros, venham do formulário ou de um arquivo."""

    data: date
    bairro: str | None
    categoria: str | None
    servico_codigo: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    detalhe: str | None = None
    id_local: str | None = None
    numero_informado: bool = False


@dataclass(frozen=True)
class Comparacao:
    classe: ClasseDaComparacao
    pontuacao: float = 0.0
    motivos: tuple[str, ...] = ()


@dataclass(frozen=True)
class Local:
    nota: float
    exato: bool
    motivo: str


DISTINTA = Comparacao(ClasseDaComparacao.DISTINTA)
LOCAL_DESCONHECIDO = Local(0.0, exato=False, motivo="Endereço não comparável")


def _inteiro_do_numero(numero: str | None) -> int | None:
    digitos = "".join(caractere for caractere in numero or "" if caractere.isdigit())
    return int(digitos) if digitos else None


def _tem_numero(relato: Relato) -> bool:
    return relato.numero_informado or numero_foi_informado(relato.numero or "")


def _local_pelo_pseudonimo(a: Relato, b: Relato) -> Local | None:
    if not a.id_local or a.id_local != b.id_local:
        return None
    if _tem_numero(a) and _tem_numero(b):
        return Local(1.0, exato=True, motivo="Mesmo endereço")
    return Local(DESCONTO_SEM_NUMERO, exato=False, motivo="Mesma rua, sem número para confirmar")


def _local_pelos_numeros(a: Relato, b: Relato, via: float) -> Local:
    numero_a, numero_b = _inteiro_do_numero(a.numero), _inteiro_do_numero(b.numero)
    if numero_a is None or numero_b is None:
        return Local(via * DESCONTO_SEM_NUMERO, exato=False, motivo="Mesma rua, sem número")
    if numero_a == numero_b:
        return Local(via, exato=via >= 1.0, motivo="Mesmo endereço")
    if abs(numero_a - numero_b) <= DISTANCIA_DE_NUMEROS_PROXIMOS:
        return Local(via * DESCONTO_DE_NUMEROS_PROXIMOS, exato=False, motivo="Números próximos")
    return Local(via * DESCONTO_DE_NUMEROS_DISTANTES, exato=False, motivo="Números distantes")


def _local_pela_via(a: Relato, b: Relato) -> Local:
    if not a.logradouro or not b.logradouro:
        return LOCAL_DESCONHECIDO
    via = semelhanca_de_via(a.logradouro, b.logradouro)
    if a.logradouro in VIAS_GENERICAS and a.logradouro == b.logradouro:
        return Local(via * DESCONTO_DE_VIA_GENERICA, exato=False, motivo="Rua de nome genérico")
    local = _local_pelos_numeros(a, b, via)
    if via >= VIA_QUASE_CERTA:
        return local
    return Local(local.nota, exato=False, motivo=f"Rua parecida ({via:.0%}). {local.motivo}")


def _comparar_local(a: Relato, b: Relato) -> Local:
    return _local_pelo_pseudonimo(a, b) or _local_pela_via(a, b)


def _nota_do_tempo(dias: int) -> float:
    if dias <= DIFERENCA_DE_UM_DIA:
        return NOTA_DO_TEMPO_NO_MESMO_DIA
    if dias <= DIAS_DE_DUPLICIDADE:
        return NOTA_DO_TEMPO_DE_DUPLICIDADE
    return NOTA_DO_TEMPO_INTERMEDIARIO


def _nota_do_detalhe(a: Relato, b: Relato) -> float:
    if not a.detalhe or not b.detalhe:
        return NOTA_DO_DETALHE_AUSENTE
    return semelhanca_de_texto(a.detalhe.upper(), b.detalhe.upper())


def _descrever_tempo(dias: int) -> str:
    if dias == 0:
        return "Mesmo dia"
    return "1 dia de diferença" if dias == 1 else f"{dias} dias de diferença"


def _descrever(local: Local, mesmo_servico: bool, dias: int) -> tuple[str, ...]:
    servico = "Mesmo serviço" if mesmo_servico else "Mesmo tema, serviços diferentes"
    return (local.motivo, servico, _descrever_tempo(dias))


def comparar_relatos(a: Relato, b: Relato) -> Comparacao:
    """Vinculação de registros: a pontuação só vale dentro do mesmo bairro e do mesmo tema."""
    dias = abs((a.data - b.data).days)
    if dias >= DIAS_DE_REINCIDENCIA or not a.bairro or a.bairro != b.bairro:
        return DISTINTA
    if not a.categoria or a.categoria != b.categoria:
        return DISTINTA
    local = _comparar_local(a, b)
    mesmo_servico = bool(a.servico_codigo) and a.servico_codigo == b.servico_codigo
    pontuacao = (
        PESO_DO_LOCAL * local.nota
        + PESO_DO_SERVICO * (1.0 if mesmo_servico else NOTA_DO_MESMO_TEMA)
        + PESO_DO_TEMPO * _nota_do_tempo(dias)
        + PESO_DO_DETALHE * _nota_do_detalhe(a, b)
    )
    motivos = _descrever(local, mesmo_servico, dias)
    if local.exato and mesmo_servico and dias <= DIAS_DE_DUPLICIDADE:
        return Comparacao(ClasseDaComparacao.MESMA, round(pontuacao, 3), motivos)
    if pontuacao >= PONTUACAO_PARA_REVISAR:
        return Comparacao(ClasseDaComparacao.PROVAVEL, round(pontuacao, 3), motivos)
    return DISTINTA
