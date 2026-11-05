from collections.abc import Mapping
from dataclasses import dataclass, field

from app.domain.filtros import Filtros

SEM_MESMO_DIA = "dias > 0"


@dataclass(frozen=True)
class Recorte:
    """Pedaço de WHERE com os parâmetros dele, para montar consultas com filtros opcionais."""

    condicoes: tuple[str, ...] = ()
    parametros: Mapping[str, object] = field(default_factory=dict)

    def com(self, *outros: "Recorte") -> "Recorte":
        condicoes = list(self.condicoes)
        parametros = dict(self.parametros)
        for outro in outros:
            condicoes.extend(outro.condicoes)
            parametros.update(outro.parametros)
        return Recorte(tuple(condicoes), parametros)

    def com_condicao(self, condicao: str) -> "Recorte":
        return Recorte((*self.condicoes, condicao), self.parametros)

    @property
    def onde(self) -> str:
        return f"WHERE {' AND '.join(self.condicoes)}" if self.condicoes else ""


def por_ano(filtros: Filtros) -> Recorte:
    return Recorte(
        ("ano BETWEEN :ano_inicio AND :ano_fim",),
        {"ano_inicio": filtros.ano_inicio, "ano_fim": filtros.ano_fim},
    )


def por_territorio(filtros: Filtros) -> Recorte:
    recorte = Recorte()
    if filtros.rpas:
        recorte = recorte.com(Recorte(("rpa = ANY(:rpas)",), {"rpas": list(filtros.rpas)}))
    if filtros.bairros:
        recorte = recorte.com(
            Recorte(("bairro_oficial = ANY(:bairros)",), {"bairros": list(filtros.bairros)})
        )
    return recorte


def por_categoria(filtros: Filtros) -> Recorte:
    if not filtros.categorias:
        return Recorte()
    return Recorte(("categoria = ANY(:categorias)",), {"categorias": list(filtros.categorias)})


def recorte_completo(filtros: Filtros) -> Recorte:
    return por_ano(filtros).com(por_territorio(filtros), por_categoria(filtros))
