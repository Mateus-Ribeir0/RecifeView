import secrets
from collections.abc import Collection
from dataclasses import dataclass

from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import normalizar_nome
from app.domain.email import Email
from app.domain.erros import AcessoNegado, CadastroInvalido, SenhaAtualIncorreta
from app.domain.usuario import Usuario

DOMINIO_DAS_CONTAS_EXCLUIDAS = "contas-excluidas.invalid"
BYTES_DA_SENHA_INUTIL = 32


@dataclass(frozen=True)
class AtualizarMinhaConta:
    servicos: ServicosDeConta
    bairros_oficiais: Collection[str]

    def executar(self, usuario: Usuario, nome: str, bairro_oficial: str | None) -> Usuario:
        if bairro_oficial and bairro_oficial not in self.bairros_oficiais:
            raise CadastroInvalido("bairro", "Escolha um dos bairros do Recife.")
        atualizado = usuario.com_dados_pessoais(normalizar_nome(nome), bairro_oficial or None)
        self.servicos.usuarios.atualizar(atualizado)
        return atualizado


@dataclass(frozen=True)
class DefinirAvisos:
    """Avisos por e-mail do andamento de pedidos, relatos e encaminhamentos (ADR 0011)."""

    servicos: ServicosDeConta

    def executar(self, usuario: Usuario, recebe_avisos: bool) -> Usuario:
        atualizado = usuario.com_avisos(recebe_avisos)
        self.servicos.usuarios.atualizar(atualizado)
        return atualizado


@dataclass(frozen=True)
class ExcluirMinhaConta:
    """Apaga o que identifica a pessoa e mantém a linha, porque a auditoria aponta para ela.

    Os protocolos guardados também saem: ligados à conta, diriam de quem é cada pedido.
    """

    servicos: ServicosDeConta

    def executar(self, usuario: Usuario, senha: str) -> None:
        if usuario.e_da_gestao:
            raise AcessoNegado
        if not self.servicos.senhas.confere(senha, usuario.hash_da_senha):
            raise SenhaAtualIncorreta
        email_anonimo = Email(f"conta-{usuario.id.hex}@{DOMINIO_DAS_CONTAS_EXCLUIDAS}")
        hash_inutil = self.servicos.senhas.gerar(secrets.token_urlsafe(BYTES_DA_SENHA_INUTIL))
        self.servicos.usuarios.atualizar(usuario.excluido(email_anonimo, hash_inutil))
        self.servicos.pedidos.remover_todos(usuario.id)
        self.servicos.sessoes.encerrar_todas(usuario.id)
        agora = self.servicos.relogio.agora()
        evento = EventoDeAcesso(TipoDeEventoDeAcesso.CONTA_EXCLUIDA, agora, usuario.id)
        self.servicos.acessos.registrar(evento)
