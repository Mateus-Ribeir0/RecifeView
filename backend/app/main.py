from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencias import Seguranca
from app.api.erros import registrar_tratadores_de_erro
from app.api.routers import autenticacao, saude
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.db.conexao import criar_fabrica_de_sessoes
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.settings import Configuracao, carregar_configuracao

PREFIXO_DA_API = "/api/v1"


def criar_aplicacao(configuracao: Configuracao | None = None) -> FastAPI:
    configuracao = configuracao or carregar_configuracao()
    app = FastAPI(
        title="RecifeView API",
        version="0.1.0",
        description="Acesso dos gestores e indicadores do painel RecifeView.",
        docs_url=f"{PREFIXO_DA_API}/docs",
        openapi_url=f"{PREFIXO_DA_API}/openapi.json",
        redoc_url=None,
    )
    app.state.configuracao = configuracao
    app.state.fabrica_de_sessoes = criar_fabrica_de_sessoes(configuracao.url_do_banco)
    app.state.seguranca = _montar_seguranca(configuracao)
    _liberar_origens(app, configuracao.origens_permitidas)
    registrar_tratadores_de_erro(app)
    app.include_router(saude.roteador, prefix=PREFIXO_DA_API)
    app.include_router(autenticacao.roteador, prefix=PREFIXO_DA_API)
    return app


def _montar_seguranca(configuracao: Configuracao) -> Seguranca:
    return Seguranca(
        senhas=HashDeSenhaArgon2(),
        emissor=EmissorDeTokenJwt(
            configuracao.segredo_jwt.get_secret_value(),
            timedelta(minutes=configuracao.minutos_do_token_de_acesso),
        ),
        relogio=RelogioDoSistema(),
        duracao_da_sessao=timedelta(hours=configuracao.horas_da_sessao),
    )


def _liberar_origens(app: FastAPI, origens: list[str]) -> None:
    if not origens:
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
