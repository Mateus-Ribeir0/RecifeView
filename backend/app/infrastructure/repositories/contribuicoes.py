from collections.abc import Iterable, Sequence
from dataclasses import asdict
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import bindparam

from app.application.portas.contribuicoes import (
    BairroDoFormulario,
    DecisaoRegistrada,
    FiltroDaCidade,
    LadoDoPar,
    OcorrenciaDaCidade,
    OcorrenciaDoPacote,
    OcorrenciaDoPainel,
    PaginaDeOcorrencias,
    ParNovo,
    ParParaRevisar,
    RelatoDoCidadao,
    ResumoDasContribuicoes,
)
from app.application.portas.importacoes import RegistroNoMesmoLocal
from app.domain.contribuicao.catalogo import SERVICOS_POR_CODIGO
from app.domain.contribuicao.comparacao import Relato
from app.domain.contribuicao.conferencia import RelatoGuardado
from app.domain.contribuicao.contribuicao import (
    Contribuicao,
    DecisaoDoPar,
    ResultadoDoEnvio,
    RetornoAnterior,
)
from app.domain.fontes import Fonte

COLUNAS = """
    id, chave_de_envio, recebida_em, data_relato, categoria, servico_codigo, servico,
    bairro_oficial, logradouro, numero, detalhe, id_local, numero_informado, retorno, resultado,
    principal_id, usuario_id
"""
INSERIR = """
INSERT INTO app.contribuicao (
    id, chave_de_envio, recebida_em, data_relato, categoria, servico_codigo, servico,
    bairro_oficial, logradouro, numero, detalhe, id_local, numero_informado, retorno, resultado,
    principal_id, usuario_id
) VALUES (
    :id, :chave_de_envio, :recebida_em, :data_relato, :categoria, :servico_codigo, :servico,
    :bairro_oficial, :logradouro, :numero, :detalhe, :id_local, :numero_informado, :retorno,
    :resultado, :principal_id, :usuario_id
)
ON CONFLICT (chave_de_envio) DO NOTHING
"""
INSERIR_PAR = """
INSERT INTO app.par_de_contribuicoes (primeira_id, segunda_id, pontuacao, motivos)
VALUES (:primeira_id, :segunda_id, :pontuacao, :motivos)
ON CONFLICT (primeira_id, segunda_id) DO NOTHING
"""

# Derivada do estado da importação: cancelar ou desfazer devolve o relato à fila sem mais código.
SITUACAO = """
CASE
    WHEN c.principal_id IS NOT NULL THEN 'somada'
    WHEN retirada.status IN ('CONCLUIDA', 'ATUALIZANDO_PAINEL', 'CARREGANDO') THEN 'retirada'
    WHEN pacote.status = 'CONCLUIDA' THEN 'na_base'
    WHEN pacote.status IS NULL OR pacote.status IN ('CANCELADA', 'DESFEITA') THEN 'aberta'
    ELSE 'em_pacote'
END
"""
COM_SITUACAO = f"""
WITH situacoes AS (
    SELECT c.*, {SITUACAO} AS situacao
    FROM app.contribuicao c
    LEFT JOIN app.importacao pacote ON pacote.id = c.importacao_id
    LEFT JOIN app.importacao retirada ON retirada.id = c.retirada_por
)
"""
RESUMIR = f"""
{COM_SITUACAO}
SELECT
    count(*),
    count(*) FILTER (WHERE principal_id IS NULL),
    count(*) FILTER (WHERE principal_id IS NOT NULL),
    (SELECT count(*) FROM app.par_de_contribuicoes WHERE decisao IS NULL),
    count(*) FILTER (WHERE situacao = 'aberta'),
    count(*) FILTER (WHERE situacao = 'em_pacote'),
    count(*) FILTER (WHERE situacao = 'na_base'),
    count(*) FILTER (WHERE situacao = 'retirada'),
    count(*) FILTER (WHERE retorno = 'registrou_sem_retorno')
FROM situacoes
"""
LISTAR_OCORRENCIAS = f"""
{COM_SITUACAO}
SELECT
    s.id, s.recebida_em, s.servico_codigo, s.servico, b.nome, s.logradouro, s.numero,
    1 + count(f.id), count(*) FILTER (
        WHERE coalesce(f.retorno, s.retorno) = 'registrou_sem_retorno'
    ), s.situacao
FROM situacoes s
JOIN ouro.dim_bairro b USING (bairro_oficial)
LEFT JOIN app.contribuicao f ON f.principal_id = s.id
WHERE s.principal_id IS NULL
GROUP BY s.id, s.recebida_em, s.servico_codigo, s.servico, b.nome, s.logradouro, s.numero,
    s.situacao
ORDER BY s.recebida_em DESC
LIMIT :limite OFFSET :deslocamento
"""
CONTAR_OCORRENCIAS = "SELECT count(*) FROM app.contribuicao WHERE principal_id IS NULL"
LADO_DO_PAR = """
    c.id, c.recebida_em, c.servico_codigo, c.servico, b.nome, c.logradouro, c.numero, c.detalhe,
    1 + (SELECT count(*) FROM app.contribuicao f WHERE f.principal_id = c.id)
"""
LISTAR_PARES = """
SELECT p.id, p.pontuacao, p.motivos
FROM app.par_de_contribuicoes p
WHERE p.decisao IS NULL
ORDER BY p.pontuacao DESC, p.id
LIMIT :limite
"""
LER_LADO = f"""
SELECT {LADO_DO_PAR}
FROM app.contribuicao c
JOIN ouro.dim_bairro b USING (bairro_oficial)
WHERE c.id = (SELECT {{coluna}} FROM app.par_de_contribuicoes WHERE id = :par_id)
"""
LER_PAR_ABERTO = """
SELECT primeira_id, segunda_id FROM app.par_de_contribuicoes
WHERE id = :par_id AND decisao IS NULL
FOR UPDATE
"""
FECHAR_PAR = """
UPDATE app.par_de_contribuicoes
SET decisao = :decisao, decidido_por = :usuario_id, decidido_em = :decidida_em
WHERE id = :par_id
"""
RAIZ = "SELECT coalesce(principal_id, id) FROM app.contribuicao WHERE id = :id"
SOMAR_A_PRINCIPAL = """
UPDATE app.contribuicao SET principal_id = :principal_id, resultado = 'somada'
WHERE id = :absorvida OR principal_id = :absorvida
"""
FECHAR_PARES_RESOLVIDOS = """
UPDATE app.par_de_contribuicoes p
SET decisao = 'mesma', decidido_por = :usuario_id, decidido_em = :decidida_em
FROM app.contribuicao a, app.contribuicao b
WHERE p.decisao IS NULL AND a.id = p.primeira_id AND b.id = p.segunda_id
    AND coalesce(a.principal_id, a.id) = coalesce(b.principal_id, b.id)
"""
PRONTAS = f"""
{COM_SITUACAO}
SELECT
    s.id, s.data_relato, s.categoria, s.servico_codigo, s.servico, s.bairro_oficial, s.id_local,
    s.numero_informado,
    1 + (SELECT count(*) FROM app.contribuicao f WHERE f.principal_id = s.id)
FROM situacoes s
WHERE s.situacao = 'aberta'
ORDER BY s.recebida_em
"""
RELATOS_GUARDADOS = f"""
{COM_SITUACAO}
SELECT
    s.id, s.data_relato, s.bairro_oficial, s.categoria, s.servico_codigo, s.logradouro, s.numero,
    s.id_local, s.numero_informado, b.nome
FROM situacoes s
JOIN ouro.dim_bairro b USING (bairro_oficial)
WHERE s.situacao IN ('aberta', 'em_pacote', 'na_base')
"""
MESMO_LOCAL = """
SELECT fonte, id_local, categoria, servico_codigo, bairro_oficial, data_abertura,
    coalesce(numero_informado, false)
FROM ouro.fato_demanda
WHERE id_local = ANY(:locais) AND fonte <> :formulario AND data_abertura IS NOT NULL
"""
OCORRENCIAS_DA_CIDADE = f"""
{COM_SITUACAO}
SELECT
    s.id, s.data_relato, s.servico_codigo, s.servico, s.bairro_oficial, b.nome, b.rpa,
    l.logradouro, s.numero,
    1 + (SELECT count(*) FROM app.contribuicao f WHERE f.principal_id = s.id),
    (s.retorno = 'registrou_sem_retorno')::int + (
        SELECT count(*) FROM app.contribuicao f
        WHERE f.principal_id = s.id AND f.retorno = 'registrou_sem_retorno'
    ),
    s.situacao,
    EXISTS (
        SELECT 1 FROM app.par_de_contribuicoes p
        WHERE p.decisao IS NULL AND s.id IN (p.primeira_id, p.segunda_id)
    )
FROM situacoes s
JOIN ouro.dim_bairro b USING (bairro_oficial)
LEFT JOIN ouro.dim_logradouro l
    ON l.bairro_oficial = s.bairro_oficial AND l.logradouro = s.logradouro
WHERE s.principal_id IS NULL AND s.data_relato >= :desde
    AND (CAST(:bairro AS text) IS NULL OR s.bairro_oficial = :bairro)
    AND (cardinality(CAST(:categorias AS text[])) = 0 OR s.categoria = ANY(:categorias))
ORDER BY s.data_relato DESC, s.recebida_em DESC
LIMIT :limite
"""
LIMITE_DA_VISAO_DA_CIDADE = 300
# A situação de um relato somado é a da ocorrência que o recebeu.
RELATOS_DO_CIDADAO = f"""
{COM_SITUACAO}
SELECT
    meu.id, meu.recebida_em, meu.servico_codigo, meu.servico, b.nome,
    meu.logradouro, meu.numero, meu.detalhe, meu.expurgada_em IS NOT NULL,
    meu.principal_id IS NOT NULL,
    1 + (SELECT count(*) FROM app.contribuicao f WHERE f.principal_id = ocorrencia.id),
    ocorrencia.situacao,
    EXISTS (
        SELECT 1 FROM app.par_de_contribuicoes p
        WHERE p.decisao IS NULL AND ocorrencia.id IN (p.primeira_id, p.segunda_id)
    ),
    ocorrencia.id
FROM situacoes meu
JOIN situacoes ocorrencia ON ocorrencia.id = coalesce(meu.principal_id, meu.id)
JOIN ouro.dim_bairro b ON b.bairro_oficial = meu.bairro_oficial
WHERE meu.usuario_id = :usuario
ORDER BY meu.recebida_em DESC
LIMIT :limite
"""
LIMITE_DOS_RELATOS_DO_CIDADAO = 200
EXPURGAR = """
UPDATE app.contribuicao
SET logradouro = NULL, numero = NULL, detalhe = NULL, expurgada_em = :agora
WHERE recebida_em < :limite AND expurgada_em IS NULL
"""


def _contribuicao(linha: Row[Any]) -> Contribuicao:
    dados = dict(linha._mapping)
    dados["retorno"] = RetornoAnterior(dados["retorno"])
    dados["resultado"] = ResultadoDoEnvio(dados["resultado"])
    return Contribuicao(**dados)


def _rotulo_do_servico(codigo: str, nome: str) -> str:
    servico = SERVICOS_POR_CODIGO.get(codigo)
    return servico.rotulo if servico else nome


def _lado(linha: Sequence[Any]) -> LadoDoPar:
    id_, recebida_em, codigo, nome, bairro, logradouro, numero, detalhe, relatos = linha
    return LadoDoPar(
        id_,
        recebida_em,
        _rotulo_do_servico(codigo, nome),
        bairro,
        logradouro,
        numero,
        detalhe,
        relatos,
    )


def _ocorrencia(linha: Sequence[Any]) -> OcorrenciaDoPainel:
    id_, recebida_em, codigo, nome, bairro, logradouro, numero, relatos, sem_retorno, situacao = (
        linha
    )
    return OcorrenciaDoPainel(
        id_,
        recebida_em,
        _rotulo_do_servico(codigo, nome),
        bairro,
        logradouro,
        numero,
        relatos,
        sem_retorno,
        situacao,
    )


def _relato_guardado(linha: Sequence[Any]) -> RelatoGuardado:
    id_, data, bairro, categoria, codigo, logradouro, numero, id_local, informado, nome = linha
    relato = Relato(
        data=data,
        bairro=bairro,
        categoria=categoria,
        servico_codigo=codigo,
        logradouro=logradouro,
        numero=numero,
        id_local=id_local,
        numero_informado=informado,
    )
    rotulo = f"{_rotulo_do_servico(codigo, categoria)}, {nome}, relato de {data:%d/%m/%Y}"
    return RelatoGuardado(id_, relato, rotulo)


class ContribuicaoRepositorySql:
    """Cada método abre a própria transação: quem chama pode ser a API ou a fila de importação."""

    def __init__(self, fabrica: sessionmaker[Session]) -> None:
        self._fabrica = fabrica

    def buscar_por_chave_de_envio(self, chave: str) -> Contribuicao | None:
        consulta = f"SELECT {COLUNAS} FROM app.contribuicao WHERE chave_de_envio = :chave"
        with self._fabrica() as sessao:
            linha = sessao.execute(text(consulta), {"chave": chave}).first()
        return _contribuicao(linha) if linha else None

    def candidatas(self, bairro: str, categoria: str, desde: date) -> list[Contribuicao]:
        consulta = f"""
        SELECT {COLUNAS} FROM app.contribuicao
        WHERE bairro_oficial = :bairro AND categoria = :categoria AND data_relato >= :desde
            AND principal_id IS NULL
        """
        parametros = {"bairro": bairro, "categoria": categoria, "desde": desde}
        with self._fabrica() as sessao:
            return [_contribuicao(linha) for linha in sessao.execute(text(consulta), parametros)]

    def inserir(self, contribuicao: Contribuicao, pares: Sequence[ParNovo]) -> Contribuicao:
        dados = {
            **asdict(contribuicao),
            "retorno": contribuicao.retorno.value,
            "resultado": contribuicao.resultado.value,
        }
        with self._fabrica.begin() as sessao:
            inseridas = sessao.execute(text(INSERIR), dados).rowcount  # type: ignore[attr-defined]
            if inseridas:
                self._inserir_pares(sessao, contribuicao.id, pares)
        if inseridas:
            return contribuicao
        guardada = self.buscar_por_chave_de_envio(contribuicao.chave_de_envio)
        return guardada or contribuicao

    @staticmethod
    def _inserir_pares(sessao: Session, nova_id: UUID, pares: Sequence[ParNovo]) -> None:
        consulta = text(INSERIR_PAR).bindparams(bindparam("motivos", type_=JSONB))
        for par in pares:
            sessao.execute(
                consulta,
                {
                    "primeira_id": par.contribuicao_id,
                    "segunda_id": nova_id,
                    "pontuacao": par.comparacao.pontuacao,
                    "motivos": list(par.comparacao.motivos),
                },
            )

    def resumir(self) -> ResumoDasContribuicoes:
        with self._fabrica() as sessao:
            return ResumoDasContribuicoes(*sessao.execute(text(RESUMIR)).one())

    def listar_ocorrencias(self, limite: int, deslocamento: int) -> PaginaDeOcorrencias:
        parametros = {"limite": limite, "deslocamento": deslocamento}
        with self._fabrica() as sessao:
            linhas = sessao.execute(text(LISTAR_OCORRENCIAS), parametros).all()
            total = sessao.scalar(text(CONTAR_OCORRENCIAS)) or 0
        return PaginaDeOcorrencias([_ocorrencia(linha) for linha in linhas], total)

    def listar_pares_abertos(self, limite: int) -> list[ParParaRevisar]:
        with self._fabrica() as sessao:
            pares = sessao.execute(text(LISTAR_PARES), {"limite": limite}).all()
            return [
                ParParaRevisar(
                    par_id,
                    pontuacao,
                    motivos,
                    self._ler_lado(sessao, par_id, "primeira_id"),
                    self._ler_lado(sessao, par_id, "segunda_id"),
                )
                for par_id, pontuacao, motivos in pares
            ]

    @staticmethod
    def _ler_lado(sessao: Session, par_id: int, coluna: str) -> LadoDoPar:
        consulta = LER_LADO.format(coluna=coluna)
        return _lado(sessao.execute(text(consulta), {"par_id": par_id}).one())

    def decidir_par(self, par_id: int, decisao: DecisaoRegistrada) -> bool:
        with self._fabrica.begin() as sessao:
            par = sessao.execute(text(LER_PAR_ABERTO), {"par_id": par_id}).first()
            if par is None:
                return False
            if decisao.decisao is DecisaoDoPar.MESMA:
                self._somar(sessao, par.primeira_id, par.segunda_id)
            parametros = {
                "par_id": par_id,
                "decisao": decisao.decisao.value,
                "usuario_id": decisao.usuario_id,
                "decidida_em": decisao.decidida_em,
            }
            sessao.execute(text(FECHAR_PAR), parametros)
            sessao.execute(text(FECHAR_PARES_RESOLVIDOS), parametros)
        return True

    @staticmethod
    def _somar(sessao: Session, primeira: UUID, segunda: UUID) -> None:
        principal = sessao.scalar(text(RAIZ), {"id": primeira})
        absorvida = sessao.scalar(text(RAIZ), {"id": segunda})
        if principal != absorvida:
            sessao.execute(
                text(SOMAR_A_PRINCIPAL), {"principal_id": principal, "absorvida": absorvida}
            )

    def contar_pares_abertos(self) -> int:
        consulta = "SELECT count(*) FROM app.par_de_contribuicoes WHERE decisao IS NULL"
        with self._fabrica() as sessao:
            return sessao.scalar(text(consulta)) or 0

    def prontas_para_pacote(self) -> list[OcorrenciaDoPacote]:
        with self._fabrica() as sessao:
            return [OcorrenciaDoPacote(*linha) for linha in sessao.execute(text(PRONTAS))]

    def marcar_no_pacote(self, ids: Sequence[UUID], importacao_id: int) -> None:
        consulta = "UPDATE app.contribuicao SET importacao_id = :pacote WHERE id = ANY(:ids)"
        with self._fabrica.begin() as sessao:
            sessao.execute(text(consulta), {"pacote": importacao_id, "ids": list(ids)})

    def expurgar_enderecos(self, recebidas_ate: datetime, agora: datetime) -> int:
        with self._fabrica.begin() as sessao:
            resultado = sessao.execute(text(EXPURGAR), {"limite": recebidas_ate, "agora": agora})
        return int(resultado.rowcount)  # type: ignore[attr-defined]

    def ocorrencias_da_cidade(self, filtro: FiltroDaCidade) -> list[OcorrenciaDaCidade]:
        parametros = {
            "desde": filtro.desde,
            "bairro": filtro.bairro,
            "categorias": list(filtro.categorias),
            "limite": LIMITE_DA_VISAO_DA_CIDADE,
        }
        with self._fabrica() as sessao:
            linhas = sessao.execute(text(OCORRENCIAS_DA_CIDADE), parametros)
            return [OcorrenciaDaCidade(*linha) for linha in linhas]

    def relatos_do_cidadao(self, usuario_id: UUID) -> list[RelatoDoCidadao]:
        parametros = {"usuario": usuario_id, "limite": LIMITE_DOS_RELATOS_DO_CIDADAO}
        with self._fabrica() as sessao:
            linhas = sessao.execute(text(RELATOS_DO_CIDADAO), parametros)
            return [RelatoDoCidadao(*linha) for linha in linhas]

    def relatos_guardados(self) -> list[RelatoGuardado]:
        with self._fabrica() as sessao:
            return [_relato_guardado(linha) for linha in sessao.execute(text(RELATOS_GUARDADOS))]

    def ids_do_pacote(self, importacao_id: int) -> list[UUID]:
        consulta = "SELECT id FROM app.contribuicao WHERE importacao_id = :pacote"
        with self._fabrica() as sessao:
            return list(sessao.scalars(text(consulta), {"pacote": importacao_id}))

    def registros_no_mesmo_local(self, ids_locais: list[str]) -> list[RegistroNoMesmoLocal]:
        parametros = {"locais": ids_locais, "formulario": Fonte.FORMULARIO.value}
        with self._fabrica() as sessao:
            linhas = sessao.execute(text(MESMO_LOCAL), parametros)
            return [RegistroNoMesmoLocal(*linha) for linha in linhas]


class ReferenciaDoFormularioSql:
    def __init__(self, fabrica: sessionmaker[Session]) -> None:
        self._fabrica = fabrica

    def bairros(self) -> list[BairroDoFormulario]:
        consulta = "SELECT bairro_oficial, nome, rpa FROM ouro.dim_bairro ORDER BY nome"
        with self._fabrica() as sessao:
            return [BairroDoFormulario(*linha) for linha in sessao.execute(text(consulta))]

    def logradouros(self, bairro: str) -> list[str]:
        consulta = """
        SELECT logradouro FROM ouro.dim_logradouro
        WHERE bairro_oficial = :bairro ORDER BY pedidos DESC, logradouro
        """
        with self._fabrica() as sessao:
            return list(sessao.scalars(text(consulta), {"bairro": bairro}))

    def somar_logradouros(self, vias: Iterable[tuple[str, str, int]]) -> int:
        consulta = """
        INSERT INTO ouro.dim_logradouro (bairro_oficial, logradouro, pedidos)
        VALUES (:bairro, :logradouro, :pedidos)
        ON CONFLICT (bairro_oficial, logradouro)
        DO UPDATE SET pedidos = ouro.dim_logradouro.pedidos + excluded.pedidos
        """
        linhas = [
            {"bairro": bairro, "logradouro": logradouro, "pedidos": pedidos}
            for bairro, logradouro, pedidos in vias
        ]
        if not linhas:
            return 0
        with self._fabrica.begin() as sessao:
            sessao.execute(text(consulta), linhas)
        return len(linhas)
