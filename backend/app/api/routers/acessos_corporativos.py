from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencias import GestorAtualDep, auditar_consulta, exigir_gestao
from app.api.dependencias_corporativas import ServicosDeAcessosCorporativosDep
from app.api.schemas.acessos_corporativos import (
    AcessoCorporativoResposta,
    DadosDoAcessoEntrada,
    ListaDeAcessosResposta,
    NovoAcessoEntrada,
)
from app.api.schemas.erros import ErroResposta
from app.application.casos_de_uso.acessos_corporativos.acessos import (
    CriarAcessoCorporativo,
    DadosDoAcesso,
    DesativarAcesso,
    EditarAcessoCorporativo,
    ExcluirAcesso,
    ListarAcessosCorporativos,
    NovoAcesso,
    ReativarAcesso,
    ReenviarConvite,
)
from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
)
from app.domain.acesso_corporativo import AcessoCorporativo

roteador = APIRouter(
    prefix="/acessos-corporativos",
    tags=["Acessos corporativos"],
    dependencies=[Depends(exigir_gestao), Depends(auditar_consulta)],
)

SO_DA_ADMINISTRACAO: dict[int | str, dict[str, Any]] = {
    403: {"model": ErroResposta, "description": "Só o perfil Administração altera acessos"},
    404: {"model": ErroResposta, "description": "Acesso corporativo não encontrado"},
}


def _resposta(
    acesso: AcessoCorporativo, servicos: ServicosDeAcessosCorporativos
) -> AcessoCorporativoResposta:
    return AcessoCorporativoResposta.de_acesso(acesso, servicos.relogio.agora())


def _dados(entrada: DadosDoAcessoEntrada) -> DadosDoAcesso:
    return DadosDoAcesso(entrada.nome, entrada.orgao)


@roteador.get("", summary="Contas corporativas dos órgãos, com a situação do convite")
def listar(
    gestor: GestorAtualDep, servicos: ServicosDeAcessosCorporativosDep
) -> ListaDeAcessosResposta:
    acessos = ListarAcessosCorporativos(servicos).executar()
    return ListaDeAcessosResposta(
        pode_alterar=gestor.e_da_administracao,
        itens=[_resposta(acesso, servicos) for acesso in acessos],
    )


@roteador.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cria o acesso de um órgão e manda o convite por e-mail",
    description=(
        "O convite leva um link de uso único, válido por 7 dias, em que a pessoa define a senha. "
        "Se o e-mail não sair, nada é gravado."
    ),
    responses={
        **SO_DA_ADMINISTRACAO,
        409: {"model": ErroResposta, "description": "Já existe conta com este e-mail"},
        422: {"model": ErroResposta, "description": "Campo recusado"},
    },
)
def criar(
    entrada: NovoAcessoEntrada,
    gestor: GestorAtualDep,
    servicos: ServicosDeAcessosCorporativosDep,
) -> AcessoCorporativoResposta:
    novo = NovoAcesso(entrada.email, _dados(entrada))
    return _resposta(CriarAcessoCorporativo(servicos).executar(novo, gestor), servicos)


@roteador.put(
    "/{usuario_id}",
    summary="Corrige o nome ou o órgão de um acesso",
    responses={
        **SO_DA_ADMINISTRACAO,
        422: {"model": ErroResposta, "description": "Campo recusado"},
    },
)
def editar(
    usuario_id: UUID,
    entrada: DadosDoAcessoEntrada,
    gestor: GestorAtualDep,
    servicos: ServicosDeAcessosCorporativosDep,
) -> AcessoCorporativoResposta:
    acesso = EditarAcessoCorporativo(servicos).executar(usuario_id, _dados(entrada), gestor)
    return _resposta(acesso, servicos)


@roteador.post(
    "/{usuario_id}/convite",
    summary="Manda um convite novo, que substitui o anterior",
    responses={
        **SO_DA_ADMINISTRACAO,
        409: {"model": ErroResposta, "description": "Convite já aceito ou acesso desativado"},
    },
)
def reenviar_convite(
    usuario_id: UUID, gestor: GestorAtualDep, servicos: ServicosDeAcessosCorporativosDep
) -> AcessoCorporativoResposta:
    return _resposta(ReenviarConvite(servicos).executar(usuario_id, gestor), servicos)


@roteador.post(
    "/{usuario_id}/desativacao",
    summary="Desativa o acesso e encerra as sessões abertas",
    responses=SO_DA_ADMINISTRACAO,
)
def desativar(
    usuario_id: UUID, gestor: GestorAtualDep, servicos: ServicosDeAcessosCorporativosDep
) -> AcessoCorporativoResposta:
    return _resposta(DesativarAcesso(servicos).executar(usuario_id, gestor), servicos)


@roteador.post(
    "/{usuario_id}/reativacao", summary="Reativa o acesso", responses=SO_DA_ADMINISTRACAO
)
def reativar(
    usuario_id: UUID, gestor: GestorAtualDep, servicos: ServicosDeAcessosCorporativosDep
) -> AcessoCorporativoResposta:
    return _resposta(ReativarAcesso(servicos).executar(usuario_id, gestor), servicos)


@roteador.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui o acesso: apaga nome e e-mail e mantém a auditoria",
    responses=SO_DA_ADMINISTRACAO,
)
def excluir(
    usuario_id: UUID, gestor: GestorAtualDep, servicos: ServicosDeAcessosCorporativosDep
) -> None:
    ExcluirAcesso(servicos).executar(usuario_id, gestor)
