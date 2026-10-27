from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.email import Email
from app.domain.erros import UsuarioNaoEncontrado
from app.domain.usuario import Perfil, Usuario
from app.infrastructure.db.modelos import UsuarioModelo


class UsuarioRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def buscar_por_email(self, email: Email) -> Usuario | None:
        consulta = select(UsuarioModelo).where(UsuarioModelo.email == str(email))
        modelo = self._sessao.scalar(consulta)
        return _para_dominio(modelo) if modelo else None

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        modelo = self._sessao.get(UsuarioModelo, usuario_id)
        return _para_dominio(modelo) if modelo else None

    def adicionar(self, usuario: Usuario) -> None:
        modelo = UsuarioModelo(id=usuario.id)
        _preencher(modelo, usuario)
        self._sessao.add(modelo)
        self._sessao.flush()

    def atualizar(self, usuario: Usuario) -> None:
        modelo = self._sessao.get(UsuarioModelo, usuario.id)
        if modelo is None:
            raise UsuarioNaoEncontrado
        _preencher(modelo, usuario)
        self._sessao.flush()


def _preencher(modelo: UsuarioModelo, usuario: Usuario) -> None:
    modelo.email = str(usuario.email)
    modelo.nome = usuario.nome
    modelo.perfil = usuario.perfil.value
    modelo.hash_da_senha = usuario.hash_da_senha
    modelo.ativo = usuario.ativo
    modelo.deve_trocar_senha = usuario.deve_trocar_senha
    modelo.tentativas_falhas = usuario.tentativas_falhas
    modelo.bloqueado_ate = usuario.bloqueado_ate


def _para_dominio(modelo: UsuarioModelo) -> Usuario:
    return Usuario(
        id=modelo.id,
        email=Email(modelo.email),
        nome=modelo.nome,
        perfil=Perfil(modelo.perfil),
        hash_da_senha=modelo.hash_da_senha,
        ativo=modelo.ativo,
        deve_trocar_senha=modelo.deve_trocar_senha,
        tentativas_falhas=modelo.tentativas_falhas,
        bloqueado_ate=modelo.bloqueado_ate,
    )
