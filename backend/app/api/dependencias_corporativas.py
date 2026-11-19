from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencias import (
    GestaoDeSessoesDep,
    RepositoriosDep,
    Seguranca,
    SegurancaDep,
    ServicosDeEncaminhamentoDep,
    abrir_transacao,
)
from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
)
from app.application.casos_de_uso.corporativo.servicos import ServicosDoOrgao
from app.application.casos_de_uso.encaminhamentos.desempenho import CompararOrgaos
from app.application.casos_de_uso.notificacoes import NotificacoesDaConta
from app.application.portas.contas import EnvioDeEmail
from app.infrastructure.repositories.acessos_corporativos import (
    AcessosCorporativosSql,
    ConviteRepositorySql,
)
from app.infrastructure.repositories.avisos import DestinatariosDosAvisosSql
from app.infrastructure.repositories.demanda_do_orgao import DemandaDoOrgaoSql
from app.infrastructure.repositories.indicadores_do_ciclo import IndicadoresDoCicloSql
from app.infrastructure.repositories.notificacoes import NotificacaoRepositorySql
from app.infrastructure.settings import Configuracao

Transacao = Annotated[Session, Depends(abrir_transacao)]


def obter_servicos_de_acessos_corporativos(
    request: Request,
    sessao: Transacao,
    repositorios: RepositoriosDep,
    gestao_de_sessoes: GestaoDeSessoesDep,
) -> ServicosDeAcessosCorporativos:
    seguranca: Seguranca = request.app.state.seguranca
    configuracao: Configuracao = request.app.state.configuracao
    emails: EnvioDeEmail = request.app.state.caixa_de_emails
    return ServicosDeAcessosCorporativos(
        usuarios=repositorios.usuarios,
        convites=ConviteRepositorySql(sessao),
        acessos=AcessosCorporativosSql(sessao),
        senhas=seguranca.senhas,
        emails=emails,
        registro=repositorios.acessos,
        sessoes=gestao_de_sessoes,
        relogio=seguranca.relogio,
        endereco_do_site=configuracao.endereco_do_site,
    )


ServicosDeAcessosCorporativosDep = Annotated[
    ServicosDeAcessosCorporativos, Depends(obter_servicos_de_acessos_corporativos)
]


def obter_notificacoes_da_conta(sessao: Transacao, seguranca: SegurancaDep) -> NotificacoesDaConta:
    return NotificacoesDaConta(NotificacaoRepositorySql(sessao), seguranca.relogio)


NotificacoesDaContaDep = Annotated[NotificacoesDaConta, Depends(obter_notificacoes_da_conta)]


def obter_servicos_do_orgao(
    sessao: Transacao, encaminhamentos: ServicosDeEncaminhamentoDep
) -> ServicosDoOrgao:
    return ServicosDoOrgao(
        encaminhamentos=encaminhamentos,
        indicadores=IndicadoresDoCicloSql(sessao),
        pessoas=DestinatariosDosAvisosSql(sessao),
        demanda=DemandaDoOrgaoSql(sessao),
    )


ServicosDoOrgaoDep = Annotated[ServicosDoOrgao, Depends(obter_servicos_do_orgao)]


def obter_comparacao_dos_orgaos(
    sessao: Transacao, encaminhamentos: ServicosDeEncaminhamentoDep
) -> CompararOrgaos:
    return CompararOrgaos(
        encaminhamentos, IndicadoresDoCicloSql(sessao), AcessosCorporativosSql(sessao)
    )


CompararOrgaosDep = Annotated[CompararOrgaos, Depends(obter_comparacao_dos_orgaos)]
