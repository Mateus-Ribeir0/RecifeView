import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencias import Seguranca
from app.api.erros import registrar_tratadores_de_erro
from app.api.routers import autenticacao, cidade, contas, contribuicoes, importacoes, painel, saude
from app.application.casos_de_uso.contribuicoes.expurgar_enderecos import ExpurgarEnderecos
from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.casos_de_uso.importacoes.retomar_importacoes import RetomarImportacoes
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.contribuicoes.limite_em_memoria import LimiteEmMemoria
from app.infrastructure.db.conexao import criar_fabrica_de_sessoes
from app.infrastructure.email.caixa_de_saida_local import CaixaDeSaidaLocal
from app.infrastructure.importacao.fila_em_processo import FilaEmProcesso
from app.infrastructure.importacao.montagem import (
    montar_servicos_de_contribuicoes,
    montar_servicos_de_importacao,
)
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.settings import Configuracao, carregar_configuracao

PREFIXO_DA_API = "/api/v1"
SEGUNDOS_ENTRE_EXPURGOS = 6 * 60 * 60
OPERACOES_DE_CONTA_POR_JANELA = 10

registro_de_log = logging.getLogger(__name__)


async def _expurgar_sempre(servicos: ServicosDeContribuicoes) -> None:
    """O prazo de guarda é uma promessa ao público: não pode depender de alguém gerar pacote."""
    expurgar = ExpurgarEnderecos(servicos.contribuicoes, servicos.relogio)
    while True:
        try:
            await asyncio.to_thread(expurgar.executar)
        except Exception:
            registro_de_log.exception("Falha ao apagar endereços vencidos")
        await asyncio.sleep(SEGUNDOS_ENTRE_EXPURGOS)


@asynccontextmanager
async def _ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    RetomarImportacoes(app.state.servicos_de_importacao).executar()
    expurgo = asyncio.create_task(_expurgar_sempre(app.state.servicos_de_contribuicoes))
    yield
    expurgo.cancel()


def criar_aplicacao(configuracao: Configuracao | None = None) -> FastAPI:
    configuracao = configuracao or carregar_configuracao()
    app = FastAPI(
        title="RecifeView API",
        version="0.1.0",
        description="Acesso dos gestores e indicadores do painel RecifeView.",
        docs_url=f"{PREFIXO_DA_API}/docs",
        openapi_url=f"{PREFIXO_DA_API}/openapi.json",
        redoc_url=None,
        lifespan=_ciclo_de_vida,
    )
    app.state.configuracao = configuracao
    app.state.fabrica_de_sessoes = criar_fabrica_de_sessoes(configuracao.url_do_banco)
    app.state.seguranca = _montar_seguranca(configuracao)
    app.state.caixa_de_emails = CaixaDeSaidaLocal(configuracao.pasta_dos_emails)
    app.state.limite_de_contas = LimiteEmMemoria(RelogioDoSistema(), OPERACOES_DE_CONTA_POR_JANELA)
    app.state.servicos_de_importacao = montar_servicos_de_importacao(
        configuracao, app.state.fabrica_de_sessoes, FilaEmProcesso()
    )
    app.state.servicos_de_contribuicoes = montar_servicos_de_contribuicoes(
        app.state.fabrica_de_sessoes, app.state.servicos_de_importacao
    )
    _liberar_origens(app, configuracao.origens_permitidas)
    registrar_tratadores_de_erro(app)
    app.include_router(saude.roteador, prefix=PREFIXO_DA_API)
    app.include_router(autenticacao.roteador, prefix=PREFIXO_DA_API)
    app.include_router(contas.roteador, prefix=PREFIXO_DA_API)
    app.include_router(cidade.roteador, prefix=PREFIXO_DA_API)
    app.include_router(importacoes.roteador, prefix=PREFIXO_DA_API)
    app.include_router(contribuicoes.roteador, prefix=PREFIXO_DA_API)
    for roteador in painel.ROTEADORES:
        app.include_router(roteador, prefix=PREFIXO_DA_API)
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
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type"],
    )
