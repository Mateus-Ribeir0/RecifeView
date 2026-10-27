from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def criar_fabrica_de_sessoes(url_do_banco: str) -> sessionmaker[Session]:
    motor = create_engine(url_do_banco, pool_pre_ping=True)
    return sessionmaker(motor, expire_on_commit=False)
