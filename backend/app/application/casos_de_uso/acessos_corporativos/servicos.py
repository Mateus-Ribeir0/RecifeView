import secrets
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.casos_de_uso.acessos_corporativos.mensagens import mensagem_de_convite
from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.acessos_corporativos import (
    AcessosCorporativosRepository,
    ConviteRepository,
)
from app.application.portas.contas import EnvioDeEmail
from app.application.portas.relogio import Relogio
from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.sessoes import GestaoDeSessoes, calcular_hash_do_token
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.acesso_corporativo import (
    CAMINHO_DO_CONVITE,
    VALIDADE_DO_CONVITE,
    AcessoCorporativo,
    ConviteDeAcesso,
)
from app.domain.erros import AcaoSoDaAdministracao, AcessoCorporativoNaoEncontrado
from app.domain.usuario import Usuario

BYTES_DO_TOKEN_DO_CONVITE = 32
BYTES_DA_SENHA_INUTIL = 32


def exigir_administracao(usuario: Usuario) -> None:
    if not usuario.e_da_administracao:
        raise AcaoSoDaAdministracao


@dataclass(frozen=True)
class ServicosDeAcessosCorporativos:
    usuarios: UsuarioRepository
    convites: ConviteRepository
    acessos: AcessosCorporativosRepository
    senhas: HashDeSenha
    emails: EnvioDeEmail
    registro: RegistroDeAcessos
    sessoes: GestaoDeSessoes
    relogio: Relogio
    endereco_do_site: str

    def obter_conta(self, usuario_id: UUID) -> Usuario:
        usuario = self.usuarios.buscar_por_id(usuario_id)
        if usuario is None or not usuario.e_corporativo or usuario.foi_excluido:
            raise AcessoCorporativoNaoEncontrado
        return usuario

    def obter_acesso(self, usuario_id: UUID) -> AcessoCorporativo:
        acesso = self.acessos.buscar(usuario_id)
        if acesso is None:
            raise AcessoCorporativoNaoEncontrado
        return acesso

    def gerar_hash_inutil(self) -> str:
        """Uma senha que ninguém conhece: a conta só abre depois do convite aceito."""
        return self.senhas.gerar(secrets.token_urlsafe(BYTES_DA_SENHA_INUTIL))

    def convidar(self, usuario: Usuario, convidado_por: UUID) -> None:
        """Um convite novo encerra o anterior. Se o e-mail falhar, a transação desfaz tudo."""
        agora = self.relogio.agora()
        valor = secrets.token_urlsafe(BYTES_DO_TOKEN_DO_CONVITE)
        convite = ConviteDeAcesso(
            uuid4(), usuario.id, calcular_hash_do_token(valor), agora, agora + VALIDADE_DO_CONVITE
        )
        self.convites.encerrar_os_abertos(usuario.id, agora)
        self.convites.adicionar(convite, convidado_por)
        link = f"{self.endereco_do_site.rstrip('/')}{CAMINHO_DO_CONVITE}{valor}"
        self.emails.enviar(mensagem_de_convite(usuario, link, convite.expira_em))
        self.registrar(TipoDeEventoDeAcesso.CONVITE_ENVIADO, usuario.id)

    def registrar(self, tipo: TipoDeEventoDeAcesso, usuario_id: UUID) -> None:
        self.registro.registrar(EventoDeAcesso(tipo, self.relogio.agora(), usuario_id))
