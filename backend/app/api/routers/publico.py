from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencias import (
    PainelDep,
    SegurancaDep,
    ServicosDePedidosDep,
    limitar_consultas_publicas,
)
from app.api.schemas.cidade import IndicadoresDoBairroResposta
from app.api.schemas.erros import ErroResposta
from app.api.schemas.pedidos import AndamentoResposta, ProtocoloEntrada
from app.application.casos_de_uso.cidade.meu_bairro import ConsultarMeuBairro

roteador = APIRouter(
    prefix="/publico",
    tags=["Acesso à informação"],
    dependencies=[Depends(limitar_consultas_publicas)],
)

BairroOficial = Annotated[str, Path(max_length=60)]


@roteador.post(
    "/pedidos/consultar",
    summary="Andamento de um pedido pelo protocolo que a pessoa recebeu",
    description=(
        "Não exige conta. Só devolve em busca exata, e o protocolo vai no corpo para não ficar "
        "em log de acesso. Traz a situação na fonte e, se houver, para qual órgão a ocorrência "
        "foi encaminhada e em que etapa ela está. Nunca devolve endereço nem texto."
    ),
    responses={422: {"model": ErroResposta, "description": "Protocolo fora do formato"}},
)
def consultar_pedido(
    entrada: ProtocoloEntrada, servicos: ServicosDePedidosDep, seguranca: SegurancaDep
) -> list[AndamentoResposta]:
    hoje = seguranca.relogio.agora().date()
    andamentos = servicos.consultar.executar(entrada.protocolo)
    return [AndamentoResposta.de_andamento(andamento, hoje) for andamento in andamentos]


@roteador.get(
    "/bairros/{bairro_oficial}",
    summary="Indicadores de um bairro, comparados com o Recife",
    description="Números agregados dos dados abertos. Não exige conta.",
    responses={422: {"model": ErroResposta, "description": "Bairro desconhecido"}},
)
def consultar_bairro(
    bairro_oficial: BairroOficial, painel: PainelDep
) -> IndicadoresDoBairroResposta:
    caso = ConsultarMeuBairro(painel.visao_geral, painel.territorio)
    return IndicadoresDoBairroResposta.model_validate(caso.executar(bairro_oficial))
