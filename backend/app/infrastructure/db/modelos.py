from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB
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
    bairro_oficial: Mapped[str | None] = mapped_column(Text)
    recebe_avisos: Mapped[bool] = mapped_column(default=True, server_default=true())
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


class CodigoDeContaModelo(Base):
    __tablename__ = "codigo_de_conta"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey(UsuarioModelo.id), index=True)
    finalidade: Mapped[str] = mapped_column(String(30))
    hash_do_codigo: Mapped[str] = mapped_column(String(64))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tentativas: Mapped[int] = mapped_column(SmallInteger, default=0)
    usado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EventoDeAcessoModelo(Base):
    __tablename__ = "evento_de_acesso"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey(UsuarioModelo.id), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ImportacaoModelo(Base):
    __tablename__ = "importacao"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    nome_do_arquivo: Mapped[str] = mapped_column(Text)
    tamanho_em_bytes: Mapped[int] = mapped_column(BigInteger)
    hash_do_arquivo: Mapped[str] = mapped_column(String(64), index=True)
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey(UsuarioModelo.id))
    status: Mapped[str] = mapped_column(String(30))
    progresso: Mapped[int] = mapped_column(SmallInteger, default=0)
    fonte: Mapped[str | None] = mapped_column(String(30))
    layout: Mapped[str | None] = mapped_column(String(30))
    data_do_retrato: Mapped[date | None] = mapped_column(Date)
    periodo_inicio: Mapped[date | None] = mapped_column(Date)
    periodo_fim: Mapped[date | None] = mapped_column(Date)
    carga_inicial: Mapped[bool] = mapped_column(default=False)
    arquivo_guardado: Mapped[bool] = mapped_column(default=True)
    estrutura: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    decisoes: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    pendencias: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    resultado: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    mensagem_de_erro: Mapped[str | None] = mapped_column(Text)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    desfeita_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    desfeita_por: Mapped[UUID | None] = mapped_column(ForeignKey(UsuarioModelo.id))


class ConsultaAuditadaModelo(Base):
    __tablename__ = "consulta_auditada"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey(UsuarioModelo.id))
    rota: Mapped[str] = mapped_column(Text)
    filtros: Mapped[dict[str, Any]] = mapped_column(JSONB)
    ocorrida_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
