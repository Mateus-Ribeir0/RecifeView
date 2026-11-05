from dataclasses import dataclass

from app.domain.fontes import Fonte
from app.domain.importacao.bairros import VALORES_SEM_BAIRRO, localizar_bairro
from app.domain.importacao.correcoes import (
    RPAS_VALIDAS,
    bairro_na_ementa,
    padrao_de_bairro_na_ementa,
)
from app.domain.importacao.decisoes import DEIXAR_VAZIO, DESCARTAR_LINHA, Decisoes
from app.domain.importacao.layouts import TEXTO_LIVRE
from app.domain.importacao.linha_recusada import recusar
from app.domain.importacao.relatorio import Correcao, MotivoDeDescarte, RelatorioDeLinhas


@dataclass(frozen=True)
class TerritorioResolvido:
    bairro: str | None
    recuperado: bool


def decidir_valor(decisoes: Decisoes, campo: str, valor: str) -> str | None:
    decisao = decisoes.substituicoes.get(campo, {}).get(valor)
    return decisao if decisao is not None else decisoes.padrao_para_valores.get(campo)


class ResolvedorDeTerritorio:
    def __init__(
        self,
        bairros: dict[str, str],
        decisoes: Decisoes,
        campos_mapeados: set[str],
        relatorio: RelatorioDeLinhas,
    ) -> None:
        self._bairros = bairros
        self._decisoes = decisoes
        self._relatorio = relatorio
        self._campo_do_bairro = (
            "bairro_oficial" if "bairro_oficial" in campos_mapeados else "bairro"
        )
        self._padrao_da_ementa = padrao_de_bairro_na_ementa(bairros)

    def resolver(self, valores: dict[str, str], fonte: str) -> TerritorioResolvido:
        bairro = self._resolver_bairro(valores)
        if bairro is not None:
            return TerritorioResolvido(bairro, recuperado=False)
        recuperado = self._recuperar_bairro_da_camara(valores, fonte)
        return TerritorioResolvido(recuperado, recuperado=recuperado is not None)

    def resolver_rpa(self, valores: dict[str, str], bairro: str | None) -> str | None:
        rpa = valores.get("rpa", "")
        if rpa in RPAS_VALIDAS:
            return rpa
        if bairro is None:
            return None
        self._relatorio.correcoes[Correcao.RPA_PREENCHIDA] += 1
        return self._bairros.get(bairro)

    def _resolver_bairro(self, valores: dict[str, str]) -> str | None:
        informado = valores.get(self._campo_do_bairro, "")
        if informado in VALORES_SEM_BAIRRO:
            return None
        oficial = localizar_bairro(informado, self._bairros)
        if oficial is not None:
            return oficial
        decisao = decidir_valor(self._decisoes, "bairro", informado)
        if decisao is None:
            self._relatorio.bairros_desconhecidos[informado] += 1
            return None
        if decisao == DESCARTAR_LINHA:
            recusar(MotivoDeDescarte.VALOR_RECUSADO)
        if decisao == DEIXAR_VAZIO:
            return None
        self._relatorio.correcoes[Correcao.BAIRRO_ASSOCIADO] += 1
        return decisao

    def _recuperar_bairro_da_camara(self, valores: dict[str, str], fonte: str) -> str | None:
        ementa = valores.get(TEXTO_LIVRE)
        if fonte != Fonte.CAMARA or not ementa:
            return None
        bairro = bairro_na_ementa(ementa, self._padrao_da_ementa)
        if bairro is not None:
            self._relatorio.correcoes[Correcao.BAIRRO_RECUPERADO] += 1
        return bairro
