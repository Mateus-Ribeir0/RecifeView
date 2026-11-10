import re
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.application.portas.contas import MensagemDeEmail
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import CodigoDeConta, FinalidadeDoCodigo
from app.domain.email import Email
from app.domain.sessao import Sessao
from app.domain.usuario import Perfil, Usuario

INICIO_DOS_TESTES = datetime(2026, 10, 26, 12, 0, tzinfo=UTC)
SENHA_DE_TESTE = "senha-correta-123"


class RelogioFixo:
    def __init__(self, inicio: datetime = INICIO_DOS_TESTES) -> None:
        self.momento = inicio

    def agora(self) -> datetime:
        return self.momento

    def avancar(self, intervalo: timedelta) -> None:
        self.momento += intervalo


class HashDeSenhaDeTeste:
    def __init__(self) -> None:
        self.conferencias_simuladas = 0

    def gerar(self, senha: str) -> str:
        return f"hash:{senha}"

    def confere(self, senha: str, hash_da_senha: str) -> bool:
        return hash_da_senha == self.gerar(senha)

    def simular_conferencia(self, senha: str) -> None:
        self.conferencias_simuladas += 1


class UsuariosEmMemoria:
    def __init__(self, *usuarios: Usuario) -> None:
        self.por_id: dict[UUID, Usuario] = {usuario.id: usuario for usuario in usuarios}

    def buscar_por_email(self, email: Email) -> Usuario | None:
        return next((u for u in self.por_id.values() if u.email == email), None)

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self.por_id.get(usuario_id)

    def adicionar(self, usuario: Usuario) -> None:
        self.por_id[usuario.id] = usuario

    def atualizar(self, usuario: Usuario) -> None:
        self.por_id[usuario.id] = usuario


class SessoesEmMemoria:
    def __init__(self) -> None:
        self.por_id: dict[UUID, Sessao] = {}

    def adicionar(self, sessao: Sessao) -> None:
        self.por_id[sessao.id] = sessao

    def buscar_por_hash_do_token(self, hash_do_token: str) -> Sessao | None:
        return next((s for s in self.por_id.values() if s.hash_do_token == hash_do_token), None)

    def atualizar(self, sessao: Sessao) -> None:
        self.por_id[sessao.id] = sessao

    def revogar_todas_do_usuario(self, usuario_id: UUID, agora: datetime) -> None:
        for sessao in list(self.por_id.values()):
            if sessao.usuario_id == usuario_id and sessao.revogada_em is None:
                self.por_id[sessao.id] = sessao.revogada(agora)

    def ativas(self) -> list[Sessao]:
        return [s for s in self.por_id.values() if s.revogada_em is None]


class AcessosEmMemoria:
    def __init__(self) -> None:
        self.eventos: list[EventoDeAcesso] = []

    def registrar(self, evento: EventoDeAcesso) -> None:
        self.eventos.append(evento)

    def tipos(self) -> list[TipoDeEventoDeAcesso]:
        return [evento.tipo for evento in self.eventos]


def criar_usuario(**alteracoes: object) -> Usuario:
    usuario = Usuario(
        id=uuid4(),
        email=Email("gestora@recife.pe.gov.br"),
        nome="Gestora de Teste",
        perfil=Perfil.GESTOR,
        hash_da_senha=HashDeSenhaDeTeste().gerar(SENHA_DE_TESTE),
        deve_trocar_senha=False,
    )
    return replace(usuario, **alteracoes)  # type: ignore[arg-type]


class CodigosEmMemoria:
    def __init__(self) -> None:
        self.codigos: dict[UUID, CodigoDeConta] = {}

    def adicionar(self, codigo: CodigoDeConta) -> None:
        self.codigos[codigo.id] = codigo

    def ultimo(self, usuario_id: UUID, finalidade: FinalidadeDoCodigo) -> CodigoDeConta | None:
        do_usuario = [
            codigo
            for codigo in self.codigos.values()
            if codigo.usuario_id == usuario_id and codigo.finalidade is finalidade
        ]
        return max(do_usuario, key=lambda codigo: codigo.criado_em, default=None)

    def atualizar(self, codigo: CodigoDeConta) -> None:
        self.codigos[codigo.id] = codigo

    def invalidar_abertos(
        self, usuario_id: UUID, finalidade: FinalidadeDoCodigo, agora: datetime
    ) -> None:
        for codigo in list(self.codigos.values()):
            aberto = codigo.usado_em is None and codigo.finalidade is finalidade
            if codigo.usuario_id == usuario_id and aberto:
                self.codigos[codigo.id] = codigo.usado(agora)


class CaixaDeEmailsEmMemoria:
    def __init__(self) -> None:
        self.mensagens: list[MensagemDeEmail] = []

    def enviar(self, mensagem: MensagemDeEmail) -> None:
        self.mensagens.append(mensagem)

    def ultimo_codigo(self) -> str:
        achado = re.search(r"\b(\d{3}) (\d{3})\b", self.mensagens[-1].corpo)
        assert achado is not None
        return achado.group(1) + achado.group(2)
