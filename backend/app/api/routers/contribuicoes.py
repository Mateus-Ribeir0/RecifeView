from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.dependencias import (
    GestorAtualDep,
    ServicosDeContribuicoesDep,
    auditar_consulta,
)
from app.api.schemas.contribuicoes import (
    BairroResposta,
    CatalogoDoFormularioResposta,
    ContribuicaoEntrada,
    DecisaoDoParEntrada,
    PaginaDeOcorrenciasResposta,
    ParResposta,
    ResultadoDoEnvioResposta,
    ResumoDasContribuicoesResposta,
    TemaResposta,
)
from app.api.schemas.erros import ErroResposta
from app.api.schemas.importacoes import ImportacaoResumoResposta
from app.application.casos_de_uso.contribuicoes.decidir_par import DecidirPar
from app.application.casos_de_uso.contribuicoes.gerar_pacote import GerarPacote
from app.application.casos_de_uso.contribuicoes.receber_contribuicao import ReceberContribuicao
from app.domain.contribuicao.catalogo import TEMAS_DO_FORMULARIO
from app.domain.contribuicao.contribuicao import ResultadoDoEnvio
from app.domain.erros import EnviosDemais

roteador = APIRouter(prefix="/contribuicoes", tags=["Contribuições"])

ORIGEM_DESCONHECIDA = "desconhecida"
PARES_POR_PAGINA = 50
Limite = Annotated[int, Query(ge=1, le=200)]
Deslocamento = Annotated[int, Query(ge=0)]


@roteador.get("/catalogo", summary="Temas, serviços e bairros do formulário público")
def ler_catalogo(servicos: ServicosDeContribuicoesDep) -> CatalogoDoFormularioResposta:
    return CatalogoDoFormularioResposta(
        temas=[TemaResposta.model_validate(tema) for tema in TEMAS_DO_FORMULARIO],
        bairros=[BairroResposta.model_validate(bairro) for bairro in servicos.referencia.bairros()],
    )


@roteador.get(
    "/logradouros",
    summary="Vias conhecidas de um bairro",
    description="Só nomes de via, tirados dos arquivos públicos do 156. Nunca número de imóvel.",
)
def listar_logradouros(
    bairro: Annotated[str, Query(max_length=60)], servicos: ServicosDeContribuicoesDep
) -> list[str]:
    return servicos.referencia.logradouros(bairro)


@roteador.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Recebe um relato do formulário público",
    description="Não exige sessão. O relato fica em quarentena até a gestão revisar.",
    responses={
        422: {"model": ErroResposta, "description": "Campo recusado"},
        429: {"model": ErroResposta, "description": "Muitos envios em pouco tempo"},
    },
)
def receber(
    dados: ContribuicaoEntrada, request: Request, servicos: ServicosDeContribuicoesDep
) -> ResultadoDoEnvioResposta:
    if dados.site:
        return ResultadoDoEnvioResposta(resultado=ResultadoDoEnvio.NOVA)
    origem = request.client.host if request.client else ORIGEM_DESCONHECIDA
    if not servicos.limite.permitir(origem):
        raise EnviosDemais
    resultado = ReceberContribuicao(servicos).executar(dados.para_formulario())
    return ResultadoDoEnvioResposta(resultado=resultado)


@roteador.get(
    "/resumo",
    summary="Números da fila de relatos",
    dependencies=[Depends(auditar_consulta)],
)
def resumir(
    _: GestorAtualDep, servicos: ServicosDeContribuicoesDep
) -> ResumoDasContribuicoesResposta:
    return ResumoDasContribuicoesResposta.model_validate(servicos.contribuicoes.resumir())


@roteador.get(
    "/ocorrencias",
    summary="Ocorrências consolidadas",
    dependencies=[Depends(auditar_consulta)],
)
def listar_ocorrencias(
    _: GestorAtualDep,
    servicos: ServicosDeContribuicoesDep,
    limite: Limite = 50,
    deslocamento: Deslocamento = 0,
) -> PaginaDeOcorrenciasResposta:
    pagina = servicos.contribuicoes.listar_ocorrencias(limite, deslocamento)
    return PaginaDeOcorrenciasResposta.model_validate(pagina)


@roteador.get(
    "/pares",
    summary="Relatos parecidos que esperam decisão",
    dependencies=[Depends(auditar_consulta)],
)
def listar_pares(_: GestorAtualDep, servicos: ServicosDeContribuicoesDep) -> list[ParResposta]:
    pares = servicos.contribuicoes.listar_pares_abertos(PARES_POR_PAGINA)
    return [ParResposta.model_validate(par) for par in pares]


@roteador.put(
    "/pares/{par_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Decide se dois relatos são a mesma ocorrência",
    responses={404: {"model": ErroResposta, "description": "Dupla já decidida"}},
)
def decidir_par(
    par_id: int,
    dados: DecisaoDoParEntrada,
    usuario: GestorAtualDep,
    servicos: ServicosDeContribuicoesDep,
) -> None:
    DecidirPar(servicos).executar(par_id, dados.decisao, usuario.id)


@roteador.post(
    "/pacotes",
    status_code=status.HTTP_201_CREATED,
    summary="Gera o pacote de ocorrências revisadas para a importação",
    responses={409: {"model": ErroResposta, "description": "Pendência ou pacote vazio"}},
)
def gerar_pacote(
    usuario: GestorAtualDep, servicos: ServicosDeContribuicoesDep
) -> ImportacaoResumoResposta:
    importacao = GerarPacote(servicos).executar(usuario.id)
    return ImportacaoResumoResposta.de_importacao(importacao)
