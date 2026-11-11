from collections.abc import Iterator
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.casos_de_uso.entrar import Entrar
from app.application.casos_de_uso.identificar_usuario import IdentificarUsuario
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.casos_de_uso.pedidos.consultar_pedido import ConsultarPedido
from app.application.casos_de_uso.pedidos.meus_pedidos import ServicosDePedidos
from app.application.casos_de_uso.renovar_acesso import RenovarAcesso
from app.application.casos_de_uso.sair import Sair
from app.application.casos_de_uso.trocar_senha import TrocarSenha
from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.contas import EnvioDeEmail
from app.application.portas.contribuicoes import LimiteDeEnvios
from app.application.portas.encaminhamentos import (
    DespachoAosOrgaos,
    EncaminhamentosDasOcorrencias,
)
from app.application.portas.painel import (
    CatalogoRepository,
    PrazoRepository,
    PrioridadeRepository,
    RecorrenciaRepository,
    ReferenciaRepository,
    RegistroDeConsultas,
    RetornoRepository,
    SobreRepository,
    TerritorioRepository,
    VisaoGeralRepository,
    WarRoomRepository,
)
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import EmissorDeTokenDeAcesso, HashDeSenha
from app.application.portas.sessoes import SessaoRepository
from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import GestaoDeSessoes
from app.domain.auditoria import ConsultaAuditada
from app.domain.erros import AcessoNegado, ErroDeDominio, SessaoInvalida, TentativasDemais
from app.domain.filtros import ANO_FINAL_PADRAO, ANO_INICIAL_PADRAO, Filtros
from app.domain.usuario import Usuario
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.catalogos import (
    CatalogoRepositorySql,
    ReferenciaRepositorySql,
)
from app.infrastructure.repositories.codigos_de_conta import CodigoDeContaRepositorySql
from app.infrastructure.repositories.consultas import RegistroDeConsultasSql
from app.infrastructure.repositories.encaminhamentos import EncaminhamentoRepositorySql
from app.infrastructure.repositories.pedidos import (
    ConsultaDePedidosSql,
    PedidoAcompanhadoRepositorySql,
)
from app.infrastructure.repositories.prazos import PrazoRepositorySql
from app.infrastructure.repositories.prioridade import PrioridadeRepositorySql
from app.infrastructure.repositories.recorrencias import RecorrenciaRepositorySql
from app.infrastructure.repositories.retorno import RetornoRepositorySql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.sobre import SobreRepositorySql
from app.infrastructure.repositories.territorio import TerritorioRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from app.infrastructure.repositories.visao_geral import VisaoGeralRepositorySql
from app.infrastructure.repositories.war_room import WarRoomRepositorySql
from app.infrastructure.settings import Configuracao

PADRAO_DO_PERIODO = r"^\d{4}-\d{2}$"
ORIGEM_DESCONHECIDA = "desconhecida"
TAMANHO_DO_ANO = 4


@dataclass(frozen=True)
class Seguranca:
    senhas: HashDeSenha
    emissor: EmissorDeTokenDeAcesso
    relogio: Relogio
    duracao_da_sessao: timedelta


@dataclass(frozen=True)
class Repositorios:
    usuarios: UsuarioRepository
    sessoes: SessaoRepository
    acessos: RegistroDeAcessos


@dataclass(frozen=True)
class RepositoriosDoPainel:
    catalogo: CatalogoRepository
    referencia: ReferenciaRepository
    visao_geral: VisaoGeralRepository
    retorno: RetornoRepository
    recorrencias: RecorrenciaRepository
    prazos: PrazoRepository
    territorio: TerritorioRepository
    prioridade: PrioridadeRepository
    war_room: WarRoomRepository
    sobre: SobreRepository
    encaminhamentos: EncaminhamentosDasOcorrencias


def obter_configuracao(request: Request) -> Configuracao:
    configuracao: Configuracao = request.app.state.configuracao
    return configuracao


def obter_seguranca(request: Request) -> Seguranca:
    seguranca: Seguranca = request.app.state.seguranca
    return seguranca


def obter_servicos_de_importacao(request: Request) -> ServicosDeImportacao:
    servicos: ServicosDeImportacao = request.app.state.servicos_de_importacao
    return servicos


def obter_servicos_de_contribuicoes(request: Request) -> ServicosDeContribuicoes:
    servicos: ServicosDeContribuicoes = request.app.state.servicos_de_contribuicoes
    return servicos


def abrir_transacao(request: Request) -> Iterator[Session]:
    fabrica: sessionmaker[Session] = request.app.state.fabrica_de_sessoes
    with fabrica() as sessao:
        try:
            yield sessao
        except ErroDeDominio:
            # Uma entrada recusada também precisa gravar a tentativa e o evento de auditoria.
            sessao.commit()
            raise
        except Exception:
            sessao.rollback()
            raise
        else:
            sessao.commit()


def obter_repositorios(sessao: Annotated[Session, Depends(abrir_transacao)]) -> Repositorios:
    return Repositorios(
        usuarios=UsuarioRepositorySql(sessao),
        sessoes=SessaoRepositorySql(sessao),
        acessos=RegistroDeAcessosSql(sessao),
    )


ConfiguracaoDep = Annotated[Configuracao, Depends(obter_configuracao)]
SegurancaDep = Annotated[Seguranca, Depends(obter_seguranca)]
ServicosDeImportacaoDep = Annotated[ServicosDeImportacao, Depends(obter_servicos_de_importacao)]
ServicosDeContribuicoesDep = Annotated[
    ServicosDeContribuicoes, Depends(obter_servicos_de_contribuicoes)
]
RepositoriosDep = Annotated[Repositorios, Depends(obter_repositorios)]


def obter_gestao_de_sessoes(
    repositorios: RepositoriosDep, seguranca: SegurancaDep
) -> GestaoDeSessoes:
    return GestaoDeSessoes(
        repositorios.sessoes, seguranca.emissor, seguranca.relogio, seguranca.duracao_da_sessao
    )


GestaoDeSessoesDep = Annotated[GestaoDeSessoes, Depends(obter_gestao_de_sessoes)]


def obter_entrar(
    repositorios: RepositoriosDep, seguranca: SegurancaDep, sessoes: GestaoDeSessoesDep
) -> Entrar:
    return Entrar(
        repositorios.usuarios, seguranca.senhas, sessoes, repositorios.acessos, seguranca.relogio
    )


def obter_renovar_acesso(
    repositorios: RepositoriosDep, sessoes: GestaoDeSessoesDep
) -> RenovarAcesso:
    return RenovarAcesso(repositorios.usuarios, sessoes)


def obter_sair(
    repositorios: RepositoriosDep, seguranca: SegurancaDep, sessoes: GestaoDeSessoesDep
) -> Sair:
    return Sair(sessoes, repositorios.acessos, seguranca.relogio)


def obter_trocar_senha(
    repositorios: RepositoriosDep, seguranca: SegurancaDep, sessoes: GestaoDeSessoesDep
) -> TrocarSenha:
    return TrocarSenha(
        repositorios.usuarios, seguranca.senhas, sessoes, repositorios.acessos, seguranca.relogio
    )


def obter_identificar_usuario(
    repositorios: RepositoriosDep, seguranca: SegurancaDep
) -> IdentificarUsuario:
    return IdentificarUsuario(repositorios.usuarios, seguranca.emissor, seguranca.relogio)


esquema_bearer = HTTPBearer(auto_error=False)


def obter_usuario_atual(
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
    identificar: Annotated[IdentificarUsuario, Depends(obter_identificar_usuario)],
) -> Usuario:
    if credenciais is None:
        raise SessaoInvalida
    return identificar.executar(credenciais.credentials)


def obter_repositorios_do_painel(
    sessao: Annotated[Session, Depends(abrir_transacao)],
) -> RepositoriosDoPainel:
    return RepositoriosDoPainel(
        catalogo=CatalogoRepositorySql(sessao),
        referencia=ReferenciaRepositorySql(sessao),
        visao_geral=VisaoGeralRepositorySql(sessao),
        retorno=RetornoRepositorySql(sessao),
        recorrencias=RecorrenciaRepositorySql(sessao),
        prazos=PrazoRepositorySql(sessao),
        territorio=TerritorioRepositorySql(sessao),
        prioridade=PrioridadeRepositorySql(sessao),
        war_room=WarRoomRepositorySql(sessao),
        sobre=SobreRepositorySql(sessao),
        encaminhamentos=EncaminhamentoRepositorySql(sessao),
    )


def obter_registro_de_consultas(
    sessao: Annotated[Session, Depends(abrir_transacao)],
) -> RegistroDeConsultas:
    return RegistroDeConsultasSql(sessao)


def _ano_do_periodo(valor: str) -> int:
    return int(valor[:TAMANHO_DO_ANO])


def obter_filtros(
    periodo_inicio: Annotated[str, Query(pattern=PADRAO_DO_PERIODO)] = f"{ANO_INICIAL_PADRAO}-01",
    periodo_fim: Annotated[str, Query(pattern=PADRAO_DO_PERIODO)] = f"{ANO_FINAL_PADRAO}-12",
    rpa: Annotated[list[str] | None, Query()] = None,
    bairro: Annotated[list[str] | None, Query()] = None,
    categoria: Annotated[list[str] | None, Query()] = None,
) -> Filtros:
    return Filtros(
        _ano_do_periodo(periodo_inicio),
        _ano_do_periodo(periodo_fim),
        tuple(rpa or ()),
        tuple(bairro or ()),
        tuple(categoria or ()),
    )


EntrarDep = Annotated[Entrar, Depends(obter_entrar)]
RenovarAcessoDep = Annotated[RenovarAcesso, Depends(obter_renovar_acesso)]
SairDep = Annotated[Sair, Depends(obter_sair)]
TrocarSenhaDep = Annotated[TrocarSenha, Depends(obter_trocar_senha)]
UsuarioAtualDep = Annotated[Usuario, Depends(obter_usuario_atual)]


def obter_usuario_se_entrou(
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
    identificar: Annotated[IdentificarUsuario, Depends(obter_identificar_usuario)],
) -> Usuario | None:
    """Para rota pública: sem token, segue sem usuário; token vencido ainda responde 401."""
    if credenciais is None:
        return None
    return identificar.executar(credenciais.credentials)


UsuarioSeEntrouDep = Annotated[Usuario | None, Depends(obter_usuario_se_entrou)]


def exigir_gestao(usuario: UsuarioAtualDep) -> Usuario:
    """Painel, importação e pente fino são só da gestão: conta de cidadão recebe 403."""
    if not usuario.e_da_gestao:
        raise AcessoNegado
    return usuario


GestorAtualDep = Annotated[Usuario, Depends(exigir_gestao)]


def exigir_cidadao(usuario: UsuarioAtualDep) -> Usuario:
    """A área do cidadão é só do cidadão: a conta da gestão trabalha no painel."""
    if usuario.e_da_gestao:
        raise AcessoNegado
    return usuario


CidadaoAtualDep = Annotated[Usuario, Depends(exigir_cidadao)]


def obter_servicos_de_conta(
    request: Request,
    sessao: Annotated[Session, Depends(abrir_transacao)],
    repositorios: RepositoriosDep,
    gestao_de_sessoes: GestaoDeSessoesDep,
) -> ServicosDeConta:
    seguranca: Seguranca = request.app.state.seguranca
    emails: EnvioDeEmail = request.app.state.caixa_de_emails
    return ServicosDeConta(
        usuarios=repositorios.usuarios,
        codigos=CodigoDeContaRepositorySql(sessao),
        senhas=seguranca.senhas,
        emails=emails,
        acessos=repositorios.acessos,
        sessoes=gestao_de_sessoes,
        relogio=seguranca.relogio,
        pedidos=PedidoAcompanhadoRepositorySql(sessao),
    )


def obter_bairros_oficiais(request: Request) -> frozenset[str]:
    servicos: ServicosDeContribuicoes = request.app.state.servicos_de_contribuicoes
    return frozenset(bairro.chave for bairro in servicos.referencia.bairros())


def limitar_operacoes_de_conta(request: Request) -> None:
    """Cadastro, código e recuperação gastam e-mail: cada origem tem um limite curto."""
    limite: LimiteDeEnvios = request.app.state.limite_de_contas
    origem = request.client.host if request.client else ORIGEM_DESCONHECIDA
    if not limite.permitir(origem):
        raise TentativasDemais


ServicosDeContaDep = Annotated[ServicosDeConta, Depends(obter_servicos_de_conta)]
BairrosOficiaisDep = Annotated[frozenset[str], Depends(obter_bairros_oficiais)]
FiltrosDep = Annotated[Filtros, Depends(obter_filtros)]
PainelDep = Annotated[RepositoriosDoPainel, Depends(obter_repositorios_do_painel)]


def auditar_consulta(
    request: Request,
    usuario: UsuarioAtualDep,
    consultas: Annotated[RegistroDeConsultas, Depends(obter_registro_de_consultas)],
    seguranca: SegurancaDep,
) -> None:
    parametros: dict[str, list[str]] = {}
    for chave, valor in request.query_params.multi_items():
        parametros.setdefault(chave, []).append(valor)
    consultas.registrar(
        ConsultaAuditada(usuario.id, request.url.path, parametros, seguranca.relogio.agora())
    )


def obter_servicos_de_encaminhamento(
    request: Request, sessao: Annotated[Session, Depends(abrir_transacao)]
) -> ServicosDeEncaminhamento:
    configuracao: Configuracao = request.app.state.configuracao
    despacho: DespachoAosOrgaos = request.app.state.despacho_aos_orgaos
    seguranca: Seguranca = request.app.state.seguranca
    return ServicosDeEncaminhamento(
        encaminhamentos=EncaminhamentoRepositorySql(sessao),
        despacho=despacho,
        relogio=seguranca.relogio,
        endereco_do_site=configuracao.endereco_do_site,
    )


ServicosDeEncaminhamentoDep = Annotated[
    ServicosDeEncaminhamento, Depends(obter_servicos_de_encaminhamento)
]


def limitar_consultas_publicas(request: Request) -> None:
    """Link de retorno e consulta pelo protocolo não têm sessão: cada origem tem um limite."""
    limite: LimiteDeEnvios = request.app.state.limite_de_consultas_publicas
    origem = request.client.host if request.client else ORIGEM_DESCONHECIDA
    if not limite.permitir(origem):
        raise TentativasDemais


def obter_servicos_de_pedidos(
    sessao: Annotated[Session, Depends(abrir_transacao)], seguranca: SegurancaDep
) -> ServicosDePedidos:
    consultar = ConsultarPedido(ConsultaDePedidosSql(sessao), EncaminhamentoRepositorySql(sessao))
    return ServicosDePedidos(consultar, PedidoAcompanhadoRepositorySql(sessao), seguranca.relogio)


ServicosDePedidosDep = Annotated[ServicosDePedidos, Depends(obter_servicos_de_pedidos)]
