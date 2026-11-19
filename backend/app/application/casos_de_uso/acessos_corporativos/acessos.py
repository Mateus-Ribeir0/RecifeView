from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
    exigir_administracao,
)
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.acesso_corporativo import AcessoCorporativo
from app.domain.conta import normalizar_nome
from app.domain.email import Email
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import AcessoDesativado, ConviteJaAceito, EmailJaCadastrado
from app.domain.usuario import Perfil, Usuario, email_da_conta_excluida


@dataclass(frozen=True)
class DadosDoAcesso:
    nome: str
    orgao: Orgao


@dataclass(frozen=True)
class NovoAcesso:
    email: str
    dados: DadosDoAcesso


@dataclass(frozen=True)
class ListarAcessosCorporativos:
    servicos: ServicosDeAcessosCorporativos

    def executar(self) -> list[AcessoCorporativo]:
        return self.servicos.acessos.listar()


@dataclass(frozen=True)
class CriarAcessoCorporativo:
    servicos: ServicosDeAcessosCorporativos

    def executar(self, novo: NovoAcesso, administrador: Usuario) -> AcessoCorporativo:
        exigir_administracao(administrador)
        email = Email(novo.email)
        if self.servicos.usuarios.buscar_por_email(email) is not None:
            raise EmailJaCadastrado
        usuario = Usuario(
            id=uuid4(),
            email=email,
            nome=normalizar_nome(novo.dados.nome),
            perfil=Perfil.CORPORATIVO,
            hash_da_senha=self.servicos.gerar_hash_inutil(),
            deve_trocar_senha=False,
            orgao=novo.dados.orgao,
        )
        self.servicos.usuarios.adicionar(usuario)
        self.servicos.registrar(TipoDeEventoDeAcesso.CONTA_CRIADA, usuario.id)
        self.servicos.convidar(usuario, administrador.id)
        return self.servicos.obter_acesso(usuario.id)


@dataclass(frozen=True)
class EditarAcessoCorporativo:
    servicos: ServicosDeAcessosCorporativos

    def executar(
        self, usuario_id: UUID, dados: DadosDoAcesso, administrador: Usuario
    ) -> AcessoCorporativo:
        exigir_administracao(administrador)
        usuario = self.servicos.obter_conta(usuario_id)
        alterado = usuario.com_dados_do_acesso(normalizar_nome(dados.nome), dados.orgao)
        self.servicos.usuarios.atualizar(alterado)
        self.servicos.registrar(TipoDeEventoDeAcesso.CONTA_ALTERADA, usuario_id)
        return self.servicos.obter_acesso(usuario_id)


@dataclass(frozen=True)
class ReenviarConvite:
    servicos: ServicosDeAcessosCorporativos

    def executar(self, usuario_id: UUID, administrador: Usuario) -> AcessoCorporativo:
        exigir_administracao(administrador)
        usuario = self.servicos.obter_conta(usuario_id)
        if not usuario.ativo:
            raise AcessoDesativado
        if self.servicos.obter_acesso(usuario_id).convite_aceito:
            raise ConviteJaAceito
        self.servicos.convidar(usuario, administrador.id)
        return self.servicos.obter_acesso(usuario_id)


@dataclass(frozen=True)
class DesativarAcesso:
    """A sessão aberta cai na hora: a conta desativada não passa da identificação."""

    servicos: ServicosDeAcessosCorporativos

    def executar(self, usuario_id: UUID, administrador: Usuario) -> AcessoCorporativo:
        exigir_administracao(administrador)
        usuario = self.servicos.obter_conta(usuario_id)
        self.servicos.usuarios.atualizar(usuario.desativado())
        self.servicos.sessoes.encerrar_todas(usuario_id)
        self.servicos.convites.encerrar_os_abertos(usuario_id, self.servicos.relogio.agora())
        self.servicos.registrar(TipoDeEventoDeAcesso.CONTA_DESATIVADA, usuario_id)
        return self.servicos.obter_acesso(usuario_id)


@dataclass(frozen=True)
class ReativarAcesso:
    servicos: ServicosDeAcessosCorporativos

    def executar(self, usuario_id: UUID, administrador: Usuario) -> AcessoCorporativo:
        exigir_administracao(administrador)
        usuario = self.servicos.obter_conta(usuario_id)
        self.servicos.usuarios.atualizar(usuario.reativado())
        self.servicos.registrar(TipoDeEventoDeAcesso.CONTA_REATIVADA, usuario_id)
        return self.servicos.obter_acesso(usuario_id)


@dataclass(frozen=True)
class ExcluirAcesso:
    """Como na exclusão da conta de cidadão: sai o que identifica a pessoa, fica a auditoria."""

    servicos: ServicosDeAcessosCorporativos

    def executar(self, usuario_id: UUID, administrador: Usuario) -> None:
        exigir_administracao(administrador)
        usuario = self.servicos.obter_conta(usuario_id)
        anonima = usuario.excluido(
            email_da_conta_excluida(usuario_id), self.servicos.gerar_hash_inutil()
        )
        self.servicos.usuarios.atualizar(anonima)
        self.servicos.sessoes.encerrar_todas(usuario_id)
        self.servicos.convites.encerrar_os_abertos(usuario_id, self.servicos.relogio.agora())
        self.servicos.registrar(TipoDeEventoDeAcesso.CONTA_EXCLUIDA, usuario_id)
