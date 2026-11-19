import re
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from uuid import UUID

from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
)
from app.application.casos_de_uso.corporativo.servicos import ServicosDoOrgao
from app.application.portas.indicadores import OpcoesDeFiltro
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.acesso_corporativo import AcessoCorporativo, ConviteDeAcesso
from app.domain.demanda_do_orgao import DemandaDoOrgao, PeriodoEmAnos
from app.domain.email import Email
from app.domain.encaminhamento.desempenho import (
    ContagemPorTema,
    IndicadoresDoOrgao,
    SemanaDoCiclo,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.usuario import Perfil, Usuario
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from tests.fakes import (
    AcessosEmMemoria,
    CaixaDeEmailsEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)
from tests.fakes_encaminhamento import Ambiente

ENDERECO_DO_SITE = "https://recifeview.exemplo"
SEGREDO_DE_TESTE = "segredo-de-teste-com-mais-de-trinta-e-dois-caracteres"
PADRAO_DO_CONVITE = re.compile(r"/convite/(\S+)")


def criar_administradora() -> Usuario:
    return criar_usuario(
        email=Email("administracao@recife.pe.gov.br"),
        nome="Administração de Teste",
        perfil=Perfil.ADMINISTRADOR,
    )


def criar_conta_do_orgao(orgao: Orgao = Orgao.COMPESA, **alteracoes: object) -> Usuario:
    return criar_usuario(
        email=Email("responsavel@compesa.exemplo"),
        nome="Responsável da Compesa",
        perfil=Perfil.CORPORATIVO,
        orgao=orgao,
        **alteracoes,
    )


class ConvitesEmMemoria:
    def __init__(self) -> None:
        self.convites: dict[UUID, ConviteDeAcesso] = {}

    def adicionar(self, convite: ConviteDeAcesso, criado_por: UUID | None) -> None:
        self.convites[convite.id] = convite

    def buscar_pelo_hash(self, hash_do_token: str) -> ConviteDeAcesso | None:
        return next(
            (item for item in self.convites.values() if item.hash_do_token == hash_do_token), None
        )

    def marcar_usado(self, convite_id: UUID, agora: datetime) -> None:
        self.convites[convite_id] = replace(self.convites[convite_id], usado_em=agora)

    def encerrar_os_abertos(self, usuario_id: UUID, agora: datetime) -> None:
        for item in list(self.convites.values()):
            if item.usuario_id == usuario_id and item.usado_em is None and item.expira_em > agora:
                self.convites[item.id] = replace(item, expira_em=agora)

    def do_usuario(self, usuario_id: UUID) -> list[ConviteDeAcesso]:
        return [item for item in self.convites.values() if item.usuario_id == usuario_id]


@dataclass
class AcessosCorporativosEmMemoria:
    usuarios: UsuariosEmMemoria
    convites: ConvitesEmMemoria

    def listar(self) -> list[AcessoCorporativo]:
        return [
            self._acesso(usuario)
            for usuario in self.usuarios.por_id.values()
            if usuario.e_corporativo and not usuario.foi_excluido and usuario.orgao
        ]

    def buscar(self, usuario_id: UUID) -> AcessoCorporativo | None:
        return next((item for item in self.listar() if item.usuario_id == usuario_id), None)

    def _acesso(self, usuario: Usuario) -> AcessoCorporativo:
        convites = self.convites.do_usuario(usuario.id)
        abertos = [item.expira_em for item in convites if item.usado_em is None]
        assert usuario.orgao is not None
        return AcessoCorporativo(
            usuario_id=usuario.id,
            nome=usuario.nome,
            email=str(usuario.email),
            orgao=usuario.orgao,
            ativo=usuario.ativo,
            criado_em=datetime(2026, 10, 1),
            convite_aceito=not convites or any(item.usado_em for item in convites),
            convite_expira_em=max(abertos, default=None),
        )


@dataclass
class AmbienteDeAcessos:
    """As portas falsas do acesso corporativo, com a administradora já cadastrada."""

    administradora: Usuario = field(default_factory=criar_administradora)
    relogio: RelogioFixo = field(default_factory=RelogioFixo)
    emails: CaixaDeEmailsEmMemoria = field(default_factory=CaixaDeEmailsEmMemoria)
    registro: AcessosEmMemoria = field(default_factory=AcessosEmMemoria)
    convites: ConvitesEmMemoria = field(default_factory=ConvitesEmMemoria)
    sessoes_guardadas: SessoesEmMemoria = field(default_factory=SessoesEmMemoria)
    senhas: HashDeSenhaDeTeste = field(default_factory=HashDeSenhaDeTeste)

    def __post_init__(self) -> None:
        self.usuarios = UsuariosEmMemoria(self.administradora)

    def servicos(self) -> ServicosDeAcessosCorporativos:
        sessoes = GestaoDeSessoes(
            self.sessoes_guardadas,
            EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15)),
            self.relogio,
        )
        return ServicosDeAcessosCorporativos(
            usuarios=self.usuarios,
            convites=self.convites,
            acessos=AcessosCorporativosEmMemoria(self.usuarios, self.convites),
            senhas=self.senhas,
            emails=self.emails,
            registro=self.registro,
            sessoes=sessoes,
            relogio=self.relogio,
            endereco_do_site=ENDERECO_DO_SITE,
        )

    def token_do_ultimo_convite(self) -> str:
        achado = PADRAO_DO_CONVITE.search(self.emails.mensagens[-1].corpo)
        assert achado is not None
        return achado.group(1)

    def eventos(self) -> list[TipoDeEventoDeAcesso]:
        return self.registro.tipos()


@dataclass
class IndicadoresEmMemoria:
    medidos: list[IndicadoresDoOrgao] = field(default_factory=list)
    opcoes: OpcoesDeFiltro = field(default_factory=OpcoesDeFiltro)

    def por_orgao(self, hoje: date, orgao: Orgao | None = None) -> list[IndicadoresDoOrgao]:
        return [item for item in self.medidos if orgao is None or item.orgao is orgao]

    def semanas(self, hoje: date, orgao: Orgao | None = None) -> list[SemanaDoCiclo]:
        return [SemanaDoCiclo(hoje, 1, 0)]

    def abertas_por_bairro(self, orgao: Orgao) -> dict[str, int]:
        return {"AFOGADOS": 1}

    def resolvidas_por_tema(self, orgao: Orgao) -> list[ContagemPorTema]:
        return []

    def pessoas_com_retorno(self, orgao: Orgao) -> int:
        return 0

    def opcoes_de_filtro(self, orgao: Orgao) -> OpcoesDeFiltro:
        return self.opcoes


@dataclass
class DemandaEmMemoria:
    pedidos: list[tuple[tuple[str, ...], PeriodoEmAnos]] = field(default_factory=list)

    def resumir(self, nomes_na_fonte: Sequence[str], periodo: PeriodoEmAnos) -> DemandaDoOrgao:
        self.pedidos.append((tuple(nomes_na_fonte), periodo))
        return DemandaDoOrgao(total=10)


def servicos_do_orgao(
    ambiente: Ambiente, indicadores: IndicadoresEmMemoria | None = None
) -> ServicosDoOrgao:
    return ServicosDoOrgao(
        encaminhamentos=ambiente.servicos(),
        indicadores=indicadores or IndicadoresEmMemoria(),
        pessoas=ambiente.destinatarios,
        demanda=DemandaEmMemoria(),
    )
