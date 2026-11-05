import re
from collections.abc import Iterable
from datetime import date
from enum import StrEnum
from functools import lru_cache

CACHE_DE_DATAS = 100_000
TAMANHO_DA_DATA = 10
ULTIMO_MES = 12


class FormatoDeData(StrEnum):
    ISO = "iso"
    ANO_BARRA = "ano_barra"
    DIA_MES_ANO = "dia_mes_ano"
    MES_DIA_ANO = "mes_dia_ano"


PADRAO_ANO_PRIMEIRO = re.compile(r"^(\d{4})([-/])(\d{1,2})[-/](\d{1,2})")
PADRAO_ANO_POR_ULTIMO = re.compile(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})")


def _montar_data(ano: str, mes: str, dia: str) -> date | None:
    try:
        return date(int(ano), int(mes), int(dia))
    except ValueError:
        return None


@lru_cache(maxsize=CACHE_DE_DATAS)
def interpretar_data(valor: str, formato_barra: FormatoDeData) -> date | None:
    """Converte uma data. `formato_barra` só decide a ordem de dd/mm/aaaa ou mm/dd/aaaa."""
    texto = valor.strip()[:TAMANHO_DA_DATA]
    if (achado := PADRAO_ANO_PRIMEIRO.match(texto)) is not None:
        ano, _, mes, dia = achado.groups()
        return _montar_data(ano, mes, dia)
    if (achado := PADRAO_ANO_POR_ULTIMO.match(texto)) is None:
        return None
    primeiro, segundo, ano = achado.groups()
    if formato_barra is FormatoDeData.MES_DIA_ANO:
        return _montar_data(ano, primeiro, segundo)
    return _montar_data(ano, segundo, primeiro)


def _so_cabe_em_uma_ordem(primeiro: int, segundo: int) -> FormatoDeData | None:
    if primeiro > ULTIMO_MES >= segundo:
        return FormatoDeData.DIA_MES_ANO
    if segundo > ULTIMO_MES >= primeiro:
        return FormatoDeData.MES_DIA_ANO
    return None


def formato_de_data_ambiguo(valores: Iterable[str]) -> FormatoDeData | None:
    """Devolve a ordem provada pelos valores; None quando nenhum deles decide dia ou mês."""
    for valor in valores:
        achado = PADRAO_ANO_POR_ULTIMO.match(valor.strip()[:TAMANHO_DA_DATA])
        if achado is None:
            continue
        ordem = _so_cabe_em_uma_ordem(int(achado.group(1)), int(achado.group(2)))
        if ordem is not None:
            return ordem
    return None


def usa_barra_com_ano_no_fim(valores: Iterable[str]) -> bool:
    return any(PADRAO_ANO_POR_ULTIMO.match(valor.strip()[:TAMANHO_DA_DATA]) for valor in valores)
