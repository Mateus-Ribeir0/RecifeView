from dataclasses import asdict, dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any

from app.domain.fontes import Fonte
from app.domain.importacao.datas import FormatoDeData

DEIXAR_VAZIO = "__deixar_vazio__"
DESCARTAR_LINHA = "__descartar_linha__"
ACEITAR_COMO_NOVO = "__aceitar_como_novo__"


class PoliticaDeRepetidos(StrEnum):
    ATUALIZAR = "atualizar"
    MANTER_ATUAIS = "manter_atuais"
    INSERIR_COMO_NOVOS = "inserir_como_novos"


class PoliticaDeDuplicados(StrEnum):
    MANTER_TODOS = "manter_todos"
    MANTER_UM = "manter_um"


class PoliticaDeDatasInvalidas(StrEnum):
    DEIXAR_VAZIA = "deixar_vazia"
    DESCARTAR_LINHA = "descartar_linha"


@dataclass(frozen=True)
class Decisoes:
    """Tudo que uma pessoa escolheu para esta importação. Nada aqui é adivinhado depois."""

    fonte: Fonte | None = None
    data_do_retrato: date | None = None
    mapeamento: dict[str, str] = field(default_factory=dict)
    valores_fixos: dict[str, str] = field(default_factory=dict)
    formato_de_data: FormatoDeData | None = None
    substituicoes: dict[str, dict[str, str]] = field(default_factory=dict)
    padrao_para_valores: dict[str, str] = field(default_factory=dict)
    datas_invalidas: PoliticaDeDatasInvalidas | None = None
    repetidos_na_base: PoliticaDeRepetidos | None = None
    repetidos_no_arquivo: PoliticaDeDuplicados | None = None

    def para_dicionario(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["data_do_retrato"] = (
            self.data_do_retrato.isoformat() if self.data_do_retrato else None
        )
        return dados

    @classmethod
    def de_dicionario(cls, dados: dict[str, Any] | None) -> "Decisoes":
        dados = dados or {}
        retrato = dados.get("data_do_retrato")
        return cls(
            fonte=_opcional(Fonte, dados.get("fonte")),
            data_do_retrato=date.fromisoformat(retrato) if retrato else None,
            mapeamento=dados.get("mapeamento") or {},
            valores_fixos=dados.get("valores_fixos") or {},
            formato_de_data=_opcional(FormatoDeData, dados.get("formato_de_data")),
            substituicoes=dados.get("substituicoes") or {},
            padrao_para_valores=dados.get("padrao_para_valores") or {},
            datas_invalidas=_opcional(PoliticaDeDatasInvalidas, dados.get("datas_invalidas")),
            repetidos_na_base=_opcional(PoliticaDeRepetidos, dados.get("repetidos_na_base")),
            repetidos_no_arquivo=_opcional(PoliticaDeDuplicados, dados.get("repetidos_no_arquivo")),
        )


def _opcional[T](tipo: type[T], valor: str | None) -> T | None:
    return None if valor is None else tipo(valor)  # type: ignore[call-arg]
