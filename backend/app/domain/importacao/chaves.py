from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

from app.domain.fontes import Fonte
from app.domain.importacao.conversao import calcular_hash

ORIGEM_DA_CHAVE_POR_FONTE = {
    Fonte.CENTRAL_156.value: ("servico_codigo", "data_abertura", "bairro_oficial"),
    Fonte.DEFESA_CIVIL.value: (
        "data_abertura",
        "data_ult_movimento",
        "categoria",
        "tipo_registro",
        "bairro_oficial",
    ),
    Fonte.OUVIDORIA.value: ("data_abertura", "orgao", "servico", "tipo_registro"),
}
ORIGEM_DA_CHAVE_SEM_IDENTIFICADOR = ("data_abertura", "categoria", "bairro_oficial")


@dataclass(frozen=True)
class ChaveGerada:
    valor: int
    repetida_no_arquivo: bool


def _origem_da_chave(fonte: str, partes: Mapping[str, object]) -> tuple[str, ...]:
    if fonte in ORIGEM_DA_CHAVE_POR_FONTE:
        return ORIGEM_DA_CHAVE_POR_FONTE[fonte]
    return ("id_registro",) if partes.get("id_registro") else ORIGEM_DA_CHAVE_SEM_IDENTIFICADOR


class GeradorDeChaves:
    """Identifica um registro entre arquivos, sem depender de protocolo nem de `id_local`.

    Registros iguais no mesmo arquivo são pedidos diferentes no mesmo dia e lugar: a ordem de
    aparição os separa, e assim reimportar o mesmo arquivo gera as mesmas chaves.
    """

    def __init__(self, semente: str = "") -> None:
        self._semente = semente
        self._vistas: Counter[int] = Counter()

    def gerar(self, fonte: str, partes: Mapping[str, object]) -> ChaveGerada:
        origem = _origem_da_chave(fonte, partes)
        texto = "|".join(str(partes.get(campo) or "") for campo in origem)
        base = calcular_hash(f"{self._semente}{fonte}|{texto}")
        ordem = self._vistas[base]
        self._vistas[base] = ordem + 1
        if ordem == 0:
            return ChaveGerada(base, repetida_no_arquivo=False)
        return ChaveGerada(calcular_hash(f"{base}|{ordem}"), repetida_no_arquivo=True)
