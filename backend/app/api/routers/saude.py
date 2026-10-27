from fastapi import APIRouter

roteador = APIRouter(tags=["Saúde"])


@roteador.get("/saude", summary="Confirma que a API está no ar")
def saude() -> dict[str, str]:
    return {"situacao": "ok"}
