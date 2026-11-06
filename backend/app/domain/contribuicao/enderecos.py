import re
from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.contribuicao.semelhanca import semelhanca_de_texto
from app.domain.importacao.texto import normalizar_texto

SEMELHANCA_PARA_RECONHECER_A_VIA = 0.65
FOLGA_ENTRE_CANDIDATAS = 0.05
SEMELHANCA_MAXIMA_ENTRE_TIPOS_DIFERENTES = 0.6

# Grafia da coluna LOGRADOURO da Central 156: o `id_local` só coincide se o texto for igual.
TIPOS_DE_VIA = {
    "R": "RUA",
    "RUA": "RUA",
    "AV": "AV",
    "AVN": "AV",
    "AVENIDA": "AV",
    "TV": "TRV",
    "TR": "TRV",
    "TRV": "TRV",
    "TRAV": "TRV",
    "TRAVESSA": "TRV",
    "EST": "EST",
    "ESTR": "EST",
    "ESTRADA": "EST",
    "ROD": "ROD",
    "RODOVIA": "ROD",
    "PC": "PRC",
    "PCA": "PRC",
    "PRC": "PRC",
    "PRACA": "PRC",
    "PTE": "PTE",
    "PONTE": "PTE",
    "COR": "COR",
    "CGO": "COR",
    "CORREGO": "COR",
    "LGO": "LGO",
    "LARGO": "LGO",
    "VDO": "VDO",
    "VIADUTO": "VDO",
    "PRQ": "PRQ",
    "PARQUE": "PRQ",
    "LAD": "LAD",
    "LADEIRA": "LAD",
    "BEC": "BEC",
    "BECO": "BEC",
    "VIL": "VIL",
    "VILA": "VIL",
    "SIT": "SIT",
    "SITIO": "SIT",
    "SUB": "SUB",
    "SUBIDA": "SUB",
}
SUFIXOS_DE_VIA_NUMERADA = {"TRV": "TR", "SUB": "SB", "BEC": "BE"}
TIPOS_CANONICOS = frozenset(TIPOS_DE_VIA.values())
PALAVRAS_SEM_PESO = frozenset(
    {
        "DA",
        "DAS",
        "DE",
        "DO",
        "DOS",
        "E",
        "ALMIRANTE",
        "BARAO",
        "CAPITAO",
        "CONDE",
        "CORONEL",
        "DEPUTADO",
        "DOM",
        "DONA",
        "DOUTOR",
        "DR",
        "ENGENHEIRO",
        "GENERAL",
        "GOVERNADOR",
        "MAJOR",
        "MARECHAL",
        "PADRE",
        "PREFEITO",
        "PRESIDENTE",
        "PROFESSOR",
        "PROFESSORA",
        "SENADOR",
    }
)
# Nomes que muitas vias diferentes dividem. Nunca provam, sozinhos, que o local é o mesmo.
VIAS_GENERICAS = frozenset({"RUA PROJETADA", "RUA SEM NOME", "RUA NOVA", "RUA PRINCIPAL"})

VIA_NUMERADA = re.compile(r"^(\d+)(?:A|O)? (\w+)\b ?(.*)$")
VIA_JA_NUMERADA = re.compile(r"^\d+[A-Z]{2}$")
FORA_DE_LETRAS_E_NUMEROS = re.compile(r"[^A-Z0-9 ]+")
SEPARADORES = re.compile(r"[.,;:/\\ºª°-]+")


@dataclass(frozen=True)
class ViaSeparada:
    tipo: str
    nucleo: str


def _limpar(digitado: str) -> str:
    sem_separadores = SEPARADORES.sub(" ", digitado)
    return FORA_DE_LETRAS_E_NUMEROS.sub("", normalizar_texto(sem_separadores)).strip()


def _canonizar_via_numerada(texto: str) -> str | None:
    achado = VIA_NUMERADA.match(texto)
    if achado is None:
        return None
    ordem, tipo, resto = achado.groups()
    sufixo = SUFIXOS_DE_VIA_NUMERADA.get(TIPOS_DE_VIA.get(tipo, ""))
    return f"{ordem}{sufixo} {resto}".strip() if sufixo else None


def canonizar_logradouro(digitado: str) -> str:
    """Escreve a via como a Central 156 escreve: `R. do Hospício` vira `RUA DO HOSPICIO`."""
    texto = _limpar(digitado)
    numerada = _canonizar_via_numerada(texto)
    if numerada is not None:
        return numerada
    primeira, _, resto = texto.partition(" ")
    tipo = TIPOS_DE_VIA.get(primeira)
    return f"{tipo} {resto}".strip() if tipo else texto


def separar_via(canonico: str) -> ViaSeparada:
    primeira, _, resto = canonico.partition(" ")
    tem_tipo = primeira in TIPOS_CANONICOS or VIA_JA_NUMERADA.match(primeira) is not None
    tipo, nome = (primeira, resto) if tem_tipo else ("", canonico)
    palavras = [palavra for palavra in nome.split() if palavra not in PALAVRAS_SEM_PESO]
    return ViaSeparada(tipo, " ".join(palavras) or nome)


def semelhanca_de_via(primeira: str, segunda: str) -> float:
    """1ª Travessa e 2ª Travessa do mesmo nome são vias diferentes, por mais que pareçam."""
    via_a, via_b = separar_via(primeira), separar_via(segunda)
    semelhanca = semelhanca_de_texto(via_a.nucleo, via_b.nucleo)
    if via_a.tipo and via_b.tipo and via_a.tipo != via_b.tipo:
        return min(semelhanca, SEMELHANCA_MAXIMA_ENTRE_TIPOS_DIFERENTES)
    return semelhanca


def _vencedora_sem_empate(candidatas: list[tuple[float, str]]) -> str | None:
    ordenadas = sorted(candidatas, reverse=True)
    melhor_nota, melhor_via = ordenadas[0]
    if melhor_nota < SEMELHANCA_PARA_RECONHECER_A_VIA:
        return None
    empatou = len(ordenadas) > 1 and melhor_nota - ordenadas[1][0] < FOLGA_ENTRE_CANDIDATAS
    return None if empatou else melhor_via


def reconhecer_logradouro(digitado: str, conhecidos: Iterable[str]) -> str:
    """Troca o que foi digitado pela via conhecida do bairro, se houver uma só que combine."""
    canonico = canonizar_logradouro(digitado)
    vias = list(conhecidos)
    if canonico in vias or not vias:
        return canonico
    candidatas = [(semelhanca_de_via(canonico, via), via) for via in vias]
    return _vencedora_sem_empate(candidatas) or canonico
