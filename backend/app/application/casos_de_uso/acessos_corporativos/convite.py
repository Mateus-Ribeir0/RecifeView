from dataclasses import dataclass
from datetime import datetime

from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
)
from app.application.sessoes import SessaoAberta, calcular_hash_do_token
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.acesso_corporativo import ConviteDeAcesso
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import AcessoCorporativoNaoEncontrado, ConviteInvalido
from app.domain.senha import validar_nova_senha
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class ConviteAberto:
    nome: str
    email: str
    orgao: Orgao
    expira_em: datetime


@dataclass(frozen=True)
class ConviteConferido:
    convite: ConviteDeAcesso
    usuario: Usuario
    orgao: Orgao


def _conferir(servicos: ServicosDeAcessosCorporativos, token: str) -> ConviteConferido:
    convite = servicos.convites.buscar_pelo_hash(calcular_hash_do_token(token))
    if convite is None or not convite.pode_ser_usado(servicos.relogio.agora()):
        raise ConviteInvalido
    try:
        usuario = servicos.obter_conta(convite.usuario_id)
    except AcessoCorporativoNaoEncontrado as erro:
        raise ConviteInvalido from erro
    orgao = usuario.orgao
    if not usuario.ativo or orgao is None:
        raise ConviteInvalido
    return ConviteConferido(convite, usuario, orgao)


@dataclass(frozen=True)
class AbrirConvite:
    servicos: ServicosDeAcessosCorporativos

    def executar(self, token: str) -> ConviteAberto:
        conferido = _conferir(self.servicos, token)
        usuario = conferido.usuario
        return ConviteAberto(
            usuario.nome, str(usuario.email), conferido.orgao, conferido.convite.expira_em
        )


@dataclass(frozen=True)
class AceitarConvite:
    """A pessoa define a senha e já entra: o convite vale uma vez só."""

    servicos: ServicosDeAcessosCorporativos

    def executar(self, token: str, senha: str) -> SessaoAberta:
        conferido = _conferir(self.servicos, token)
        validar_nova_senha(senha, conferido.usuario.email)
        com_senha = conferido.usuario.com_nova_senha(self.servicos.senhas.gerar(senha))
        self.servicos.usuarios.atualizar(com_senha)
        self.servicos.convites.marcar_usado(conferido.convite.id, self.servicos.relogio.agora())
        self.servicos.registrar(TipoDeEventoDeAcesso.CONVITE_ACEITO, com_senha.id)
        return self.servicos.sessoes.abrir(com_senha)
