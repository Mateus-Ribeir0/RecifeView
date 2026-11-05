from dataclasses import fields
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.application.portas.importacoes import (
    FiltroDeImportacoes,
    NovaImportacao,
    PaginaDeImportacoes,
)
from app.application.portas.relogio import Relogio
from app.domain.importacao.decisoes import Decisoes
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.infrastructure.db.modelos import ImportacaoModelo, UsuarioModelo

STATUS_EM_ANDAMENTO = (
    StatusDaImportacao.ANALISANDO,
    StatusDaImportacao.VALIDANDO,
    StatusDaImportacao.CARREGANDO,
    StatusDaImportacao.ATUALIZANDO_PAINEL,
    StatusDaImportacao.DESFAZENDO,
)
CAMPOS_ATUALIZADOS = (
    "status",
    "progresso",
    "fonte",
    "layout",
    "data_do_retrato",
    "periodo_inicio",
    "periodo_fim",
    "arquivo_guardado",
    "estrutura",
    "pendencias",
    "resultado",
    "mensagem_de_erro",
    "concluida_em",
    "desfeita_em",
)
COLUNA_DE_AUTORIA = UsuarioModelo.nome.label("nome_de_quem_importou")


def _para_entidade(modelo: ImportacaoModelo, nome_de_quem_importou: str | None) -> Importacao:
    campos: dict[str, Any] = {
        campo.name: getattr(modelo, campo.name)
        for campo in fields(Importacao)
        if hasattr(modelo, campo.name)
    }
    campos.update(
        status=StatusDaImportacao(modelo.status),
        estrutura=modelo.estrutura or {},
        pendencias=modelo.pendencias or {},
        resultado=modelo.resultado or {},
        decisoes=Decisoes.de_dicionario(modelo.decisoes),
        nome_de_quem_importou=nome_de_quem_importou,
    )
    return Importacao(**campos)


def _consulta_com_autoria() -> Any:
    return select(ImportacaoModelo, COLUNA_DE_AUTORIA).outerjoin(
        UsuarioModelo, ImportacaoModelo.usuario_id == UsuarioModelo.id
    )


class ImportacaoRepositorySql:
    """Abre uma transação curta por operação: o progresso precisa aparecer durante a carga."""

    def __init__(self, fabrica: sessionmaker[Session], relogio: Relogio) -> None:
        self._fabrica = fabrica
        self._relogio = relogio

    def criar(self, nova: NovaImportacao, status: StatusDaImportacao) -> Importacao:
        modelo = ImportacaoModelo(
            nome_do_arquivo=nova.arquivo.nome,
            tamanho_em_bytes=nova.arquivo.tamanho_em_bytes,
            hash_do_arquivo=nova.arquivo.hash_do_arquivo,
            usuario_id=nova.usuario_id,
            status=status.value,
            carga_inicial=nova.carga_inicial,
            estrutura={"referencia": nova.arquivo.referencia},
            criada_em=self._relogio.agora(),
        )
        with self._fabrica.begin() as sessao:
            sessao.add(modelo)
            sessao.flush()
            return _para_entidade(modelo, None)

    def buscar(self, importacao_id: int) -> Importacao | None:
        consulta = _consulta_com_autoria().where(ImportacaoModelo.id == importacao_id)
        with self._fabrica() as sessao:
            linha = sessao.execute(consulta).first()
            return None if linha is None else _para_entidade(linha[0], linha[1])

    def listar(self, filtro: FiltroDeImportacoes) -> PaginaDeImportacoes:
        condicoes = _condicoes(filtro)
        consulta = (
            _consulta_com_autoria()
            .where(*condicoes)
            .order_by(ImportacaoModelo.criada_em.desc(), ImportacaoModelo.id.desc())
            .limit(filtro.limite)
            .offset(filtro.deslocamento)
        )
        contagem = select(func.count()).select_from(ImportacaoModelo).where(*condicoes)
        with self._fabrica() as sessao:
            itens = [_para_entidade(*linha) for linha in sessao.execute(consulta).all()]
            total = sessao.scalar(contagem) or 0
        return PaginaDeImportacoes(itens, total)

    def salvar(self, importacao: Importacao) -> None:
        valores = {campo: getattr(importacao, campo) for campo in CAMPOS_ATUALIZADOS}
        valores["status"] = importacao.status.value
        valores["decisoes"] = importacao.decisoes.para_dicionario()
        with self._fabrica.begin() as sessao:
            sessao.execute(
                update(ImportacaoModelo)
                .where(ImportacaoModelo.id == importacao.id)
                .values(**valores)
            )

    def atualizar_progresso(
        self, importacao_id: int, status: StatusDaImportacao, progresso: int
    ) -> None:
        with self._fabrica.begin() as sessao:
            sessao.execute(
                update(ImportacaoModelo)
                .where(ImportacaoModelo.id == importacao_id)
                .values(status=status.value, progresso=progresso)
            )

    def mesmo_arquivo(self, hash_do_arquivo: str, importacao_id: int) -> list[Importacao]:
        consulta = (
            _consulta_com_autoria()
            .where(
                ImportacaoModelo.hash_do_arquivo == hash_do_arquivo,
                ImportacaoModelo.id != importacao_id,
                ImportacaoModelo.status == StatusDaImportacao.CONCLUIDA.value,
            )
            .order_by(ImportacaoModelo.criada_em.desc())
        )
        with self._fabrica() as sessao:
            return [_para_entidade(*linha) for linha in sessao.execute(consulta).all()]

    def ultima_concluida(self) -> Importacao | None:
        consulta = (
            _consulta_com_autoria()
            .where(ImportacaoModelo.status == StatusDaImportacao.CONCLUIDA.value)
            .order_by(ImportacaoModelo.concluida_em.desc(), ImportacaoModelo.id.desc())
            .limit(1)
        )
        with self._fabrica() as sessao:
            linha = sessao.execute(consulta).first()
            return None if linha is None else _para_entidade(linha[0], linha[1])

    def em_andamento(self) -> list[Importacao]:
        status = [item.value for item in STATUS_EM_ANDAMENTO]
        consulta = _consulta_com_autoria().where(ImportacaoModelo.status.in_(status))
        with self._fabrica() as sessao:
            return [_para_entidade(*linha) for linha in sessao.execute(consulta).all()]


def _condicoes(filtro: FiltroDeImportacoes) -> list[Any]:
    condicoes: list[Any] = []
    if filtro.busca:
        condicoes.append(
            or_(
                ImportacaoModelo.nome_do_arquivo.ilike(f"%{filtro.busca}%"),
                ImportacaoModelo.fonte.ilike(f"%{filtro.busca}%"),
            )
        )
    if filtro.status:
        condicoes.append(ImportacaoModelo.status == filtro.status)
    if filtro.fonte:
        condicoes.append(ImportacaoModelo.fonte == filtro.fonte)
    return condicoes
