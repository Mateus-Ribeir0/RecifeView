from collections.abc import Collection
from dataclasses import dataclass
from uuid import uuid4

from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.application.sessoes import SessaoAberta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import normalizar_nome
from app.domain.email import Email
from app.domain.erros import CadastroInvalido
from app.domain.senha import validar_nova_senha
from app.domain.usuario import Perfil, Usuario

EMAIL_JA_TEM_CONTA = 'Este e-mail já tem conta. Entre com a sua senha ou use "Esqueci minha senha".'


@dataclass(frozen=True)
class NovaConta:
    nome: str
    email: str
    senha: str
    bairro_oficial: str | None
    aceitou_os_termos: bool


@dataclass(frozen=True)
class CriarConta:
    """Cria a conta de cidadão e já entra nela, sem confirmação por e-mail."""

    servicos: ServicosDeConta
    bairros_oficiais: Collection[str]

    def executar(self, dados: NovaConta) -> SessaoAberta:
        email, nome = self._validar(dados)
        if self.servicos.usuarios.buscar_por_email(email) is not None:
            raise CadastroInvalido("email", EMAIL_JA_TEM_CONTA)
        usuario = Usuario(
            id=uuid4(),
            email=email,
            nome=nome,
            perfil=Perfil.CIDADAO,
            hash_da_senha=self.servicos.senhas.gerar(dados.senha),
            deve_trocar_senha=False,
            bairro_oficial=dados.bairro_oficial or None,
        )
        self.servicos.usuarios.adicionar(usuario)
        agora = self.servicos.relogio.agora()
        evento = EventoDeAcesso(TipoDeEventoDeAcesso.CONTA_CRIADA, agora, usuario.id)
        self.servicos.acessos.registrar(evento)
        return self.servicos.sessoes.abrir(usuario)

    def _validar(self, dados: NovaConta) -> tuple[Email, str]:
        if not dados.aceitou_os_termos:
            raise CadastroInvalido(
                "termos", "Para criar a conta, aceite como usamos os seus dados."
            )
        email = Email(dados.email)
        nome = normalizar_nome(dados.nome)
        validar_nova_senha(dados.senha, email)
        if dados.bairro_oficial and dados.bairro_oficial not in self.bairros_oficiais:
            raise CadastroInvalido("bairro", "Escolha um dos bairros do Recife.")
        return email, nome
