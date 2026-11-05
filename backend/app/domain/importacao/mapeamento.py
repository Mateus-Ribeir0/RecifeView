from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import StrEnum

from app.domain.importacao.campos import CAMPOS, CAMPOS_OBRIGATORIOS
from app.domain.importacao.layouts import (
    ENDERECO,
    NUMERO,
    SEM_USO,
    TEXTO_LIVRE,
    CodigoDoLayout,
    Layout,
)
from app.domain.importacao.privacidade import ColunaBloqueada, MotivoDeBloqueio
from app.domain.importacao.texto import normalizar_nome_de_coluna

SEMELHANCA_MINIMA = 0.82
COLUNAS_DE_ENDERECO = ("LOGRADOURO", "ENDERECO")


class OrigemDaSugestao(StrEnum):
    LAYOUT = "layout"
    NOME_IGUAL = "nome_igual"
    SINONIMO = "sinonimo"
    PARECIDO = "parecido"
    SEM_CORRESPONDENCIA = "sem_correspondencia"
    BLOQUEADA = "bloqueada"


@dataclass(frozen=True)
class SugestaoDeColuna:
    coluna: str
    campo: str | None
    origem: OrigemDaSugestao
    motivo_de_bloqueio: MotivoDeBloqueio | None = None


def _nomes_conhecidos() -> dict[str, tuple[str, OrigemDaSugestao]]:
    conhecidos: dict[str, tuple[str, OrigemDaSugestao]] = {}
    for campo in CAMPOS:
        for sinonimo in campo.sinonimos:
            conhecidos[sinonimo] = (campo.nome, OrigemDaSugestao.SINONIMO)
    for campo in CAMPOS:
        conhecidos[normalizar_nome_de_coluna(campo.nome)] = (
            campo.nome,
            OrigemDaSugestao.NOME_IGUAL,
        )
    return conhecidos


NOMES_CONHECIDOS = _nomes_conhecidos()


def _campo_parecido(nome: str) -> str | None:
    melhor, semelhanca = None, SEMELHANCA_MINIMA
    for conhecido, (campo, _) in NOMES_CONHECIDOS.items():
        atual = SequenceMatcher(None, nome, conhecido).ratio()
        if atual >= semelhanca:
            melhor, semelhanca = campo, atual
    return melhor


def _uso_interno_de_coluna_bloqueada(bloqueio: ColunaBloqueada, layout: Layout) -> str | None:
    """Endereço só serve para gerar o pseudônimo e ementa só para achar o bairro da Câmara."""
    nome = normalizar_nome_de_coluna(bloqueio.coluna)
    if layout.codigo is CodigoDoLayout.DATASET and nome == "TEXTO":
        return TEXTO_LIVRE
    if bloqueio.motivo is not MotivoDeBloqueio.ENDERECO:
        return None
    if nome == "NUMERO":
        return NUMERO
    return ENDERECO if any(parte in nome for parte in COLUNAS_DE_ENDERECO) else None


def _sugerir_coluna_livre(coluna: str, layout: Layout) -> SugestaoDeColuna:
    nome = normalizar_nome_de_coluna(coluna)
    if nome in layout.colunas:
        campo_do_layout = layout.colunas[nome]
        return SugestaoDeColuna(
            coluna,
            None if campo_do_layout == SEM_USO else campo_do_layout,
            OrigemDaSugestao.LAYOUT,
        )
    if nome in NOMES_CONHECIDOS:
        campo, origem = NOMES_CONHECIDOS[nome]
        return SugestaoDeColuna(coluna, campo, origem)
    parecido = _campo_parecido(nome)
    if parecido is not None:
        return SugestaoDeColuna(coluna, parecido, OrigemDaSugestao.PARECIDO)
    return SugestaoDeColuna(coluna, None, OrigemDaSugestao.SEM_CORRESPONDENCIA)


def sugerir_mapeamento(
    colunas: list[str], layout: Layout, bloqueadas: list[ColunaBloqueada]
) -> list[SugestaoDeColuna]:
    por_coluna = {bloqueada.coluna: bloqueada for bloqueada in bloqueadas}
    sugestoes = []
    for coluna in colunas:
        bloqueio = por_coluna.get(coluna)
        if bloqueio is None:
            sugestoes.append(_sugerir_coluna_livre(coluna, layout))
            continue
        uso = _uso_interno_de_coluna_bloqueada(bloqueio, layout)
        sugestoes.append(
            SugestaoDeColuna(coluna, uso, OrigemDaSugestao.BLOQUEADA, bloqueio.motivo),
        )
    return _sem_campo_repetido(sugestoes)


def _sem_campo_repetido(sugestoes: list[SugestaoDeColuna]) -> list[SugestaoDeColuna]:
    usados: set[str] = set()
    resultado = []
    for sugestao in sugestoes:
        repetido = sugestao.campo is not None and sugestao.campo in usados
        if sugestao.campo is not None:
            usados.add(sugestao.campo)
        resultado.append(
            SugestaoDeColuna(sugestao.coluna, None, OrigemDaSugestao.SEM_CORRESPONDENCIA)
            if repetido
            else sugestao
        )
    return resultado


def campos_obrigatorios_faltando(campos_mapeados: set[str]) -> list[str]:
    return [campo for campo in CAMPOS_OBRIGATORIOS if campo not in campos_mapeados]
