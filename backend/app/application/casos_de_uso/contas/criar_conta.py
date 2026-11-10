from collections.abc import Collection
from dataclasses import dataclass
from uuid import uuid4

from app.application.casos_de_uso.contas.codigos import CodigosDeConta
from app.application.casos_de_uso.contas.mensagens import aviso_de_conta_existente
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import FinalidadeDoCodigo, normalizar_nome
from app.domain.email import Email
from app.domain.erros import CadastroInvalido
from app.domain.senha import validar_nova_senha
from app.domain.usuario import Perfil, Usuario


@dataclass(frozen=True)
class NovaConta:
    nome: str
    email: str
    senha: str
    bairro_oficial: str | None
    aceitou_os_termos: bool


@dataclass(frozen=True)
class CriarConta:
    """Responde igual para e-mail novo e e-mail já usado: a tela não revela quem tem conta."""

    servicos: ServicosDeConta
    bairros_oficiais: Collection[str]

    def executar(self, dados: NovaConta) -> None:
        email, nome = self._validar(dados)
        hash_da_senha = self.servicos.senhas.gerar(dados.senha)
        existente = self.servicos.usuarios.buscar_por_email(email)
        if existente is None:
            self._criar(email, nome, hash_da_senha, dados.bairro_oficial)
        elif existente.precisa_confirmar_email:
            self._substituir_cadastro_pendente(existente, nome, hash_da_senha, dados)
        else:
            self.servicos.emails.enviar(aviso_de_conta_existente(str(email)))

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

    def _criar(self, email: Email, nome: str, hash_da_senha: str, bairro: str | None) -> None:
        usuario = Usuario(
            id=uuid4(),
            email=email,
            nome=nome,
            perfil=Perfil.CIDADAO,
            hash_da_senha=hash_da_senha,
            deve_trocar_senha=False,
            bairro_oficial=bairro or None,
        )
        self.servicos.usuarios.adicionar(usuario)
        agora = self.servicos.relogio.agora()
        evento = EventoDeAcesso(TipoDeEventoDeAcesso.CONTA_CRIADA, agora, usuario.id)
        self.servicos.acessos.registrar(evento)
        CodigosDeConta(self.servicos).emitir(usuario, FinalidadeDoCodigo.CONFIRMAR_EMAIL)

    def _substituir_cadastro_pendente(
        self, pendente: Usuario, nome: str, hash_da_senha: str, dados: NovaConta
    ) -> None:
        """Vale o último cadastro: a confirmação exige a senha dele, então quem cadastrou
        o e-mail de outra pessoa não consegue entrar quando ela confirmar."""
        atualizado = pendente.com_dados_pessoais(nome, dados.bairro_oficial or None)
        self.servicos.usuarios.atualizar(atualizado.com_nova_senha(hash_da_senha))
        CodigosDeConta(self.servicos).emitir(atualizado, FinalidadeDoCodigo.CONFIRMAR_EMAIL)
