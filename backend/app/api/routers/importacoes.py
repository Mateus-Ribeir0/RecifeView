from typing import Annotated, Any

from fastapi import APIRouter, Query, Request, status

from app.api.dependencias import ServicosDeImportacaoDep, UsuarioAtualDep
from app.api.schemas.erros import ErroResposta
from app.api.schemas.importacoes import (
    CampoResposta,
    EscolhaDeColunasEntrada,
    ImportacaoDetalheResposta,
    ImportacaoResumoResposta,
    PaginaDeImportacoesResposta,
    PaginaDeRegistrosResposta,
    RespostasDePendenciasEntrada,
)
from app.application.casos_de_uso.importacoes.cancelar_importacao import CancelarImportacao
from app.application.casos_de_uso.importacoes.confirmar_importacao import ConfirmarImportacao
from app.application.casos_de_uso.importacoes.consultar_importacao import (
    ConsultarImportacao,
    ListarImportacoes,
    ListarRegistrosImportados,
)
from app.application.casos_de_uso.importacoes.definir_colunas import (
    DefinirColunas,
    EscolhaDeColunas,
)
from app.application.casos_de_uso.importacoes.desfazer_importacao import DesfazerImportacao
from app.application.casos_de_uso.importacoes.receber_arquivo import ReceberArquivo
from app.application.casos_de_uso.importacoes.responder_pendencias import (
    ResponderPendencias,
    RespostasDePendencias,
)
from app.application.portas.importacoes import FiltroDeImportacoes
from app.domain.erros import ErroDeDominio
from app.domain.importacao.campos import CAMPOS

roteador = APIRouter(prefix="/importacoes", tags=["Importações"])

Limite = Annotated[int, Query(ge=1, le=200)]
Deslocamento = Annotated[int, Query(ge=0)]
RESPOSTA_DE_ESTADO_INVALIDO: dict[int | str, dict[str, Any]] = {
    404: {"model": ErroResposta, "description": "Importação não encontrada"},
    409: {"model": ErroResposta, "description": "A importação não está nesta etapa"},
}


@roteador.get("/campos", summary="Lista os campos da base para o mapeamento de colunas")
def listar_campos(_: UsuarioAtualDep) -> list[CampoResposta]:
    return [CampoResposta.model_validate(campo) for campo in CAMPOS]


@roteador.get("", summary="Lista o histórico de importações")
def listar(
    _: UsuarioAtualDep,
    servicos: ServicosDeImportacaoDep,
    busca: str | None = None,
    situacao: str | None = None,
    fonte: str | None = None,
    limite: Limite = 50,
    deslocamento: Deslocamento = 0,
) -> PaginaDeImportacoesResposta:
    filtro = FiltroDeImportacoes(busca, situacao, fonte, limite, deslocamento)
    pagina = ListarImportacoes(servicos).executar(filtro)
    return PaginaDeImportacoesResposta(
        itens=[ImportacaoResumoResposta.de_importacao(item) for item in pagina.itens],
        total=pagina.total,
    )


@roteador.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Recebe um arquivo novo",
    description="O corpo da requisição é o próprio arquivo, sem multipart.",
    responses={
        413: {"model": ErroResposta, "description": "Arquivo maior que o limite"},
        422: {"model": ErroResposta, "description": "Arquivo vazio"},
    },
)
async def enviar_arquivo(
    request: Request,
    nome: Annotated[str, Query(min_length=1, max_length=255)],
    usuario: UsuarioAtualDep,
    servicos: ServicosDeImportacaoDep,
) -> ImportacaoResumoResposta:
    recebimento = servicos.armazenamento.iniciar_recebimento(nome)
    try:
        async for bloco in request.stream():
            recebimento.gravar(bloco)
    except ErroDeDominio:
        raise
    except Exception:
        recebimento.abandonar()
        raise
    importacao = ReceberArquivo(servicos).executar(recebimento.concluir(), usuario.id)
    return ImportacaoResumoResposta.de_importacao(importacao)


@roteador.get(
    "/{importacao_id}",
    summary="Devolve uma importação com as colunas, pendências e relatório",
    responses={404: {"model": ErroResposta, "description": "Importação não encontrada"}},
)
def consultar(
    importacao_id: int, _: UsuarioAtualDep, servicos: ServicosDeImportacaoDep
) -> ImportacaoDetalheResposta:
    return ImportacaoDetalheResposta.de_detalhe(
        ConsultarImportacao(servicos).executar(importacao_id)
    )


@roteador.put(
    "/{importacao_id}/colunas",
    summary="Define a fonte e o mapeamento das colunas",
    responses={**RESPOSTA_DE_ESTADO_INVALIDO, 422: {"model": ErroResposta}},
)
def definir_colunas(
    importacao_id: int,
    dados: EscolhaDeColunasEntrada,
    _: UsuarioAtualDep,
    servicos: ServicosDeImportacaoDep,
) -> ImportacaoResumoResposta:
    escolha = EscolhaDeColunas(
        dados.fonte, dados.data_do_retrato, dados.mapeamento, dados.valores_fixos
    )
    importacao = DefinirColunas(servicos).executar(importacao_id, escolha)
    return ImportacaoResumoResposta.de_importacao(importacao)


@roteador.put(
    "/{importacao_id}/pendencias",
    summary="Responde o que não bateu e valida o arquivo de novo",
    responses=RESPOSTA_DE_ESTADO_INVALIDO,
)
def responder_pendencias(
    importacao_id: int,
    dados: RespostasDePendenciasEntrada,
    _: UsuarioAtualDep,
    servicos: ServicosDeImportacaoDep,
) -> ImportacaoResumoResposta:
    respostas = RespostasDePendencias(**dados.model_dump())
    importacao = ResponderPendencias(servicos).executar(importacao_id, respostas)
    return ImportacaoResumoResposta.de_importacao(importacao)


@roteador.post(
    "/{importacao_id}/confirmar",
    summary="Confirma a carga na base",
    responses=RESPOSTA_DE_ESTADO_INVALIDO,
)
def confirmar(
    importacao_id: int, _: UsuarioAtualDep, servicos: ServicosDeImportacaoDep
) -> ImportacaoResumoResposta:
    importacao = ConfirmarImportacao(servicos).executar(importacao_id)
    return ImportacaoResumoResposta.de_importacao(importacao)


@roteador.post(
    "/{importacao_id}/cancelar",
    summary="Cancela uma importação que ainda não foi carregada",
    responses=RESPOSTA_DE_ESTADO_INVALIDO,
)
def cancelar(
    importacao_id: int, _: UsuarioAtualDep, servicos: ServicosDeImportacaoDep
) -> ImportacaoResumoResposta:
    importacao = CancelarImportacao(servicos).executar(importacao_id)
    return ImportacaoResumoResposta.de_importacao(importacao)


@roteador.post(
    "/{importacao_id}/desfazer",
    summary="Desfaz a importação mais recente",
    responses=RESPOSTA_DE_ESTADO_INVALIDO,
)
def desfazer(
    importacao_id: int, _: UsuarioAtualDep, servicos: ServicosDeImportacaoDep
) -> ImportacaoResumoResposta:
    importacao = DesfazerImportacao(servicos).executar(importacao_id)
    return ImportacaoResumoResposta.de_importacao(importacao)


@roteador.get(
    "/{importacao_id}/registros",
    summary="Lista os registros tratados de uma importação",
    description="Nunca devolve endereço, pseudônimo, coordenada nem texto livre.",
    responses={404: {"model": ErroResposta, "description": "Importação não encontrada"}},
)
def listar_registros(
    importacao_id: int,
    _: UsuarioAtualDep,
    servicos: ServicosDeImportacaoDep,
    limite: Limite = 50,
    deslocamento: Deslocamento = 0,
) -> PaginaDeRegistrosResposta:
    pagina = ListarRegistrosImportados(servicos).executar(importacao_id, limite, deslocamento)
    return PaginaDeRegistrosResposta.model_validate(pagina)
