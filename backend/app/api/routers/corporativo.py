from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.dependencias import CorporativoAtualDep, auditar_consulta, exigir_corporativo
from app.api.dependencias_corporativas import ServicosDoOrgaoDep
from app.api.schemas.corporativo import (
    DemandaDoOrgaoResposta,
    FilaDoOrgaoResposta,
    OcorrenciaDoOrgaoResposta,
    PainelDoOrgaoResposta,
    RespostaComoOrgaoEntrada,
    RespostaRegistradaResposta,
)
from app.api.schemas.erros import ErroResposta
from app.application.casos_de_uso.corporativo.ocorrencias import (
    AbaDoOrgao,
    ConsultarOcorrenciaDoOrgao,
    ListarOcorrenciasDoOrgao,
    PedidoDaFila,
)
from app.application.casos_de_uso.corporativo.painel import (
    ConsultarDemandaDoOrgao,
    MontarPainelDoOrgao,
)
from app.application.casos_de_uso.corporativo.resposta import (
    ResponderComoOrgao,
    RespostaDoOrgao,
)
from app.application.casos_de_uso.corporativo.servicos import orgao_da_conta
from app.application.casos_de_uso.encaminhamentos.retorno import RespostaAoEncaminhamento
from app.domain.demanda_do_orgao import PeriodoEmAnos
from app.domain.filtros import ANO_FINAL_PADRAO, ANO_INICIAL_PADRAO

roteador = APIRouter(
    prefix="/corporativo",
    tags=["Área corporativa"],
    dependencies=[Depends(exigir_corporativo), Depends(auditar_consulta)],
)

PRIMEIRO_ANO_DA_BASE = 2012
ULTIMO_ANO_ACEITO = 2100
Ano = Annotated[int, Query(ge=PRIMEIRO_ANO_DA_BASE, le=ULTIMO_ANO_ACEITO)]
Deslocamento = Annotated[int, Query(ge=0)]
NAO_ENCONTRADA: dict[int | str, dict[str, Any]] = {
    404: {"model": ErroResposta, "description": "Ocorrência não encontrada neste órgão"},
}


@roteador.get(
    "/painel",
    summary="Visão geral do órgão: números do ciclo, mapa, semanas e o que vence primeiro",
)
def painel(usuario: CorporativoAtualDep, servicos: ServicosDoOrgaoDep) -> PainelDoOrgaoResposta:
    orgao = orgao_da_conta(usuario)
    return PainelDoOrgaoResposta.de_painel(MontarPainelDoOrgao(servicos).executar(orgao), orgao)


@roteador.get(
    "/ocorrencias",
    summary="Fila do órgão por aba, com o mesmo problema e quantas pessoas acompanham",
)
def listar(
    usuario: CorporativoAtualDep,
    servicos: ServicosDoOrgaoDep,
    aba: AbaDoOrgao = AbaDoOrgao.NOVAS,
    bairro: str | None = None,
    categoria: str | None = None,
    deslocamento: Deslocamento = 0,
) -> FilaDoOrgaoResposta:
    pedido = PedidoDaFila(aba, bairro, categoria, deslocamento)
    fila = ListarOcorrenciasDoOrgao(servicos).executar(orgao_da_conta(usuario), pedido)
    return FilaDoOrgaoResposta.de_fila(fila, servicos.hoje())


@roteador.get(
    "/ocorrencias/{encaminhamento_id}",
    summary="Detalhe de uma ocorrência do órgão",
    responses=NAO_ENCONTRADA,
)
def consultar(
    encaminhamento_id: int, usuario: CorporativoAtualDep, servicos: ServicosDoOrgaoDep
) -> OcorrenciaDoOrgaoResposta:
    orgao = orgao_da_conta(usuario)
    detalhe = ConsultarOcorrenciaDoOrgao(servicos).executar(orgao, encaminhamento_id)
    return OcorrenciaDoOrgaoResposta.de_ocorrencia(detalhe, orgao, servicos.hoje())


@roteador.post(
    "/ocorrencias/{encaminhamento_id}/resposta",
    summary="O órgão informa o andamento, resolve ou devolve, e pode juntar o mesmo problema",
    description=(
        "Resolver e devolver exigem a resposta ao cidadão. Em `tambem` vão as ocorrências do mesmo "
        "problema que recebem a mesma resposta; se uma delas não puder, nenhuma é gravada."
    ),
    responses={
        **NAO_ENCONTRADA,
        409: {"model": ErroResposta, "description": "A situação mudou e não aceita esta resposta"},
        422: {"model": ErroResposta, "description": "Campo recusado"},
    },
)
def responder(
    encaminhamento_id: int,
    entrada: RespostaComoOrgaoEntrada,
    usuario: CorporativoAtualDep,
    servicos: ServicosDoOrgaoDep,
) -> RespostaRegistradaResposta:
    resposta = RespostaAoEncaminhamento(
        entrada.situacao,
        entrada.protocolo_do_orgao,
        entrada.observacao,
        entrada.resposta_ao_cidadao,
        entrada.previsao,
    )
    pedido = RespostaDoOrgao(encaminhamento_id, resposta, tuple(entrada.tambem))
    registrada = ResponderComoOrgao(servicos).executar(usuario, pedido)
    return RespostaRegistradaResposta(
        codigo=registrada.principal.codigo,
        situacao=registrada.principal.situacao,
        codigos_juntos=[item.codigo for item in registrada.demais],
    )


@roteador.get(
    "/dados",
    summary="O que a base aberta registra com o nome do órgão, por ano, bairro, tema e situação",
)
def dados(
    usuario: CorporativoAtualDep,
    servicos: ServicosDoOrgaoDep,
    ano_inicio: Ano = ANO_INICIAL_PADRAO,
    ano_fim: Ano = ANO_FINAL_PADRAO,
) -> DemandaDoOrgaoResposta:
    orgao = orgao_da_conta(usuario)
    periodo = PeriodoEmAnos(min(ano_inicio, ano_fim), max(ano_inicio, ano_fim))
    demanda = ConsultarDemandaDoOrgao(servicos).executar(orgao, periodo)
    return DemandaDoOrgaoResposta.de_demanda(demanda, orgao, periodo)
