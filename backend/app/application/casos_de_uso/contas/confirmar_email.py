from dataclasses import dataclass

from app.application.casos_de_uso.contas.codigos import CodigosDeConta
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.application.sessoes import SessaoAberta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import FinalidadeDoCodigo
from app.domain.email import Email
from app.domain.erros import CodigoInvalido, EmailInvalido
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class ConfirmacaoDeEmail:
    email: str
    codigo: str
    senha: str


@dataclass(frozen=True)
class ConfirmarEmail:
    """Confirma com código e senha juntos, e já entra na conta."""

    servicos: ServicosDeConta

    def executar(self, confirmacao: ConfirmacaoDeEmail) -> SessaoAberta:
        usuario = self._buscar_pendente(confirmacao)
        CodigosDeConta(self.servicos).conferir(
            usuario, FinalidadeDoCodigo.CONFIRMAR_EMAIL, confirmacao.codigo
        )
        agora = self.servicos.relogio.agora()
        confirmado = usuario.com_email_confirmado(agora)
        self.servicos.usuarios.atualizar(confirmado)
        evento = EventoDeAcesso(TipoDeEventoDeAcesso.EMAIL_CONFIRMADO, agora, usuario.id)
        self.servicos.acessos.registrar(evento)
        return self.servicos.sessoes.abrir(confirmado)

    def _buscar_pendente(self, confirmacao: ConfirmacaoDeEmail) -> Usuario:
        usuario = buscar_por_texto_de_email(self.servicos, confirmacao.email)
        if usuario is None or not usuario.precisa_confirmar_email:
            self.servicos.senhas.simular_conferencia(confirmacao.senha)
            raise CodigoInvalido
        if not self.servicos.senhas.confere(confirmacao.senha, usuario.hash_da_senha):
            raise CodigoInvalido
        return usuario


def buscar_por_texto_de_email(servicos: ServicosDeConta, email: str) -> Usuario | None:
    try:
        return servicos.usuarios.buscar_por_email(Email(email))
    except EmailInvalido:
        return None
