from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

ESQUEMA_DA_APLICACAO = "app"


class Base(DeclarativeBase):
    metadata = MetaData(schema=ESQUEMA_DA_APLICACAO)
