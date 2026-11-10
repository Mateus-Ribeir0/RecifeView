from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencias import (
    PainelDep,
    ServicosDeContribuicoesDep,
    UsuarioAtualDep,
    auditar_consulta,
)
from app.api.schemas.cidade import IndicadoresDoBairroResposta, OcorrenciaPublicaResposta
from app.api.schemas.erros import ErroResposta
from app.application.casos_de_uso.cidade.meu_bairro import ConsultarMeuBairro
from app.application.casos_de_uso.cidade.ocorrencias import ListarOcorrenciasDaCidade

roteador = APIRouter(
    prefix="/cidade", tags=["Área do cidadão"], dependencies=[Depends(auditar_consulta)]
)

Texto = Annotated[str | None, Query(max_length=60)]


@roteador.get(
    "/ocorrencias",
    summary="Problemas relatados nos últimos 90 dias",
    description=(
        "Para qualquer conta. Mostra a rua só quando ela está na lista oficial de vias e o "
        "número só como faixa de centena. Nunca devolve o texto do relato."
    ),
)
def listar_ocorrencias(
    _: UsuarioAtualDep,
    servicos: ServicosDeContribuicoesDep,
    bairro: Texto = None,
    tema: Texto = None,
) -> list[OcorrenciaPublicaResposta]:
    caso = ListarOcorrenciasDaCidade(servicos.contribuicoes, servicos.relogio)
    return [OcorrenciaPublicaResposta.model_validate(item) for item in caso.executar(bairro, tema)]


@roteador.get(
    "/bairros/{bairro_oficial}",
    summary="Indicadores de um bairro, comparados com o Recife",
    responses={422: {"model": ErroResposta, "description": "Bairro desconhecido"}},
)
def meu_bairro(
    bairro_oficial: str, _: UsuarioAtualDep, painel: PainelDep
) -> IndicadoresDoBairroResposta:
    caso = ConsultarMeuBairro(painel.visao_geral, painel.territorio)
    return IndicadoresDoBairroResposta.model_validate(caso.executar(bairro_oficial))
