from dataclasses import dataclass

from app.application.casos_de_uso.contas.codigos import CodigosDeConta
from app.application.casos_de_uso.contas.confirmar_email import buscar_por_texto_de_email
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import FinalidadeDoCodigo
from app.domain.erros import CodigoInvalido
from app.domain.senha import validar_nova_senha
from app.domain.usuario import Usuario


def _pode_recuperar_sozinho(usuario: Usuario | None) -> bool:
    """Conta da gestão volta pela administração, como diz a ADR 0005."""
    return (
        usuario is not None
        and usuario.ativo
        and not usuario.e_da_gestao
        and not usuario.precisa_confirmar_email
    )


@dataclass(frozen=True)
class PedirNovaSenha:
    servicos: ServicosDeConta

    def executar(self, email: str) -> None:
        usuario = buscar_por_texto_de_email(self.servicos, email)
        if usuario is not None and _pode_recuperar_sozinho(usuario):
            CodigosDeConta(self.servicos).emitir(usuario, FinalidadeDoCodigo.REDEFINIR_SENHA)


@dataclass(frozen=True)
class NovaSenhaComCodigo:
    email: str
    codigo: str
    nova_senha: str


@dataclass(frozen=True)
class CriarNovaSenha:
    servicos: ServicosDeConta

    def executar(self, pedido: NovaSenhaComCodigo) -> None:
        usuario = buscar_por_texto_de_email(self.servicos, pedido.email)
        if usuario is None or not _pode_recuperar_sozinho(usuario):
            raise CodigoInvalido
        CodigosDeConta(self.servicos).conferir(
            usuario, FinalidadeDoCodigo.REDEFINIR_SENHA, pedido.codigo
        )
        validar_nova_senha(pedido.nova_senha, usuario.email)
        self.servicos.usuarios.atualizar(
            usuario.com_nova_senha(self.servicos.senhas.gerar(pedido.nova_senha))
        )
        self.servicos.sessoes.encerrar_todas(usuario.id)
        agora = self.servicos.relogio.agora()
        evento = EventoDeAcesso(TipoDeEventoDeAcesso.SENHA_RECUPERADA, agora, usuario.id)
        self.servicos.acessos.registrar(evento)
