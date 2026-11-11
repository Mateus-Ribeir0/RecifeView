from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.dependencias import (
    FiltrosDep,
    PainelDep,
    auditar_consulta,
    exigir_gestao,
)
from app.api.schemas.comum import MetaResposta, Resposta
from app.api.schemas.erros import ErroResposta
from app.api.schemas.painel import (
    CanaisDaOuvidoriaResposta,
    CatalogoDeFiltrosResposta,
    PrazosResposta,
    RecorrenciasResposta,
    RetornoResposta,
    TerritorioResposta,
    VisaoGeralResposta,
)
from app.api.schemas.prioridade import (
    CriterioResposta,
    CriteriosResposta,
    FilaClassificadaResposta,
    JulgamentoPadraoResposta,
    JulgamentosEntrada,
    PedidoDeFilaEntrada,
    PrioridadeResposta,
)
from app.api.schemas.war_room import (
    CalendarioResposta,
    QuadroDoDiaResposta,
    SobreOsDadosResposta,
)
from app.application.casos_de_uso.painel.comum import ListarFiltros, ResultadoDaConsulta
from app.application.casos_de_uso.painel.prazos import ConsultarPrazos
from app.application.casos_de_uso.painel.prioridade import (
    CalcularPrioridade,
    ClassificarFila,
    PedidoDeFila,
)
from app.application.casos_de_uso.painel.recorrencias import ConsultarRecorrencias
from app.application.casos_de_uso.painel.retorno import (
    ConsultarCanaisDaOuvidoria,
    ConsultarRetorno,
)
from app.application.casos_de_uso.painel.sobre import ConsultarSobreOsDados
from app.application.casos_de_uso.painel.territorio import ConsultarTerritorio
from app.application.casos_de_uso.painel.visao_geral import ConsultarVisaoGeral
from app.application.casos_de_uso.painel.war_room import (
    ConsultarCalendarioDaWarRoom,
    ConsultarQuadroDoDia,
)
from app.domain.ahp import CRITERIOS, JULGAMENTOS_PADRAO, RC_ACEITAVEL, pares
from app.domain.erros import DecisaoInvalida

DEPENDENCIAS = [Depends(exigir_gestao), Depends(auditar_consulta)]
ERRO_DE_FILTRO: dict[int | str, dict[str, Any]] = {
    422: {"model": ErroResposta, "description": "Filtros inválidos"},
}

catalogos = APIRouter(prefix="/catalogos", tags=["Catálogos"], dependencies=DEPENDENCIAS)
indicadores = APIRouter(prefix="/indicadores", tags=["Início"], dependencies=DEPENDENCIAS)
retorno = APIRouter(prefix="/retorno", tags=["Retorno e fragmentação"], dependencies=DEPENDENCIAS)
recorrencias = APIRouter(prefix="/recorrencias", tags=["Reincidência"], dependencies=DEPENDENCIAS)
prazos = APIRouter(prefix="/prazos", tags=["Prazos"], dependencies=DEPENDENCIAS)
territorio = APIRouter(prefix="/territorio", tags=["Território"], dependencies=DEPENDENCIAS)
prioridade = APIRouter(prefix="/prioridade", tags=["Prioridade (AHP)"], dependencies=DEPENDENCIAS)
war_room = APIRouter(prefix="/war-room", tags=["War Room"], dependencies=DEPENDENCIAS)
sobre = APIRouter(prefix="/sobre", tags=["Sobre os dados"], dependencies=DEPENDENCIAS)

ROTEADORES = (
    catalogos,
    indicadores,
    retorno,
    recorrencias,
    prazos,
    territorio,
    prioridade,
    war_room,
    sobre,
)


def _meta(resultado: ResultadoDaConsulta[object]) -> MetaResposta:
    return MetaResposta.de_procedencia(resultado.meta)


def _julgamentos(entrada: JulgamentosEntrada) -> dict[tuple[str, str], float]:
    escolhidos = {(item.primeiro, item.segundo): item.valor for item in entrada.julgamentos}
    if not set(escolhidos) <= set(pares()):
        raise DecisaoInvalida("Há comparação entre critérios que não existem.")
    return {**JULGAMENTOS_PADRAO, **escolhidos}


@catalogos.get("/filtros", summary="Lista anos, RPAs, bairros, categorias e fontes")
def listar_filtros(painel: PainelDep) -> CatalogoDeFiltrosResposta:
    return CatalogoDeFiltrosResposta.model_validate(ListarFiltros(painel.catalogo).executar())


@indicadores.get("/visao-geral", summary="KPIs e volume por fonte", responses=ERRO_DE_FILTRO)
def consultar_visao_geral(filtros: FiltrosDep, painel: PainelDep) -> Resposta[VisaoGeralResposta]:
    resultado = ConsultarVisaoGeral(painel.visao_geral, painel.referencia).executar(filtros)
    return Resposta(dados=VisaoGeralResposta.model_validate(resultado.dados), meta=_meta(resultado))


@retorno.get("/indicacoes", summary="Funil, canal de envio, destinos e caminhos da Câmara")
def consultar_retorno(filtros: FiltrosDep, painel: PainelDep) -> Resposta[RetornoResposta]:
    caso = ConsultarRetorno(painel.visao_geral, painel.retorno, painel.referencia)
    resultado = caso.executar(filtros)
    return Resposta(dados=RetornoResposta.model_validate(resultado.dados), meta=_meta(resultado))


@retorno.get("/ouvidoria", summary="Canais de entrada e prazo da Ouvidoria")
def consultar_ouvidoria(
    filtros: FiltrosDep, painel: PainelDep
) -> Resposta[CanaisDaOuvidoriaResposta]:
    resultado = ConsultarCanaisDaOuvidoria(painel.retorno, painel.referencia).executar(filtros)
    dados = CanaisDaOuvidoriaResposta.model_validate(resultado.dados)
    return Resposta(dados=dados, meta=_meta(resultado))


@recorrencias.get("", summary="Local repetido, intervalos e pontos crônicos do 156")
def consultar_recorrencias(
    filtros: FiltrosDep, painel: PainelDep, sem_generico: bool = False
) -> Resposta[RecorrenciasResposta]:
    caso = ConsultarRecorrencias(painel.recorrencias, painel.referencia)
    resultado = caso.executar(filtros, sem_generico)
    dados = RecorrenciasResposta.model_validate(resultado.dados)
    return Resposta(dados=dados, meta=_meta(resultado))


@prazos.get("", summary="Prazos em percentis, faixas, categorias e estoque aberto do 156")
def consultar_prazos(
    filtros: FiltrosDep, painel: PainelDep, sem_mesmo_dia: bool = False
) -> Resposta[PrazosResposta]:
    resultado = ConsultarPrazos(painel.prazos, painel.referencia).executar(filtros, sem_mesmo_dia)
    return Resposta(dados=PrazosResposta.model_validate(resultado.dados), meta=_meta(resultado))


@territorio.get("/bairros", summary="Taxas por bairro, faixas e tendência")
def consultar_territorio(filtros: FiltrosDep, painel: PainelDep) -> Resposta[TerritorioResposta]:
    resultado = ConsultarTerritorio(painel.territorio, painel.referencia).executar(filtros)
    return Resposta(dados=TerritorioResposta.model_validate(resultado.dados), meta=_meta(resultado))


@prioridade.get("/criterios", summary="Critérios do índice e julgamentos propostos pelo grupo")
def listar_criterios() -> CriteriosResposta:
    return CriteriosResposta(
        criterios=[CriterioResposta.model_validate(criterio) for criterio in CRITERIOS],
        julgamentos_padrao=[
            JulgamentoPadraoResposta(primeiro=primeiro, segundo=segundo, valor=valor)
            for (primeiro, segundo), valor in JULGAMENTOS_PADRAO.items()
        ],
        razao_aceitavel=RC_ACEITAVEL,
    )


@prioridade.post("/indice", summary="Calcula pesos, índice dos bairros e sensibilidade")
def calcular_indice(entrada: JulgamentosEntrada, painel: PainelDep) -> PrioridadeResposta:
    julgamentos = _julgamentos(entrada)
    resultado = CalcularPrioridade(painel.prioridade).executar(julgamentos)
    return PrioridadeResposta.de_prioridade(resultado)


@prioridade.post("/fila", summary="Classifica os registros em aberto de uma fonte")
def classificar_fila(
    entrada: PedidoDeFilaEntrada, filtros: FiltrosDep, painel: PainelDep
) -> FilaClassificadaResposta:
    pedido = PedidoDeFila(entrada.fonte, _julgamentos(entrada), entrada.semente, filtros)
    fila = ClassificarFila(painel.prioridade, painel.encaminhamentos).executar(pedido)
    return FilaClassificadaResposta.de_fila(fila)


@war_room.get("/calendario", summary="Dias disponíveis para a War Room")
def consultar_calendario(painel: PainelDep) -> CalendarioResposta:
    calendario = ConsultarCalendarioDaWarRoom(painel.war_room).executar()
    return CalendarioResposta.model_validate(calendario)


@war_room.get(
    "/dia",
    summary="Estado de um dia: entradas, estoque, fila e alertas",
    responses={422: {"model": ErroResposta, "description": "Dia fora da janela"}},
)
def consultar_dia(
    data: date,
    painel: PainelDep,
    inicio_da_serie: Annotated[date | None, Query()] = None,
) -> QuadroDoDiaResposta:
    quadro = ConsultarQuadroDoDia(painel.war_room, painel.prioridade).executar(
        data, inicio_da_serie
    )
    return QuadroDoDiaResposta.model_validate(quadro)


@sobre.get("", summary="Cobertura por fonte e ano e correções aplicadas")
def consultar_sobre(painel: PainelDep) -> SobreOsDadosResposta:
    dados = ConsultarSobreOsDados(painel.sobre, painel.referencia).executar()
    return SobreOsDadosResposta.model_validate(dados)
