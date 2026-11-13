from fastapi import APIRouter, Depends

from app.api.dependencias import (
    RepositorioDeEncaminhamentosDep,
    SegurancaDep,
    ServicosDeContribuicoesDep,
    exigir_gestao,
)
from app.api.schemas.encaminhamentos import PendenciasResposta
from app.application.casos_de_uso.encaminhamentos.pendencias import ConsultarPendenciasDoPainel

roteador = APIRouter(prefix="/avisos", tags=["Avisos"], dependencies=[Depends(exigir_gestao)])


@roteador.get(
    "/painel",
    summary="O que espera um passo da gestão, para os contadores do menu",
    description=(
        "Devoluções sem novo destino, falhas de envio e prazos vencidos, contando só o último "
        "encaminhamento de cada ocorrência, e duplas esperando o pente fino."
    ),
)
def consultar_pendencias(
    encaminhamentos: RepositorioDeEncaminhamentosDep,
    contribuicoes: ServicosDeContribuicoesDep,
    seguranca: SegurancaDep,
) -> PendenciasResposta:
    caso = ConsultarPendenciasDoPainel(
        encaminhamentos, contribuicoes.contribuicoes, seguranca.relogio
    )
    pendencias = caso.executar()
    return PendenciasResposta(
        devolvidos=pendencias.encaminhamentos.devolvidos,
        falhas=pendencias.encaminhamentos.falhas,
        prazo_vencido=pendencias.encaminhamentos.prazo_vencido,
        pedem_acao=pendencias.encaminhamentos.pedem_acao,
        duplas_no_pente_fino=pendencias.duplas_no_pente_fino,
    )
