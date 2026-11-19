from typing import Any

from fastapi import APIRouter, Depends, Response

from app.api.cookies import gravar_cookie_de_sessao
from app.api.dependencias import ConfiguracaoDep, limitar_consultas_publicas
from app.api.dependencias_corporativas import ServicosDeAcessosCorporativosDep
from app.api.schemas.acessos_corporativos import (
    AceiteDoConviteEntrada,
    ConviteResposta,
    TokenDoConviteEntrada,
)
from app.api.schemas.autenticacao import AcessoResposta
from app.api.schemas.erros import ErroResposta
from app.application.casos_de_uso.acessos_corporativos.convite import AbrirConvite, AceitarConvite

roteador = APIRouter(
    prefix="/convites",
    tags=["Convite de acesso"],
    dependencies=[Depends(limitar_consultas_publicas)],
)
CONVITE_INVALIDO: dict[int | str, dict[str, Any]] = {
    404: {"model": ErroResposta, "description": "Convite vencido, usado ou trocado"}
}


@roteador.post(
    "/abrir",
    summary="Mostra para quem é o convite, antes de definir a senha",
    description="O token vai no corpo, e não no caminho, para não ficar em log de acesso.",
    responses=CONVITE_INVALIDO,
)
def abrir(
    entrada: TokenDoConviteEntrada, servicos: ServicosDeAcessosCorporativosDep
) -> ConviteResposta:
    return ConviteResposta.de_convite(AbrirConvite(servicos).executar(entrada.token))


@roteador.post(
    "/aceitar",
    summary="Define a senha do acesso corporativo e já abre a sessão",
    responses={
        **CONVITE_INVALIDO,
        422: {"model": ErroResposta, "description": "Senha fora das regras"},
    },
)
def aceitar(
    entrada: AceiteDoConviteEntrada,
    resposta: Response,
    servicos: ServicosDeAcessosCorporativosDep,
    configuracao: ConfiguracaoDep,
) -> AcessoResposta:
    sessao = AceitarConvite(servicos).executar(entrada.token, entrada.senha)
    gravar_cookie_de_sessao(resposta, sessao, configuracao.cookie_seguro)
    return AcessoResposta.de_acesso(sessao.acesso)
