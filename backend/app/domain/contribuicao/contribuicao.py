import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.contribuicao.comparacao import Relato
from app.domain.erros import ContribuicaoInvalida
from app.domain.importacao.privacidade import motivo_pelo_conteudo

TAMANHO_MAXIMO_DA_VIA = 120
TAMANHO_MINIMO_DA_VIA = 3
TAMANHO_MAXIMO_DO_NUMERO = 10
TAMANHO_MAXIMO_DO_DETALHE = 280
DIAS_DE_GUARDA_DO_ENDERECO = 90

PADRAO_CPF_SEM_PONTUACAO = re.compile(r"(?<!\d)\d{11}(?!\d)")
PADRAO_TELEFONE_SOLTO = re.compile(r"(?<!\d)(?:\d{2}[\s.-]?)?9?\d{4}[\s.-]\d{4}(?!\d)")
AVISO_DE_DADO_PESSOAL = (
    "Parece haver CPF, telefone ou e-mail neste campo. Retire para proteger a sua privacidade."
)


class RetornoAnterior(StrEnum):
    NAO_REGISTROU = "nao_registrou"
    REGISTROU_SEM_RETORNO = "registrou_sem_retorno"
    REGISTROU_COM_RETORNO = "registrou_com_retorno"


class ResultadoDoEnvio(StrEnum):
    NOVA = "nova"
    SOMADA = "somada"
    EM_CONFERENCIA = "em_conferencia"


class DecisaoDoPar(StrEnum):
    MESMA = "mesma"
    DIFERENTE = "diferente"


@dataclass(frozen=True)
class FormularioPreenchido:
    chave_de_envio: str
    servico_codigo: str
    bairro_oficial: str
    logradouro: str
    numero: str
    detalhe: str
    retorno: RetornoAnterior


@dataclass(frozen=True)
class Contribuicao:
    id: UUID
    chave_de_envio: str
    recebida_em: datetime
    data_relato: date
    categoria: str
    servico_codigo: str
    servico: str
    bairro_oficial: str
    logradouro: str | None
    numero: str | None
    detalhe: str | None
    id_local: str | None
    numero_informado: bool
    retorno: RetornoAnterior
    resultado: ResultadoDoEnvio
    principal_id: UUID | None = None
    usuario_id: UUID | None = None

    def como_relato(self) -> Relato:
        return Relato(
            data=self.data_relato,
            bairro=self.bairro_oficial,
            categoria=self.categoria,
            servico_codigo=self.servico_codigo,
            logradouro=self.logradouro,
            numero=self.numero,
            detalhe=self.detalhe,
            id_local=self.id_local,
            numero_informado=self.numero_informado,
        )


def _tem_dado_pessoal(texto: str) -> bool:
    return (
        motivo_pelo_conteudo(texto) is not None
        or PADRAO_CPF_SEM_PONTUACAO.search(texto) is not None
        or PADRAO_TELEFONE_SOLTO.search(texto) is not None
    )


def exigir_texto_sem_dado_pessoal(campo: str, texto: str) -> None:
    if _tem_dado_pessoal(texto):
        raise ContribuicaoInvalida(campo, AVISO_DE_DADO_PESSOAL)


def exigir_tamanhos(formulario: FormularioPreenchido) -> None:
    via = formulario.logradouro.strip()
    if not TAMANHO_MINIMO_DA_VIA <= len(via) <= TAMANHO_MAXIMO_DA_VIA:
        raise ContribuicaoInvalida("logradouro", "Informe o nome da rua, com até 120 caracteres.")
    if len(formulario.numero.strip()) > TAMANHO_MAXIMO_DO_NUMERO:
        raise ContribuicaoInvalida("numero", "Informe só o número do imóvel mais próximo.")
    if len(formulario.detalhe.strip()) > TAMANHO_MAXIMO_DO_DETALHE:
        raise ContribuicaoInvalida("detalhe", "Use até 280 caracteres.")
