from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
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
