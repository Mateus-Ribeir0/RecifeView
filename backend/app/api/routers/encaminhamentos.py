from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencias import (
    GestorAtualDep,
    ServicosDeEncaminhamentoDep,
    auditar_consulta,
    exigir_gestao,
    limitar_consultas_publicas,
)
from app.api.schemas.encaminhamentos import (
    EncaminhamentoParaOOrgaoResposta,
    EncaminhamentoResposta,
    EncaminharEntrada,
    OrgaoResposta,
    PreparoResposta,
    QuadroResposta,
    RespostaDoOrgaoEntrada,
    RetornoPeloLinkEntrada,
    TokenEntrada,
    orgaos_com_canal,
)
from app.api.schemas.erros import ErroResposta
from app.application.casos_de_uso.encaminhamentos.consultar import ListarEncaminhamentos
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
    PrepararEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.retorno import (
    AbrirPeloLink,
    ReenviarEncaminhamento,
    RegistrarRetornoPelaGestao,
    RegistrarRetornoPeloLink,
    RespostaAoEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.encaminhamentos import FiltroDeEncaminhamentos
from app.domain.encaminhamento.encaminhamento import SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import CATALOGO_DE_ORGAOS, Orgao

roteador = APIRouter(
    prefix="/encaminhamentos",
    tags=["Encaminhamentos"],
    dependencies=[Depends(exigir_gestao), Depends(auditar_consulta)],
)
retornos = APIRouter(
    prefix="/retornos",
    tags=["Retorno do órgão"],
    dependencies=[Depends(limitar_consultas_publicas)],
)

Limite = Annotated[int, Query(ge=1, le=200)]
Deslocamento = Annotated[int, Query(ge=0)]
NAO_ENCONTRADO: dict[int | str, dict[str, Any]] = {
    404: {"model": ErroResposta, "description": "Encaminhamento não encontrado"},
}
RETORNO_RECUSADO: dict[int | str, dict[str, Any]] = {
    **NAO_ENCONTRADO,
    409: {"model": ErroResposta, "description": "A situação atual não aceita esta resposta"},
    422: {"model": ErroResposta, "description": "Campo recusado"},
}


def _hoje(servicos: ServicosDeEncaminhamento) -> date:
    return servicos.relogio.agora().date()


def _resposta(entrada: RespostaDoOrgaoEntrada) -> RespostaAoEncaminhamento:
    return RespostaAoEncaminhamento(
        entrada.situacao, entrada.protocolo_do_orgao, entrada.observacao
    )


@roteador.get("", summary="Resumo e lista dos encaminhamentos, do mais novo ao mais antigo")
def listar(
    servicos: ServicosDeEncaminhamentoDep,
    situacao: SituacaoDoEncaminhamento | None = None,
    orgao: Orgao | None = None,
    so_atrasados: bool = False,
    pedem_acao: bool = False,
    limite: Limite = 50,
    deslocamento: Deslocamento = 0,
) -> QuadroResposta:
    filtro = FiltroDeEncaminhamentos(
        situacao=situacao,
        orgao=orgao,
        so_atrasados=so_atrasados,
        so_os_que_pedem_acao=pedem_acao,
        limite=limite,
        deslocamento=deslocamento,
    )
    return QuadroResposta.de_quadro(ListarEncaminhamentos(servicos).executar(filtro))


@roteador.get("/orgaos", summary="Órgãos que recebem encaminhamentos e o canal de cada um")
def listar_orgaos(servicos: ServicosDeEncaminhamentoDep) -> list[OrgaoResposta]:
    canais = {dados.orgao: servicos.despacho.canal_de(dados.orgao) for dados in CATALOGO_DE_ORGAOS}
    return orgaos_com_canal(canais)


@roteador.get(
    "/ocorrencias/{chave_registro}",
    summary="Prepara o encaminhamento de uma ocorrência: sugestão de destino e histórico",
    description=(
        "A sugestão é o órgão que o próprio registro aponta ou, sem isso, o mais citado nas "
        "indicações da Câmara do mesmo tema. A distribuição do tema vem junto, como evidência."
    ),
    responses={404: {"model": ErroResposta, "description": "Ocorrência não encontrada"}},
)
def preparar(chave_registro: int, servicos: ServicosDeEncaminhamentoDep) -> PreparoResposta:
    preparo = PrepararEncaminhamento(servicos).executar(chave_registro)
    return PreparoResposta.de_preparo(preparo, _hoje(servicos))


@roteador.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Encaminha uma ocorrência ao órgão escolhido",
    description=(
        "Grava o encaminhamento e manda a mensagem pelo canal do órgão. Se o canal falhar, o "
        "encaminhamento fica como `falhou` e pode ser reenviado."
    ),
    responses={
        404: {"model": ErroResposta, "description": "Ocorrência não encontrada"},
        409: {"model": ErroResposta, "description": "A ocorrência já tem encaminhamento aberto"},
        422: {"model": ErroResposta, "description": "Campo recusado"},
    },
)
def encaminhar(
    entrada: EncaminharEntrada, gestor: GestorAtualDep, servicos: ServicosDeEncaminhamentoDep
) -> EncaminhamentoResposta:
    pedido = PedidoDeEncaminhamento(
        chave_registro=entrada.chave_registro,
        orgao=entrada.orgao,
        criado_por=gestor.id,
        justificativa=entrada.justificativa,
        nota=entrada.nota,
        contribuicao_id=entrada.contribuicao_id,
    )
    encaminhamento = EncaminharOcorrencia(servicos).executar(pedido)
    return EncaminhamentoResposta.de_encaminhamento(encaminhamento, _hoje(servicos))


@roteador.get("/{encaminhamento_id}", summary="Detalhe e eventos", responses=NAO_ENCONTRADO)
def consultar(
    encaminhamento_id: int, servicos: ServicosDeEncaminhamentoDep
) -> EncaminhamentoResposta:
    encaminhamento = servicos.obter(encaminhamento_id)
    return EncaminhamentoResposta.de_encaminhamento(encaminhamento, _hoje(servicos))


@roteador.post(
    "/{encaminhamento_id}/retorno",
    summary="Registra o que o órgão respondeu por outro meio (telefone, ofício, e-mail)",
    responses=RETORNO_RECUSADO,
)
def registrar_retorno(
    encaminhamento_id: int,
    entrada: RespostaDoOrgaoEntrada,
    gestor: GestorAtualDep,
    servicos: ServicosDeEncaminhamentoDep,
) -> EncaminhamentoResposta:
    caso = RegistrarRetornoPelaGestao(servicos)
    encaminhamento = caso.executar(encaminhamento_id, _resposta(entrada), gestor.id)
    return EncaminhamentoResposta.de_encaminhamento(encaminhamento, _hoje(servicos))


@roteador.post(
    "/{encaminhamento_id}/reenvio",
    summary="Reenvia um encaminhamento cujo canal falhou, com um link de retorno novo",
    responses=RETORNO_RECUSADO,
)
def reenviar(
    encaminhamento_id: int, gestor: GestorAtualDep, servicos: ServicosDeEncaminhamentoDep
) -> EncaminhamentoResposta:
    encaminhamento = ReenviarEncaminhamento(servicos).executar(encaminhamento_id, gestor.id)
    return EncaminhamentoResposta.de_encaminhamento(encaminhamento, _hoje(servicos))


@retornos.post(
    "/abrir",
    summary="Mostra ao órgão o que ele recebeu",
    description=(
        "Não exige sessão: o token do link é a credencial. Ele vai no corpo, e não no caminho, "
        "para não ficar em log de acesso."
    ),
    responses={404: {"model": ErroResposta, "description": "Link vencido ou desconhecido"}},
)
def abrir_pelo_link(
    entrada: TokenEntrada, servicos: ServicosDeEncaminhamentoDep
) -> EncaminhamentoParaOOrgaoResposta:
    encaminhamento = AbrirPeloLink(servicos).executar(entrada.token)
    return EncaminhamentoParaOOrgaoResposta.de_encaminhamento(encaminhamento)


@retornos.post(
    "",
    summary="O órgão informa que recebeu, resolveu ou devolveu a ocorrência",
    description="Serve para a pessoa que abre o link e para o sistema do órgão, em JSON.",
    responses=RETORNO_RECUSADO,
)
def responder_pelo_link(
    entrada: RetornoPeloLinkEntrada, servicos: ServicosDeEncaminhamentoDep
) -> EncaminhamentoParaOOrgaoResposta:
    encaminhamento = RegistrarRetornoPeloLink(servicos).executar(entrada.token, _resposta(entrada))
    return EncaminhamentoParaOOrgaoResposta.de_encaminhamento(encaminhamento)
