from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class UsuarioModelo(Base):
    __tablename__ = "usuario"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    nome: Mapped[str] = mapped_column(String(200))
    perfil: Mapped[str] = mapped_column(String(30))
    hash_da_senha: Mapped[str] = mapped_column(String(255))
    ativo: Mapped[bool]
    deve_trocar_senha: Mapped[bool]
    tentativas_falhas: Mapped[int]
    bloqueado_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SessaoModelo(Base):
    __tablename__ = "sessao"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey(UsuarioModelo.id), index=True)
    hash_do_token: Mapped[str] = mapped_column(String(64), unique=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revogada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EventoDeAcessoModelo(Base):
    __tablename__ = "evento_de_acesso"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey(UsuarioModelo.id), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
