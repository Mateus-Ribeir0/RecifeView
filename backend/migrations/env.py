from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.infrastructure.db import modelos  # noqa: F401
from app.infrastructure.db.base import Base
from app.infrastructure.settings import carregar_configuracao_do_banco

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)


def executar_migracoes() -> None:
    motor = create_engine(carregar_configuracao_do_banco().url_do_banco)
    with motor.connect() as conexao:
        context.configure(
            connection=conexao,
            target_metadata=Base.metadata,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()


executar_migracoes()
