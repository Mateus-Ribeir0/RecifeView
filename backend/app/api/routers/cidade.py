from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencias import (
    CidadaoAtualDep,
    RepositorioDeEncaminhamentosDep,
    SegurancaDep,
    ServicosDeContribuicoesDep,
    ServicosDePedidosDep,
    auditar_consulta,
)
from app.api.schemas.cidade import MeuRelatoResposta, OcorrenciaPublicaResposta
from app.api.schemas.erros import ErroResposta
from app.api.schemas.pedidos import PedidoAcompanhadoResposta, ProtocoloEntrada
from app.application.casos_de_uso.cidade.meus_relatos import ListarMeusRelatos
from app.application.casos_de_uso.cidade.ocorrencias import ListarOcorrenciasDaCidade
from app.application.casos_de_uso.pedidos.meus_pedidos import (
    AcompanharPedido,
    DeixarDeAcompanhar,
    ListarMeusPedidos,
)

roteador = APIRouter(
    prefix="/cidade", tags=["Área do cidadão"], dependencies=[Depends(auditar_consulta)]
)

Texto = Annotated[str | None, Query(max_length=60)]


@roteador.get(
    "/ocorrencias",
    summary="Problemas relatados nos últimos 90 dias",
    description=(
        "Só para conta de cidadão. Mostra a rua só quando ela está na lista oficial de vias e o "
        "número só como faixa de centena. Nunca devolve o texto do relato."
    ),
)
def listar_ocorrencias(
    _: CidadaoAtualDep,
    servicos: ServicosDeContribuicoesDep,
    bairro: Texto = None,
    tema: Texto = None,
) -> list[OcorrenciaPublicaResposta]:
    caso = ListarOcorrenciasDaCidade(servicos.contribuicoes, servicos.relogio)
    return [OcorrenciaPublicaResposta.model_validate(item) for item in caso.executar(bairro, tema)]


@roteador.get(
    "/meus-relatos",
    summary="Os relatos que a própria pessoa enviou com a conta aberta, e a situação de cada um",
    description="A situação de um relato somado é a da ocorrência que o recebeu.",
)
def listar_meus_relatos(
    cidadao: CidadaoAtualDep,
    servicos: ServicosDeContribuicoesDep,
    encaminhamentos: RepositorioDeEncaminhamentosDep,
    seguranca: SegurancaDep,
) -> list[MeuRelatoResposta]:
    caso = ListarMeusRelatos(servicos.contribuicoes, encaminhamentos)
    hoje = seguranca.relogio.agora().date()
    return [MeuRelatoResposta.de_relato(item, hoje) for item in caso.executar(cidadao)]


@roteador.get(
    "/pedidos",
    summary="Os protocolos que a pessoa guardou e o andamento de cada um",
    description="Pedidos feitos no Conecta Recife, no 156 ou na Ouvidoria, com o encaminhamento.",
)
def listar_meus_pedidos(
    cidadao: CidadaoAtualDep, servicos: ServicosDePedidosDep, seguranca: SegurancaDep
) -> list[PedidoAcompanhadoResposta]:
    hoje = seguranca.relogio.agora().date()
    pedidos = ListarMeusPedidos(servicos).executar(cidadao)
    return [PedidoAcompanhadoResposta.de_pedido(item, hoje) for item in pedidos]


@roteador.post(
    "/pedidos",
    status_code=status.HTTP_201_CREATED,
    summary="Guarda um protocolo para acompanhar",
    description="Até 20 por conta. O protocolo fica guardado mesmo sem registro na base ainda.",
    responses={
        409: {"model": ErroResposta, "description": "Limite de pedidos atingido"},
        422: {"model": ErroResposta, "description": "Protocolo fora do formato"},
    },
)
def acompanhar_pedido(
    entrada: ProtocoloEntrada,
    cidadao: CidadaoAtualDep,
    servicos: ServicosDePedidosDep,
    seguranca: SegurancaDep,
) -> PedidoAcompanhadoResposta:
    pedido = AcompanharPedido(servicos).executar(cidadao, entrada.protocolo)
    return PedidoAcompanhadoResposta.de_pedido(pedido, seguranca.relogio.agora().date())


@roteador.delete(
    "/pedidos/{pedido_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deixa de acompanhar um protocolo",
)
def deixar_de_acompanhar(
    pedido_id: int, cidadao: CidadaoAtualDep, servicos: ServicosDePedidosDep
) -> None:
    DeixarDeAcompanhar(servicos).executar(cidadao, pedido_id)
