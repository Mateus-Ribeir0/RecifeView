from collections.abc import Sequence
from dataclasses import replace
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.orm import Session

from app.application.portas.encaminhamentos import (
    FiltroDeEncaminhamentos,
    MudancaDeSituacao,
    NovoEncaminhamento,
    PaginaDeEncaminhamentos,
    PendenciasDosEncaminhamentos,
    ResumoDosEncaminhamentos,
    TokenDeRetorno,
)
from app.domain.encaminhamento.encaminhamento import (
    SITUACOES_ABERTAS,
    AutorDoEvento,
    CanalDeEnvio,
    Encaminhamento,
    EventoDoEncaminhamento,
    OcorrenciaEncaminhavel,
    SituacaoDoEncaminhamento,
    descrever_local_aproximado,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.encaminhamento.sugestao import CitacoesDoTema

COLUNAS = """
    e.id, e.chave_registro, e.fonte, e.data_abertura, e.categoria, e.servico, e.bairro_oficial,
    e.rpa, e.situacao_na_fonte, e.orgao_na_fonte, e.protocolo_de_origem, e.orgao,
    e.orgao_sugerido, e.canal, e.situacao, e.criado_em, e.prazo_de_resposta, e.atualizado_em,
    e.nota, e.justificativa, e.automatico, e.protocolo_do_orgao, e.contribuicao_id,
    e.referencia_de_local, e.lembrete_enviado_em
"""
OCORRENCIA = """
SELECT
    chave_registro, fonte, data_abertura, categoria, servico, bairro_oficial, rpa, situacao,
    orgao, protocolo
FROM ouro.fato_demanda
WHERE chave_registro = :chave
"""
CITACOES_DO_TEMA = """
SELECT orgao, count(*)::int FROM ouro.mv_camara_indicacoes WHERE categoria = :tema GROUP BY orgao
"""
INSERIR = """
INSERT INTO app.encaminhamento (
    chave_registro, fonte, data_abertura, categoria, servico, bairro_oficial, rpa,
    situacao_na_fonte, orgao_na_fonte, protocolo_de_origem, nota, orgao, orgao_sugerido, canal,
    situacao, justificativa, automatico, criado_por, criado_em, prazo_de_resposta, hash_do_token,
    token_expira_em, atualizado_em, contribuicao_id, referencia_de_local
) VALUES (
    :chave_registro, :fonte, :data_abertura, :categoria, :servico, :bairro_oficial, :rpa,
    :situacao_na_fonte, :orgao_na_fonte, :protocolo_de_origem, :nota, :orgao, :orgao_sugerido,
    :canal, :situacao, :justificativa, :automatico, :criado_por, :criado_em, :prazo_de_resposta,
    :hash_do_token, :token_expira_em, :criado_em, :contribuicao_id, :referencia_de_local
)
RETURNING id
"""
INSERIR_EVENTO = """
INSERT INTO app.evento_de_encaminhamento (
    encaminhamento_id, situacao, autor, usuario_id, ocorrido_em, observacao, protocolo_do_orgao
) VALUES (
    :encaminhamento_id, :situacao, :autor, :usuario_id, :ocorrido_em, :observacao,
    :protocolo_do_orgao
)
"""
MUDAR_SITUACAO = """
UPDATE app.encaminhamento
SET situacao = :situacao,
    protocolo_do_orgao = coalesce(:protocolo_do_orgao, protocolo_do_orgao),
    atualizado_em = :ocorrido_em
WHERE id = :encaminhamento_id
"""
PREPARAR_REENVIO = """
UPDATE app.encaminhamento
SET hash_do_token = :hash_do_token, token_expira_em = :token_expira_em, canal = :canal
WHERE id = :encaminhamento_id
"""
EVENTOS = """
SELECT encaminhamento_id, situacao, autor, ocorrido_em, observacao, protocolo_do_orgao
FROM app.evento_de_encaminhamento
WHERE encaminhamento_id = ANY(:ids)
ORDER BY ocorrido_em, id
"""
ULTIMOS_POR_CHAVE = f"""
SELECT DISTINCT ON (e.chave_registro) {COLUNAS}
FROM app.encaminhamento e
WHERE e.chave_registro = ANY(:chaves)
ORDER BY e.chave_registro, e.criado_em DESC
"""
CONTAGEM_POR_SITUACAO = "SELECT situacao, count(*)::int FROM app.encaminhamento GROUP BY situacao"
ATRASADOS = """
SELECT count(*)::int FROM app.encaminhamento
WHERE situacao = ANY(:abertas) AND prazo_de_resposta < :hoje
"""
MEDIANA_ATE_RESOLVER = """
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY ev.ocorrido_em::date - e.criado_em::date)
FROM app.encaminhamento e
JOIN app.evento_de_encaminhamento ev ON ev.encaminhamento_id = e.id
WHERE ev.situacao = 'resolvido'
"""
POR_ID = f"SELECT {COLUNAS} FROM app.encaminhamento e WHERE e.id = :id"
ULTIMO_DE_CADA_OCORRENCIA = """
SELECT DISTINCT ON (chave_registro) id, situacao, prazo_de_resposta
FROM app.encaminhamento
ORDER BY chave_registro, criado_em DESC, id DESC
"""
PEDEM_ACAO = f"""
SELECT id FROM ({ULTIMO_DE_CADA_OCORRENCIA}) u
WHERE u.situacao IN ('devolvido', 'falhou')
    OR (u.situacao = ANY(:abertas) AND u.prazo_de_resposta < :hoje)
"""
PENDENCIAS = f"""
SELECT
    count(*) FILTER (WHERE situacao = 'devolvido')::int,
    count(*) FILTER (WHERE situacao = 'falhou')::int,
    count(*) FILTER (WHERE situacao = ANY(:abertas) AND prazo_de_resposta < :hoje)::int
FROM ({ULTIMO_DE_CADA_OCORRENCIA}) u
"""
LOCAL_DO_RELATO = """
SELECT l.logradouro, c.numero
FROM app.contribuicao c
LEFT JOIN ouro.dim_logradouro l
    ON l.bairro_oficial = c.bairro_oficial AND l.logradouro = c.logradouro
WHERE c.id = :id
"""
VENCIDOS_SEM_LEMBRETE = f"""
SELECT {COLUNAS} FROM app.encaminhamento e
WHERE e.situacao = ANY(:abertas) AND e.prazo_de_resposta < :hoje AND e.lembrete_enviado_em IS NULL
ORDER BY e.prazo_de_resposta, e.id
"""
REGISTRAR_LEMBRETE = """
UPDATE app.encaminhamento
SET hash_do_token = :hash_do_token, token_expira_em = :token_expira_em,
    lembrete_enviado_em = :agora
WHERE id = :encaminhamento_id
"""
ULTIMOS_POR_RELATO = f"""
SELECT DISTINCT ON (e.contribuicao_id) {COLUNAS}
FROM app.encaminhamento e
WHERE e.contribuicao_id = ANY(:ids)
ORDER BY e.contribuicao_id, e.criado_em DESC, e.id DESC
"""
ABERTAS = [situacao.value for situacao in SITUACOES_ABERTAS]


def _orgao_ou_nada(valor: str | None) -> Orgao | None:
    return Orgao(valor) if valor else None


def _encaminhamento(linha: Row[Any]) -> Encaminhamento:
    dados = linha._mapping
    return Encaminhamento(
        id=dados["id"],
        ocorrencia=OcorrenciaEncaminhavel(
            chave_registro=dados["chave_registro"],
            fonte=dados["fonte"],
            data_abertura=dados["data_abertura"],
            categoria=dados["categoria"],
            servico=dados["servico"],
            bairro_oficial=dados["bairro_oficial"],
            rpa=dados["rpa"],
            situacao=dados["situacao_na_fonte"],
            orgao=dados["orgao_na_fonte"],
            protocolo=dados["protocolo_de_origem"],
            referencia_de_local=dados["referencia_de_local"],
        ),
        orgao=Orgao(dados["orgao"]),
        orgao_sugerido=_orgao_ou_nada(dados["orgao_sugerido"]),
        canal=CanalDeEnvio(dados["canal"]),
        situacao=SituacaoDoEncaminhamento(dados["situacao"]),
        criado_em=dados["criado_em"],
        prazo_de_resposta=dados["prazo_de_resposta"],
        atualizado_em=dados["atualizado_em"],
        nota=dados["nota"],
        justificativa=dados["justificativa"],
        automatico=dados["automatico"],
        protocolo_do_orgao=dados["protocolo_do_orgao"],
        contribuicao_id=dados["contribuicao_id"],
        lembrete_enviado_em=dados["lembrete_enviado_em"],
    )


def _parametros_do_novo(novo: NovoEncaminhamento) -> dict[str, object]:
    ocorrencia = novo.ocorrencia
    return {
        "chave_registro": ocorrencia.chave_registro,
        "fonte": ocorrencia.fonte,
        "data_abertura": ocorrencia.data_abertura,
        "categoria": ocorrencia.categoria,
        "servico": ocorrencia.servico,
        "bairro_oficial": ocorrencia.bairro_oficial,
        "rpa": ocorrencia.rpa,
        "situacao_na_fonte": ocorrencia.situacao,
        "orgao_na_fonte": ocorrencia.orgao,
        "protocolo_de_origem": ocorrencia.protocolo,
        "nota": novo.nota,
        "orgao": novo.orgao.value,
        "orgao_sugerido": novo.orgao_sugerido.value if novo.orgao_sugerido else None,
        "canal": novo.canal.value,
        "situacao": SituacaoDoEncaminhamento.ENVIADO.value,
        "justificativa": novo.justificativa,
        "automatico": novo.automatico,
        "criado_por": novo.criado_por,
        "criado_em": novo.criado_em,
        "prazo_de_resposta": novo.prazo_de_resposta,
        "hash_do_token": novo.token.hash,
        "token_expira_em": novo.token.expira_em,
        "contribuicao_id": novo.contribuicao_id,
        "referencia_de_local": ocorrencia.referencia_de_local,
    }


def _onde(filtro: FiltroDeEncaminhamentos, hoje: date) -> tuple[str, dict[str, object]]:
    condicoes: list[str] = []
    parametros: dict[str, object] = {"hoje": hoje, "abertas": ABERTAS}
    if filtro.situacao is not None:
        condicoes.append("e.situacao = :situacao")
        parametros["situacao"] = filtro.situacao.value
    if filtro.orgao is not None:
        condicoes.append("e.orgao = :orgao")
        parametros["orgao"] = filtro.orgao.value
    if filtro.so_atrasados:
        condicoes.append("e.situacao = ANY(:abertas) AND e.prazo_de_resposta < :hoje")
    if filtro.so_os_que_pedem_acao:
        condicoes.append(f"e.id IN ({PEDEM_ACAO})")
    onde = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    return onde, parametros


class EncaminhamentoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def ocorrencia(self, chave_registro: int) -> OcorrenciaEncaminhavel | None:
        linha = self._sessao.execute(text(OCORRENCIA), {"chave": chave_registro}).first()
        return OcorrenciaEncaminhavel(*linha) if linha else None

    def citacoes_do_tema(self, tema: str) -> CitacoesDoTema:
        linhas = self._sessao.execute(text(CITACOES_DO_TEMA), {"tema": tema}).all()
        por_nome = {orgao: indicacoes for orgao, indicacoes in linhas if orgao}
        return CitacoesDoTema(tema, sum(indicacoes for _, indicacoes in linhas), por_nome)

    def da_ocorrencia(self, chave_registro: int) -> list[Encaminhamento]:
        consulta = f"""
        SELECT {COLUNAS} FROM app.encaminhamento e
        WHERE e.chave_registro = :chave ORDER BY e.criado_em DESC
        """
        linhas = self._sessao.execute(text(consulta), {"chave": chave_registro})
        return self._com_eventos([_encaminhamento(linha) for linha in linhas])

    def criar(self, novo: NovoEncaminhamento) -> Encaminhamento:
        parametros = _parametros_do_novo(novo)
        encaminhamento_id = self._sessao.execute(text(INSERIR), parametros).scalar_one()
        autor = AutorDoEvento.SISTEMA if novo.automatico else AutorDoEvento.GESTAO
        envio = MudancaDeSituacao(
            SituacaoDoEncaminhamento.ENVIADO, autor, novo.criado_em, novo.criado_por
        )
        self._inserir_evento(encaminhamento_id, envio)
        linha = self._sessao.execute(text(POR_ID), {"id": encaminhamento_id}).one()
        return self._com_eventos([_encaminhamento(linha)])[0]

    def buscar(self, encaminhamento_id: int) -> Encaminhamento | None:
        linha = self._sessao.execute(text(POR_ID), {"id": encaminhamento_id}).first()
        return self._com_eventos([_encaminhamento(linha)])[0] if linha else None

    def buscar_pelo_token(self, hash_do_token: str, agora: datetime) -> Encaminhamento | None:
        consulta = f"""
        SELECT {COLUNAS} FROM app.encaminhamento e
        WHERE e.hash_do_token = :hash AND e.token_expira_em > :agora
        """
        parametros = {"hash": hash_do_token, "agora": agora}
        linha = self._sessao.execute(text(consulta), parametros).first()
        return self._com_eventos([_encaminhamento(linha)])[0] if linha else None

    def mudar_situacao(self, encaminhamento_id: int, mudanca: MudancaDeSituacao) -> None:
        parametros = {
            "encaminhamento_id": encaminhamento_id,
            "situacao": mudanca.situacao.value,
            "protocolo_do_orgao": mudanca.protocolo_do_orgao,
            "ocorrido_em": mudanca.ocorrido_em,
        }
        self._sessao.execute(text(MUDAR_SITUACAO), parametros)
        self._inserir_evento(encaminhamento_id, mudanca)

    def preparar_reenvio(
        self, encaminhamento_id: int, token: TokenDeRetorno, canal: CanalDeEnvio
    ) -> None:
        parametros = {
            "encaminhamento_id": encaminhamento_id,
            "hash_do_token": token.hash,
            "token_expira_em": token.expira_em,
            "canal": canal.value,
        }
        self._sessao.execute(text(PREPARAR_REENVIO), parametros)

    def listar(self, filtro: FiltroDeEncaminhamentos, hoje: date) -> PaginaDeEncaminhamentos:
        onde, parametros = _onde(filtro, hoje)
        consulta = f"""
        SELECT {COLUNAS}, count(*) OVER () AS total
        FROM app.encaminhamento e
        {onde}
        ORDER BY e.criado_em DESC, e.id DESC
        LIMIT :limite OFFSET :deslocamento
        """
        parametros |= {"limite": filtro.limite, "deslocamento": filtro.deslocamento}
        linhas = self._sessao.execute(text(consulta), parametros).all()
        total = linhas[0]._mapping["total"] if linhas else 0
        return PaginaDeEncaminhamentos([_encaminhamento(linha) for linha in linhas], total)

    def resumir(self, hoje: date) -> ResumoDosEncaminhamentos:
        contagem = {
            SituacaoDoEncaminhamento(situacao): quantidade
            for situacao, quantidade in self._sessao.execute(text(CONTAGEM_POR_SITUACAO))
        }
        parametros = {"abertas": ABERTAS, "hoje": hoje}
        atrasados = self._sessao.execute(text(ATRASADOS), parametros).scalar() or 0
        mediana = self._sessao.execute(text(MEDIANA_ATE_RESOLVER)).scalar()
        return ResumoDosEncaminhamentos(
            total=sum(contagem.values()),
            abertos=sum(contagem.get(situacao, 0) for situacao in SITUACOES_ABERTAS),
            atrasados=atrasados,
            por_situacao=contagem,
            mediana_de_dias_ate_resolver=float(mediana) if mediana is not None else None,
        )

    def contar_pendencias(self, hoje: date) -> PendenciasDosEncaminhamentos:
        parametros = {"abertas": ABERTAS, "hoje": hoje}
        devolvidos, falhas, vencidos = self._sessao.execute(text(PENDENCIAS), parametros).one()
        return PendenciasDosEncaminhamentos(devolvidos, falhas, vencidos)

    def local_aproximado_do_relato(self, contribuicao_id: UUID) -> str | None:
        linha = self._sessao.execute(text(LOCAL_DO_RELATO), {"id": contribuicao_id}).first()
        return descrever_local_aproximado(*linha) if linha else None

    def vencidos_sem_lembrete(self, hoje: date) -> list[Encaminhamento]:
        parametros = {"abertas": ABERTAS, "hoje": hoje}
        linhas = self._sessao.execute(text(VENCIDOS_SEM_LEMBRETE), parametros)
        return [_encaminhamento(linha) for linha in linhas]

    def registrar_lembrete(
        self, encaminhamento_id: int, token: TokenDeRetorno, agora: datetime
    ) -> None:
        parametros = {
            "encaminhamento_id": encaminhamento_id,
            "hash_do_token": token.hash,
            "token_expira_em": token.expira_em,
            "agora": agora,
        }
        self._sessao.execute(text(REGISTRAR_LEMBRETE), parametros)

    def ultimos_por_relato(self, ids: Sequence[UUID]) -> dict[UUID, Encaminhamento]:
        if not ids:
            return {}
        linhas = self._sessao.execute(text(ULTIMOS_POR_RELATO), {"ids": list(ids)})
        encaminhamentos = self._com_eventos([_encaminhamento(linha) for linha in linhas])
        return {item.contribuicao_id: item for item in encaminhamentos if item.contribuicao_id}

    def ultimos_por_chave(self, chaves: Sequence[int]) -> dict[int, Encaminhamento]:
        linhas = self._sessao.execute(text(ULTIMOS_POR_CHAVE), {"chaves": list(chaves)})
        return {
            encaminhamento.ocorrencia.chave_registro: encaminhamento
            for encaminhamento in map(_encaminhamento, linhas)
        }

    def _inserir_evento(self, encaminhamento_id: int, mudanca: MudancaDeSituacao) -> None:
        parametros = {
            "encaminhamento_id": encaminhamento_id,
            "situacao": mudanca.situacao.value,
            "autor": mudanca.autor.value,
            "usuario_id": mudanca.usuario_id,
            "ocorrido_em": mudanca.ocorrido_em,
            "observacao": mudanca.observacao,
            "protocolo_do_orgao": mudanca.protocolo_do_orgao,
        }
        self._sessao.execute(text(INSERIR_EVENTO), parametros)

    def _com_eventos(self, encaminhamentos: list[Encaminhamento]) -> list[Encaminhamento]:
        if not encaminhamentos:
            return []
        ids = [encaminhamento.id for encaminhamento in encaminhamentos]
        eventos: dict[int, list[EventoDoEncaminhamento]] = {}
        for linha in self._sessao.execute(text(EVENTOS), {"ids": ids}):
            encaminhamento_id, situacao, autor, ocorrido_em, observacao, protocolo = linha
            eventos.setdefault(encaminhamento_id, []).append(
                EventoDoEncaminhamento(
                    SituacaoDoEncaminhamento(situacao),
                    AutorDoEvento(autor),
                    ocorrido_em,
                    observacao,
                    protocolo,
                )
            )
        return [
            replace(encaminhamento, eventos=tuple(eventos.get(encaminhamento.id, [])))
            for encaminhamento in encaminhamentos
        ]
