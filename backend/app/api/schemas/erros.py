from typing import Any

from pydantic import BaseModel


class DetalheDoErro(BaseModel):
    codigo: str
    mensagem: str
    detalhes: dict[str, Any] | None = None


class ErroResposta(BaseModel):
    erro: DetalheDoErro
