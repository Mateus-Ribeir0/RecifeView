from bisect import bisect_left
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

from app.domain.fontes import Fonte
from app.domain.importacao.conversao import calcular_hash

ORIGEM_DA_CHAVE_POR_FONTE = {
    Fonte.CENTRAL_156.value: (
        "ano_do_arquivo",
        "servico_codigo",
        "data_abertura",
        "bairro_oficial",
    ),
    Fonte.DEFESA_CIVIL.value: (
        "ano_do_arquivo",
        "data_abertura",
        "data_ult_movimento",
        "categoria",
        "tipo_registro",
        "bairro_oficial",
    ),
    Fonte.OUVIDORIA.value: ("ano_do_arquivo", "data_abertura", "orgao", "servico", "tipo_registro"),
}
ORIGEM_DA_CHAVE_SEM_IDENTIFICADOR = (
    "ano_do_arquivo",
    "data_abertura",
    "categoria",
    "bairro_oficial",
)


@dataclass(frozen=True)
class ChaveGerada:
    valor: int
    repetida_no_arquivo: bool


@dataclass(frozen=True)
class PosicaoNoGrupo:
    indice: int
    copia_de_outra_linha: bool


UNICA_DO_GRUPO = PosicaoNoGrupo(0, copia_de_outra_linha=False)


def _origem_da_chave(fonte: str, partes: Mapping[str, object]) -> tuple[str, ...]:
    if fonte in ORIGEM_DA_CHAVE_POR_FONTE:
        return ORIGEM_DA_CHAVE_POR_FONTE[fonte]
    return ("id_registro",) if partes.get("id_registro") else ORIGEM_DA_CHAVE_SEM_IDENTIFICADOR


def chave_base(fonte: str, partes: Mapping[str, object], semente: str = "") -> int:
    origem = _origem_da_chave(fonte, partes)
    texto = "|".join(str(partes.get(campo) or "") for campo in origem)
    return calcular_hash(f"{semente}{fonte}|{texto}")


class OrdemPorConteudo:
    """Dá a posição de cada registro entre os que têm a mesma chave base.

    Registros iguais no mesmo arquivo são pedidos diferentes no mesmo dia e lugar. Ordenar pelo
    conteúdo, e não pela linha do arquivo, faz o mesmo pedido cair na mesma chave em arquivos que
    trazem as linhas em outra ordem. Sem isso, um arquivo idêntico pareceria alterado.
    """

    def __init__(self) -> None:
        self._assinaturas: dict[int, list[int]] = {}
        self._vistas: Counter[tuple[int, int]] = Counter()

    def anotar(self, base: int, assinatura: int) -> None:
        self._assinaturas.setdefault(base, []).append(assinatura)

    def fechar(self) -> None:
        self._assinaturas = {
            base: sorted(assinaturas)
            for base, assinaturas in self._assinaturas.items()
            if len(assinaturas) > 1
        }

    def posicao(self, base: int, assinatura: int) -> PosicaoNoGrupo:
        assinaturas = self._assinaturas.get(base)
        if assinaturas is None:
            return UNICA_DO_GRUPO
        copias = self._vistas[(base, assinatura)]
        self._vistas[(base, assinatura)] = copias + 1
        return PosicaoNoGrupo(bisect_left(assinaturas, assinatura) + copias, copias > 0)


class GeradorDeChaves:
    """Identifica um registro entre arquivos, sem depender de protocolo nem de `id_local`."""

    def __init__(self, ordem: OrdemPorConteudo, semente: str = "") -> None:
        self._ordem = ordem
        self._semente = semente

    def gerar(self, fonte: str, partes: Mapping[str, object], assinatura: int) -> ChaveGerada:
        base = chave_base(fonte, partes, self._semente)
        posicao = self._ordem.posicao(base, assinatura)
        valor = calcular_hash(f"{base}|{posicao.indice}") if posicao.indice else base
        return ChaveGerada(valor, posicao.copia_de_outra_linha)

    def anotar(self, fonte: str, partes: Mapping[str, object], assinatura: int) -> None:
        self._ordem.anotar(chave_base(fonte, partes, self._semente), assinatura)
