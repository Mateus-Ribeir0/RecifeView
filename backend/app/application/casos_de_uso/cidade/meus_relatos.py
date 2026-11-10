from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.casos_de_uso.cidade.ocorrencias import TEMA_POR_SERVICO
from app.application.portas.contribuicoes import ContribuicaoRepository, RelatoDoCidadao
from app.domain.cidade import SituacaoPublica, situacao_publica
from app.domain.contribuicao.catalogo import SERVICOS_POR_CODIGO
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class MeuRelato:
    id: UUID
    recebido_em: datetime
    servico: str
    tema: str
    bairro: str
    endereco: str | None
    detalhe: str | None
    endereco_apagado: bool
    somado: bool
    relatos: int
    situacao: SituacaoPublica


def _endereco(linha: RelatoDoCidadao) -> str | None:
    if linha.logradouro is None:
        return None
    return f"{linha.logradouro}, {linha.numero}" if linha.numero else linha.logradouro


def _acompanhar(linha: RelatoDoCidadao) -> MeuRelato:
    servico = SERVICOS_POR_CODIGO.get(linha.servico_codigo)
    tema = TEMA_POR_SERVICO.get(linha.servico_codigo)
    return MeuRelato(
        id=linha.id,
        recebido_em=linha.recebida_em,
        servico=servico.rotulo if servico else linha.servico,
        tema=tema.rotulo if tema else "Outros",
        bairro=linha.bairro,
        endereco=_endereco(linha),
        detalhe=linha.detalhe,
        endereco_apagado=linha.endereco_apagado,
        somado=linha.somado,
        relatos=linha.relatos,
        situacao=situacao_publica(linha.situacao, linha.tem_dupla_aberta),
    )


@dataclass(frozen=True)
class ListarMeusRelatos:
    """Só quem enviou vê o próprio relato com endereço; a gestão não sabe quem relatou."""

    contribuicoes: ContribuicaoRepository

    def executar(self, cidadao: Usuario) -> list[MeuRelato]:
        return [_acompanhar(linha) for linha in self.contribuicoes.relatos_do_cidadao(cidadao.id)]
